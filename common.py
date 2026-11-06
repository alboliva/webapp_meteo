"""
common.py — dati condivisi tra le pagine: stazioni, zone, webcam, fetch meteo,


FORMATO dashboard.txt (una webcam per riga):
    chiave = URL_immagine
    chiave = URL_immagine | Centro, Monti        ← zone esplicite (anche più di una)

  • Se la chiave corrisponde a una stazione (es. monte_cavo) la webcam prende
    nome e temperatura della stazione; senza zone esplicite va nella zona
    della stazione.
  • Una chiave che NON è una stazione viene comunque mostrata (senza temperatura),
    con nome ricavato dalla chiave; senza zone esplicite finisce in "Centro".
  • La stessa webcam può comparire in più sezioni: basta elencarle dopo "|".
    Lo storico degli scatti è unico per webcam (legato alla chiave), quindi è
    lo stesso in tutte le sezioni in cui compare.
"""

import base64
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo

import requests
import streamlit as st

# ─── STAZIONI ────────────────────────────────────────────────────────────────
STAZIONI = [
    (41.8967, 12.4822, "Roma Centro",           "roma_centro",           "Roma",   "b-roma",   "Europe/Rome"),
    (41.9147, 12.4178, "Roma Pineta Sacchetti", "roma_pineta_sacchetti", "Roma",   "b-roma",   "Europe/Rome"),
    (41.9183, 12.4347, "Roma Monte Mario",      "roma_monte_mario",      "Roma",   "b-roma",   "Europe/Rome"),
    (41.8836, 12.4694, "Roma Gianicolo",        "roma_gianicolo",        "Roma",   "b-roma",   "Europe/Rome"),
    (41.9736, 12.0631, "Marina di San Nicola",  "marina_san_nicola",     "Mare",   "b-mare",   "Europe/Rome"),
    (42.7500, 10.3830, "Capoliveri",            "capoliveri",            "Mare",   "b-mare",   "Europe/Rome"),
    (42.7425, 10.2332, "Marina di Campo",       "marina_di_campo",       "Mare",   "b-mare",   "Europe/Rome"),
    (42.1089, 12.1667, "Bracciano",             "bracciano",             "Lago",   "b-lago",   "Europe/Rome"),
    (42.1608, 12.2458, "Trevignano Romano",     "trevignano_romano",     "Lago",   "b-lago",   "Europe/Rome"),
    (41.7700, 12.7200, "Monte Cavo",            "monte_cavo",            "Monti",  "b-monti",  "Europe/Rome"),
    (42.5539, 13.5367, "Fano Adriano",          "fano_adriano",          "Monti",  "b-monti",  "Europe/Rome"),
    (41.8561, 13.7950, "Pescasseroli",          "pescasseroli",          "Monti",  "b-monti",  "Europe/Rome"),
    (42.4996, 13.5597, "Prati di Tivo",         "prati_di_tivo",         "Monti",  "b-monti",  "Europe/Rome"),
    (42.5233, 13.5540, "Pietracamela",          "pietracamela",          "Monti",  "b-monti",  "Europe/Rome"),
    (41.8750, 13.0333, "Monte Livata",          "monte_livata",          "Monti",  "b-monti",  "Europe/Rome"),
    (42.2333, 13.5667, "Campo Imperatore",      "campo_imperatore",      "Monti",  "b-monti",  "Europe/Rome"),
    (41.9917, 14.1017, "Campo di Giove",        "campo_di_giove",        "Monti",  "b-monti",  "Europe/Rome"),
    (41.8500, 14.0667, "Roccaraso",             "roccaraso",             "Monti",  "b-monti",  "Europe/Rome"),
    (41.7833, 13.8167, "Forca d'Acero",         "forca_dacero",          "Monti",  "b-monti",  "Europe/Rome"),
    (41.8375, 13.9304, "Passo Godi",            "passo_godi",            "Monti",  "b-monti",  "Europe/Rome"),
    (42.477064175108076, 13.565367956920705, "Rifugio Franchetti", "rifugio_franchetti", "Monti", "b-monti", "Europe/Rome"),
    (42.49976459287265,  13.55813093025115,  "Prati di Tivo 2",    "prati_di_tivo_2",    "Monti", "b-monti", "Europe/Rome"),
    (42.496257,          13.561939,          "Prati di Tivo 3",    "prati_di_tivo_3",    "Monti", "b-monti", "Europe/Rome"),
    (42.48676792416478,  13.56747688527417,  "La Madonnina",       "la_madonnina",       "Monti", "b-monti", "Europe/Rome"),
    (45.9383,  7.6267, "Breuil-Cervinia",       "breuil_cervinia",       "Nord",   "b-nord",   "Europe/Rome"),
    (45.9417,  7.6556, "Plan Maison",           "plan_maison",           "Nord",   "b-nord",   "Europe/Rome"),
    (45.9349,  7.7073, "Plateau Rosà",          "plateau_rosa",          "Nord",   "b-nord",   "Europe/Rome"),
    (45.9271,  7.8771, "Capanna Margherita",    "capanna_margherita",    "Nord",   "b-nord",   "Europe/Rome"),
    (45.8955,  7.8479, "Rifugio Mantova",       "rifugio_mantova",       "Nord",   "b-nord",   "Europe/Rome"),
    (46.5386, 11.7528, "Ciampinoi",             "ciampinoi",             "Nord",   "b-nord",   "Europe/Rome"),
    (46.5750, 11.6722, "Ortisei",               "ortisei",               "Nord",   "b-nord",   "Europe/Rome"),
    (44.4056,  8.9463, "Genova",                "genova",                "Nord",   "b-nord",   "Europe/Rome"),
    (44.9561,  6.8761, "Sestriere",             "sestriere",             "Nord",   "b-nord",   "Europe/Rome"),
    (45.7369,  7.3200, "Aosta",                 "aosta",                 "Nord",   "b-nord",   "Europe/Rome"),
    (46.1679,  9.8722, "Sondrio",               "sondrio",               "Nord",   "b-nord",   "Europe/Rome"),
    (46.5286, 10.4528, "Passo dello Stelvio",   "stelvio",               "Nord",   "b-nord",   "Europe/Rome"),
    (38.1938, 15.5540, "Messina",               "messina",               "Sud",    "b-sud",    "Europe/Rome"),
    (38.1111, 15.6617, "Reggio Calabria",       "reggio_calabria",       "Sud",    "b-sud",    "Europe/Rome"),
    (38.1157, 13.3615, "Palermo",               "palermo",               "Sud",    "b-sud",    "Europe/Rome"),
    (38.4833, 14.9667, "Lipari (Isole Eolie)",  "lipari",                "Sud",    "b-sud",    "Europe/Rome"),
    (37.0755, 15.2866, "Siracusa",              "siracusa",              "Sud",    "b-sud",    "Europe/Rome"),
    (52.5200, 13.4050, "Berlino",               "berlino",               "Estero", "b-estero", "Europe/Berlin"),
    (51.5074, -0.1278, "Londra",                "londra",                "Estero", "b-estero", "Europe/London"),
    (69.6489, 18.9551, "Tromsø",                "tromso",                "Estero", "b-estero", "Europe/Oslo"),
    (52.2297, 21.0122, "Varsavia",              "varsavia",              "Estero", "b-estero", "Europe/Warsaw"),
    (40.7128, -74.006, "New York",              "new_york",              "Estero", "b-estero", "America/New_York"),
    (25.7617, -80.192, "Miami",                 "miami",                 "Estero", "b-estero", "America/New_York"),
    (34.0522,-118.244, "Los Angeles",           "los_angeles",           "Estero", "b-estero", "America/Los_Angeles"),
    (36.1699,-115.140, "Las Vegas",             "las_vegas",             "Estero", "b-estero", "America/Los_Angeles"),
    (42.3601, -71.059, "Boston",                "boston",                "Estero", "b-estero", "America/New_York"),
    (41.8781, -87.630, "Chicago",               "chicago",               "Estero", "b-estero", "America/Chicago"),
]

# Ordine delle sezioni (tabella e gallery). "Centro" esiste solo per le webcam.
ZONE_ORDER  = ["Roma", "Centro", "Mare", "Lago", "Monti", "Nord", "Sud", "Estero"]
ZONE_LABELS = {
    "Roma":   "🏙️  Città di Roma",
    "Centro": "🧭  Centro Italia",
    "Mare":   "🌊  Costa",
    "Lago":   "💧  Area Laghi",
    "Monti":  "⛰️  Monti & Appennino",
    "Nord":   "🏔️  Nord Italia",
    "Sud":    "☀️  Sud Italia & Isole",
    "Estero": "🌍  Estero",
}
_ZONE_CANON = {z.lower(): z for z in ZONE_ORDER}
DEFAULT_WEBCAM_ZONE = "Centro"

ROOT           = os.getcwd()
DASHBOARD_CONF = os.path.join(ROOT, "dashboard.txt")
IMG_EXT        = (".jpg", ".jpeg", ".png", ".gif", ".webp")
IMG_PROXY      = "webcam_proxy.php"   # restituisce un'immagine anche senza estensione
_ORE_RE        = re.compile(r"ore_\d{4}(?=\.jpg\b)", re.I)
ORE_TENTATIVI  = 13                   # slot controllati: da adesso a 1 ora fa
ORE_MAX_ETA    = timedelta(hours=3)   # oltre questa età è lo scatto di ieri, non di oggi



# ─── HELPER METEO ────────────────────────────────────────────────────────────
def wmo_icon(code):
    if code is None: return "❓"
    if code == 0:  return "☀️"
    if code <= 2:  return "🌤️"
    if code <= 3:  return "☁️"
    if code <= 49: return "🌫️"
    if code <= 59: return "🌦️"
    if code <= 69: return "🌧️"
    if code <= 79: return "🌨️"
    if code <= 84: return "🌧️"
    if code <= 99: return "⛈️"
    return "🌡️"


def tc(t):
    if t is None: return ""
    if t < 0:  return "tc-vc"
    if t < 5:  return "tc-c"
    if t < 10: return "tc-co"
    if t < 18: return "tc-m"
    if t < 28: return "tc-w"
    return "tc-h"


def wdir(deg):
    if deg is None: return "–"
    return ["N", "NE", "E", "SE", "S", "SO", "O", "NO"][round(deg / 45) % 8]


def is_img_url(url):
    if not url: return False
    path = url.lower().split("?")[0]
    return path.endswith(IMG_PROXY) or any(path.endswith(e) for e in IMG_EXT)


def cache_bust(url, cb):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}_cb={cb}"


def _ora_italia():
    try:
        return datetime.now(ZoneInfo("Europe/Rome"))
    except Exception:   # fusi orari non installati: serve "tzdata" in requirements.txt
        return datetime.now()


def url_ultimi_5_minuti(url, ora=None):
    """ore_1000.jpg → ultimo scatto a 5 minuti, ora italiana (10:02 → 1000, 10:06 → 1005)."""
    ora = ora or _ora_italia()
    return _ORE_RE.sub(f"ore_{ora.hour:02d}{ora.minute - ora.minute % 5:02d}", url)


def _troppo_vecchio(last_modified):
    """True se il file è di ieri: l'archivio è circolare e i nomi si ripetono ogni 24 ore."""
    try:
        data = parsedate_to_datetime(last_modified)
        if data.tzinfo is None:
            data = data.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) - data > ORE_MAX_ETA
    except Exception:
        return False


@st.cache_data(ttl=120, max_entries=30, show_spinner=False)
def scatto_recente(url):
    """
    Cerca l'ultimo scatto davvero pubblicato, tornando indietro di 5 minuti alla volta.
    Ritorna (url_scatto, immagine_data_uri, trovato).
    L'immagine viene scaricata dal server, così si vede anche se il sito blocca l'anteprima.
    Se il server non riesce a interrogare il sito, ritorna l'URL e lascia provare il browser.
    """
    ora = _ora_italia()
    for i in range(ORE_TENTATIVI):
        candidato = url_ultimi_5_minuti(url, ora - timedelta(minutes=5 * i))
        try:
            r = requests.get(candidato, timeout=6, headers={"User-Agent": "Mozilla/5.0"})
        except Exception:
            return url, None, True
        if r.status_code in (403, 429) or r.status_code >= 500:
            return url, None, True
        tipo = r.headers.get("Content-Type", "").split(";")[0].strip()
        if r.status_code != 200 or not tipo.startswith("image") or not r.content:
            continue
        if _troppo_vecchio(r.headers.get("Last-Modified", "")):
            continue
        dati = base64.b64encode(r.content).decode("ascii")
        return candidato, f"data:{tipo};base64,{dati}", True
    return url, None, False


# ─── CONFIG WEBCAM ───────────────────────────────────────────────────────────
def leggi_webcam_config(filepath=DASHBOARD_CONF):
    """{chiave: {"url": str, "zone": [zone esplicite] }}"""
    cfg = {}
    if not os.path.exists(filepath):
        return cfg
    with open(filepath, "r", encoding="utf-8") as f:
        for riga in f:
            riga = riga.strip()
            if not riga or riga.startswith("#") or "=" not in riga:
                continue
            k, _, v = riga.partition("=")
            k, v = k.strip().lower(), v.strip()
            if not k or not v:
                continue
            zone = []
            if "|" in v:
                head, _, tail = v.rpartition("|")
                cand = [z.strip().lower() for z in tail.split(",") if z.strip()]
                if cand and all(c in _ZONE_CANON for c in cand):
                    zone = [_ZONE_CANON[c] for c in cand]
                    v = head.strip()
            cfg[k] = {"url": url_ultimi_5_minuti(v), "zone": zone}
    return cfg


def leggi_webcam_links(filepath=DASHBOARD_CONF):
    """Compatibilità: {chiave: url}"""
    return {k: c["url"] for k, c in leggi_webcam_config(filepath).items()}


def nome_da_chiave(chiave):
    return chiave.replace("_", " ").strip().title()


def build_webcams(dati, cfg):
    """Lista di webcam (una per chiave) con zone, nome, temperatura."""
    by_key = {d["chiave"]: d for d in dati}
    cams = []
    for chiave, c in cfg.items():
        st_ = by_key.get(chiave)
        zone = c["zone"] or ([st_["zona"]] if st_ else [DEFAULT_WEBCAM_ZONE])
        url, src, trovato = c["url"], None, True
        if _ORE_RE.search(url):
            url, src, trovato = scatto_recente(url)
        cams.append({
            "chiave": chiave,
            "nome":   st_["nome"] if st_ else nome_da_chiave(chiave),
            "url":    url,
            "src":    src,       # immagine già scaricata (se disponibile)
            "trovato": trovato,  # False = nessuno scatto recente sul sito
            "zone":   zone,
            "temp":   st_.get("temp") if st_ else None,
            "is_img": is_img_url(c["url"]),
        })
    return cams


def zone_con_webcam(cams):
    """{zona: [cam,...]} — una webcam può stare in più zone."""
    out = {}
    for zona in ZONE_ORDER:
        lst = [c for c in cams if c["is_img"] and zona in c["zone"]]
        if lst:
            out[zona] = lst
    return out


# ─── FETCH CURRENT (batch) ───────────────────────────────────────────────────
@st.cache_data(ttl=900, show_spinner=False)
def fetch_current(stazioni):
    gruppi = defaultdict(list)
    for s in stazioni:
        gruppi[s[6]].append(s)
    risultati = {}
    for tz, lista in gruppi.items():
        lats = ",".join(str(s[0]) for s in lista)
        lons = ",".join(str(s[1]) for s in lista)
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lats}&longitude={lons}"
            f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
            f"precipitation,weathercode,wind_speed_10m,wind_direction_10m,pressure_msl"
            f"&hourly=freezing_level_height"
            f"&daily=temperature_2m_max,temperature_2m_min"
            f"&timezone={tz}"
        )
        try:
            raw = requests.get(url, timeout=15).json()
            if isinstance(raw, dict):
                raw = [raw]
            for i, s in enumerate(lista):
                try:
                    d = raw[i]; c = d["current"]
                    fz = d["hourly"].get("freezing_level_height", [None])[0]
                    risultati[(s[0], s[1])] = {
                        "ok": True,
                        "temp":  c.get("temperature_2m"),
                        "feels": c.get("apparent_temperature"),
                        "hum":   c.get("relative_humidity_2m"),
                        "prec":  c.get("precipitation"),
                        "wmo":   c.get("weathercode"),
                        "wind":  c.get("wind_speed_10m"),
                        "wdir":  c.get("wind_direction_10m"),
                        "pres":  c.get("pressure_msl"),
                        "tmax":  d["daily"]["temperature_2m_max"][0],
                        "tmin":  d["daily"]["temperature_2m_min"][0],
                        "fz":    fz,
                    }
                except Exception as e:
                    risultati[(s[0], s[1])] = {"ok": False, "err": str(e)}
        except Exception as e:
            for s in lista:
                risultati[(s[0], s[1])] = {"ok": False, "err": str(e)}
    out = []
    for s in stazioni:
        d = risultati.get((s[0], s[1]), {"ok": False, "err": "no data"})
        out.append({"nome": s[2], "chiave": s[3].lower(), "zona": s[4], "badge": s[5],
                    "lat": s[0], "lon": s[1], "tz": s[6], **d})
    return out


# ─── FETCH STORICO (archive API) ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_storico(lat, lon, tz, giorni=30):
    fine   = datetime.now() - timedelta(days=1)
    inizio = fine - timedelta(days=giorni)
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}"
        f"&start_date={inizio.strftime('%Y-%m-%d')}"
        f"&end_date={fine.strftime('%Y-%m-%d')}"
        f"&hourly=temperature_2m,relative_humidity_2m"
        f"&daily=temperature_2m_max,temperature_2m_min"
        f"&timezone={tz}"
    )
    try:
        d = requests.get(url, timeout=20).json()
        return {
            "times":  d["hourly"]["time"],
            "temp_h": d["hourly"]["temperature_2m"],
            "hum_h":  d["hourly"].get("relative_humidity_2m", []),
            "dates":  d["daily"]["time"],
            "tmax_d": d["daily"]["temperature_2m_max"],
            "tmin_d": d["daily"]["temperature_2m_min"],
        }
    except Exception as e:
        return {"error": str(e)}