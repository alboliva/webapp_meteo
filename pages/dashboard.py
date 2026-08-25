import streamlit as st
import requests
from datetime import datetime, timedelta
import os
import base64, mimetypes
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="Dashboard Meteo", layout="wide", page_icon="🌡️")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

section[data-testid="stSidebar"] { background: #f1f5f9 !important; }

.meteo-header {
    font-family: 'DM Serif Display', serif;
    font-size: 2.6rem; font-weight: 400; color: #0f172a;
    letter-spacing: -0.02em; margin-bottom: 0; line-height: 1.1;
}
.meteo-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.8rem; font-weight: 500; color: #94a3b8;
    letter-spacing: 0.1em; text-transform: uppercase;
    margin-bottom: 1.5rem; margin-top: 4px;
}
.update-tag {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem; color: #94a3b8; margin-bottom: 1rem;
}
.dot-live {
    display: inline-block; width: 7px; height: 7px;
    background: #22c55e; border-radius: 50%; margin-right: 6px;
    animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

.metric-card {
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 14px; padding: 18px 20px;
    text-align: center; margin-bottom: 1rem;
}
.metric-label {
    font-family: 'DM Sans', sans-serif; font-size: 0.65rem;
    font-weight: 600; color: #94a3b8; letter-spacing: 0.12em;
    text-transform: uppercase; margin-bottom: 6px;
}
.metric-value {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem; font-weight: 400; line-height: 1;
}
.metric-loc {
    font-family: 'DM Sans', sans-serif; font-size: 0.7rem;
    font-weight: 500; color: #94a3b8; margin-top: 4px;
}

.meteo-wrap { overflow-x: auto; margin-top: 1rem; }
table.meteo-tbl {
    width: 100%; border-collapse: collapse;
    font-family: 'DM Sans', sans-serif; font-size: 0.84rem; background: white;
}
table.meteo-tbl thead th {
    background: #1e293b; color: #94a3b8;
    font-size: 0.62rem; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; padding: 10px 14px;
    white-space: nowrap; border: none; text-align: left;
}
table.meteo-tbl tbody tr { border-bottom: 1px solid #f1f5f9; }
table.meteo-tbl tbody tr:hover { background: #f8fafc !important; }
table.meteo-tbl tbody td {
    padding: 11px 14px; color: #334155;
    white-space: nowrap; border: none; background: white; font-size: 0.84rem;
}
table.meteo-tbl tbody td.nome { color: #0f172a; font-weight: 600; }
table.meteo-tbl tbody td.nome a {
    color: #1d4ed8; text-decoration: none; border-bottom: 1px dashed #93c5fd;
}
table.meteo-tbl tbody td.nome a:hover { color: #1e40af; }
table.meteo-tbl tr.sep td {
    background: #f1f5f9 !important; color: #64748b;
    font-size: 0.65rem; letter-spacing: 0.15em;
    text-transform: uppercase; font-weight: 700; padding: 7px 14px;
}
.badge {
    display: inline-block; font-size: 0.52rem; padding: 2px 6px;
    border-radius: 20px; margin-left: 6px; font-weight: 700;
    letter-spacing: 0.06em; text-transform: uppercase; vertical-align: middle;
}
.b-roma   { background:#dbeafe; color:#1d4ed8; }
.b-monti  { background:#dcfce7; color:#15803d; }
.b-lago   { background:#ede9fe; color:#7c3aed; }
.b-mare   { background:#cffafe; color:#0e7490; }
.b-nord   { background:#fce7f3; color:#9d174d; }
.b-sud    { background:#fff7ed; color:#c2410c; }
.b-estero { background:#f1f5f9; color:#475569; }
.tc-vc { color:#2563eb; font-weight:700; }
.tc-c  { color:#0ea5e9; font-weight:700; }
.tc-co { color:#06b6d4; font-weight:700; }
.tc-m  { color:#16a34a; font-weight:700; }
.tc-w  { color:#ca8a04; font-weight:700; }
.tc-h  { color:#ea580c; font-weight:700; }

/* Gallery webcam */
.gallery-section {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem; color: #1e293b;
    margin-top: 1.5rem; margin-bottom: 0.8rem;
    border-bottom: 2px solid #e2e8f0; padding-bottom: 5px;
}
.wcam-card {
    background: white; border: 1px solid #e2e8f0;
    border-radius: 10px; overflow: hidden;
    margin-bottom: 16px;
}
.wcam-card-title {
    font-family: 'DM Sans', sans-serif; font-size: 0.75rem;
    font-weight: 600; color: #475569; padding: 6px 10px;
    background: #f8fafc; border-top: 1px solid #f1f5f9;
    text-align: center;
}
.wcam-img {
    width: 100%; display: block;
    min-height: 120px; background: #f1f5f9;
}

.note-footer {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem; color: #cbd5e1;
    margin-top: 2rem; line-height: 1.8;
}
</style>
""", unsafe_allow_html=True)

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
    (45.9383,  7.6267, "Breuil-Cervinia",       "breuil_cervinia",       "Nord",   "b-nord",   "Europe/Rome"),
    (45.9417,  7.6556, "Plan Maison",           "plan_maison",           "Nord",   "b-nord",   "Europe/Rome"),
    (45.9349,  7.7073, "Plateau Rosà",          "plateau_rosa",          "Nord",   "b-nord",   "Europe/Rome"),
    (46.5569, 11.7855, "Selva Val Gardena",     "selva_val_gardena",     "Nord",   "b-nord",   "Europe/Rome"),
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

ZONE_ORDER  = ["Roma", "Mare", "Lago", "Monti", "Nord", "Sud", "Estero"]
ZONE_LABELS = {
    "Roma":   "🏙️  Città di Roma",
    "Mare":   "🌊  Costa",
    "Lago":   "💧  Area Laghi",
    "Monti":  "⛰️  Monti & Appennino",
    "Nord":   "🏔️  Nord Italia",
    "Sud":    "☀️  Sud Italia & Isole",
    "Estero": "🌍  Estero",
}

_ROOT          = os.getcwd()
DASHBOARD_CONF = os.path.join(_ROOT, "dashboard.txt")
IMG_EXT        = (".jpg", ".jpeg", ".png", ".gif", ".webp")

# ─── HELPER ──────────────────────────────────────────────────────────────────
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
    return ["N","NE","E","SE","S","SO","O","NO"][round(deg/45)%8]

def is_img_url(url):
    if not url: return False
    return any(url.lower().split("?")[0].endswith(e) for e in IMG_EXT)

def leggi_webcam_links(filepath):
    links = {}
    if not os.path.exists(filepath): return links
    with open(filepath, "r", encoding="utf-8") as f:
        for riga in f:
            riga = riga.strip()
            if not riga or riga.startswith("#"): continue
            if "=" in riga:
                k, _, v = riga.partition("=")
                v = v.strip()
                if v: links[k.strip().lower()] = v
    return links

# ─── FETCH CURRENT (batch) ───────────────────────────────────────────────────
@st.cache_data(ttl=900)
def fetch_current(stazioni):
    from collections import defaultdict
    gruppi = defaultdict(list)
    for s in stazioni: gruppi[s[6]].append(s)
    risultati = {}
    for tz, lista in gruppi.items():
        lats = ",".join(str(s[0]) for s in lista)
        lons = ",".join(str(s[1]) for s in lista)
        url  = (
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
            if isinstance(raw, dict): raw = [raw]
            for i, s in enumerate(lista):
                try:
                    d  = raw[i]; c = d["current"]
                    fz = d["hourly"].get("freezing_level_height", [None])[0]
                    risultati[(s[0],s[1])] = {
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
                    risultati[(s[0],s[1])] = {"ok": False, "err": str(e)}
        except Exception as e:
            for s in lista: risultati[(s[0],s[1])] = {"ok": False, "err": str(e)}
    out = []
    for s in stazioni:
        d = risultati.get((s[0],s[1]), {"ok": False, "err": "no data"})
        out.append({"nome": s[2], "chiave": s[3].lower(), "zona": s[4], "badge": s[5],
                    "lat": s[0], "lon": s[1], "tz": s[6], **d})
    return out

# ─── FETCH STORICO (archive API) ─────────────────────────────────────────────
@st.cache_data(ttl=3600)   # cache 1h — i dati storici non cambiano spesso
def fetch_storico(lat, lon, tz, giorni=30):
    """
    Recupera temperatura oraria degli ultimi N giorni dall'API archive.
    Copre fino a ieri (le ultime 24h non sono disponibili nell'archivio).
    """
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
        r = requests.get(url, timeout=20)
        d = r.json()
        return {
            "times":    d["hourly"]["time"],
            "temp_h":   d["hourly"]["temperature_2m"],
            "hum_h":    d["hourly"].get("relative_humidity_2m", []),
            "dates":    d["daily"]["time"],
            "tmax_d":   d["daily"]["temperature_2m_max"],
            "tmin_d":   d["daily"]["temperature_2m_min"],
        }
    except Exception as e:
        return {"error": str(e)}

# ═══════════════════════════════════════════════════════════════════════════════
# GENERATORE GALLERY HTML (export per sezione / tutte · snapshot "freezato")
# ═══════════════════════════════════════════════════════════════════════════════
_GALLERY_TEMPLATE = """<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Gallery Webcam — __NOW__</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400&display=swap');
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #0f172a; color: #e2e8f0;
    font-family: 'DM Sans', sans-serif; padding: 32px 24px;
    -webkit-font-smoothing: antialiased;
  }
  header { margin-bottom: 36px; border-bottom: 1px solid #1e293b; padding-bottom: 20px; }
  header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem; font-weight: 400; color: #f1f5f9; letter-spacing: -0.02em;
  }
  header p {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem; color: #64748b; margin-top: 8px; line-height: 1.7;
  }
  header .tag {
    display:inline-block; margin-top:10px; padding:3px 10px; border-radius:20px;
    background:#1e293b; border:1px solid #334155; color:#94a3b8;
    font-family:'IBM Plex Mono',monospace; font-size:0.62rem; letter-spacing:0.05em;
  }
  section { margin-bottom: 48px; }
  section h2 {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem; font-weight: 400; color: #94a3b8;
    margin-bottom: 18px; padding-bottom: 8px; border-bottom: 1px solid #1e293b;
    display:flex; align-items:center; gap:10px;
  }
  section h2 .cnt {
    font-family:'IBM Plex Mono',monospace; font-size:0.6rem; color:#64748b;
    background:#1e293b; border:1px solid #334155; border-radius:20px; padding:2px 9px;
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
  }
  .card {
    background: #1e293b; border-radius: 12px; overflow: hidden;
    border: 1px solid #334155; cursor: zoom-in;
    transition: transform .18s, box-shadow .18s, border-color .18s;
  }
  .card:hover {
    transform: translateY(-3px);
    box-shadow: 0 14px 34px rgba(0,0,0,.55);
    border-color:#475569;
  }
  .card img {
    width: 100%; display: block;
    aspect-ratio: 4/3; object-fit: cover; background: #0f172a;
  }
  .card figcaption {
    font-size: 0.78rem; font-weight: 600; color: #cbd5e1;
    padding: 10px 14px; text-align: center;
    background: #1e293b; border-top: 1px solid #334155; letter-spacing: 0.02em;
  }
  footer {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem; color: #334155;
    margin-top: 48px; padding-top: 16px; border-top: 1px solid #1e293b; line-height: 1.9;
  }
  /* ── LIGHTBOX (foto grande + nitida) ───────────────────────────────── */
  .lightbox {
    position: fixed; inset: 0; z-index: 9999;
    background: rgba(7,11,20,.96);
    display: none; align-items: center; justify-content: center;
    backdrop-filter: blur(4px);
  }
  .lightbox.on { display: flex; }
  .lb-img {
    max-width: 95vw; max-height: 88vh;
    object-fit: contain; border-radius: 8px;
    box-shadow: 0 24px 80px rgba(0,0,0,.7);
    image-rendering: auto;
  }
  .lb-cap {
    position: fixed; bottom: 22px; left: 50%; transform: translateX(-50%);
    font-family: 'DM Sans', sans-serif; font-size: 0.95rem; font-weight: 600;
    color: #f1f5f9; background: rgba(15,23,42,.85);
    padding: 8px 18px; border-radius: 24px; border: 1px solid #334155;
    max-width: 80vw; text-align: center;
  }
  .lb-btn {
    position: fixed; background: rgba(30,41,59,.85); color: #e2e8f0;
    border: 1px solid #475569; cursor: pointer; user-select: none;
    width: 52px; height: 52px; border-radius: 50%;
    font-size: 1.6rem; line-height: 1; display:flex; align-items:center; justify-content:center;
    transition: background .15s, transform .15s;
  }
  .lb-btn:hover { background: #334155; transform: scale(1.06); }
  .lb-close { top: 20px; right: 20px; font-size: 1.5rem; }
  .lb-prev  { left: 18px; top: 50%; transform: translateY(-50%); }
  .lb-next  { right: 18px; top: 50%; transform: translateY(-50%); }
  .lb-prev:hover, .lb-next:hover { transform: translateY(-50%) scale(1.06); }
  .lb-dl {
    position: fixed; top: 20px; left: 20px;
    background: rgba(30,41,59,.85); color: #e2e8f0; text-decoration: none;
    border: 1px solid #475569; border-radius: 24px; padding: 9px 16px;
    font-family: 'DM Sans', sans-serif; font-size: 0.8rem; font-weight: 600;
    display: flex; align-items: center; gap: 6px; transition: background .15s;
  }
  .lb-dl:hover { background: #334155; }
  @media (max-width: 768px) {
    .grid { grid-template-columns: repeat(2, 1fr); }
    .lb-btn { width: 44px; height: 44px; font-size: 1.3rem; }
  }
  @media (max-width: 480px) {
    .grid { grid-template-columns: 1fr; }
    .lb-cap { bottom: 80px; }
  }
</style>
</head>
<body>
<header>
  <h1>📷 Gallery Webcam</h1>
  <p>Esportata il __NOW__ · Open-Meteo (ECMWF) · __COUNT__ foto · Cache-bust: __CB__</p>
  <span class="tag">__MODE__</span>
</header>
__SEZIONI__
<footer>
  Dati meteo: Open-Meteo Forecast (ECMWF IFS)<br>
  Modalità: __MODE__ · Gallery esportata il __NOW__<br>
  Clicca una foto per vederla grande · frecce ← → o tasti per navigare · ESC per chiudere
</footer>

<!-- LIGHTBOX -->
<div id="lb" class="lightbox">
  <a id="lb-dl" class="lb-dl" download>⬇︎ Salva foto</a>
  <button class="lb-btn lb-close" title="Chiudi (ESC)">&times;</button>
  <button class="lb-btn lb-prev"  title="Precedente (←)">&#8249;</button>
  <img id="lb-img" class="lb-img" alt="">
  <button class="lb-btn lb-next"  title="Successiva (→)">&#8250;</button>
  <div id="lb-cap" class="lb-cap"></div>
</div>

<script>
  var figs = Array.prototype.slice.call(document.querySelectorAll('.card'));
  var lb    = document.getElementById('lb');
  var lbImg = document.getElementById('lb-img');
  var lbCap = document.getElementById('lb-cap');
  var lbDl  = document.getElementById('lb-dl');
  var idx = -1;

  function slug(s){ return (s||'foto').replace(/[^a-z0-9]+/gi,'_').replace(/^_|_$/g,'').toLowerCase(); }

  function open(i){
    idx = i;
    var f = figs[i];
    var img = f.querySelector('img');
    var cap = f.getAttribute('data-cap') || '';
    lbImg.src = img.currentSrc || img.src;
    lbImg.alt = cap;
    lbCap.textContent = cap;
    lbDl.href = img.currentSrc || img.src;
    lbDl.setAttribute('download', slug(cap) + '.jpg');
    lb.classList.add('on');
    document.body.style.overflow = 'hidden';
  }
  function close(){ lb.classList.remove('on'); document.body.style.overflow=''; }
  function step(d){
    if(!figs.length) return;
    var i = idx;
    for(var k=0;k<figs.length;k++){
      i = (i + d + figs.length) % figs.length;
      if(figs[i].style.display !== 'none'){ open(i); return; }
    }
  }
  figs.forEach(function(f,i){ f.addEventListener('click', function(){ open(i); }); });
  document.querySelector('.lb-close').addEventListener('click', close);
  document.querySelector('.lb-prev').addEventListener('click', function(e){ e.stopPropagation(); step(-1); });
  document.querySelector('.lb-next').addEventListener('click', function(e){ e.stopPropagation(); step(1); });
  lb.addEventListener('click', function(e){ if(e.target === lb) close(); });
  document.addEventListener('keydown', function(e){
    if(!lb.classList.contains('on')) return;
    if(e.key === 'Escape') close();
    else if(e.key === 'ArrowLeft') step(-1);
    else if(e.key === 'ArrowRight') step(1);
  });
</script>
</body>
</html>"""


def _img_to_data_uri(url, cb, timeout=12):
    """Scarica l'immagine ORA e la restituisce come data-URI base64 (foto congelata).
    None se fallisce."""
    sep  = "&" if "?" in url else "?"
    full = f"{url}{sep}_cb={cb}"
    try:
        r = requests.get(full, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        ct = r.headers.get("Content-Type", "").split(";")[0].strip()
        if not ct.startswith("image"):
            ct = mimetypes.guess_type(url)[0] or "image/jpeg"
        b64 = base64.b64encode(r.content).decode("ascii")
        return f"data:{ct};base64,{b64}"
    except Exception:
        return None


def _live_url(url, cb):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}_cb={cb}"


def genera_html_gallery(zone_dict, webcam_links, cb, freeze=True):
    """zone_dict: {zona: [cam,...]} — può essere TUTTE le zone o UNA sola sottosezione.
    freeze=True  -> scarica e incorpora le foto (snapshot fisso del momento).
    freeze=False -> usa gli URL live (la foto si aggiorna riaprendo il file)."""
    now_exp = datetime.now().strftime("%d/%m/%Y %H:%M")

    # 1) Risolvi la sorgente di ogni webcam (chiave -> src)
    src_map = {}
    if freeze:
        tasks = []
        for cams in zone_dict.values():
            for cam in cams:
                ch = cam["chiave"]
                if ch not in src_map:
                    src_map[ch] = None
                    tasks.append((ch, webcam_links[ch]))
        def _work(item):
            ch, url = item
            return ch, _img_to_data_uri(url, cb)
        with ThreadPoolExecutor(max_workers=8) as ex:
            for ch, datauri in ex.map(_work, tasks):
                src_map[ch] = datauri or _live_url(webcam_links[ch], cb)
    else:
        for cams in zone_dict.values():
            for cam in cams:
                ch = cam["chiave"]
                src_map[ch] = _live_url(webcam_links[ch], cb)

    # 2) Costruisci le sezioni HTML
    sezioni = ""
    n_foto = 0
    for zona, cams in zone_dict.items():
        label = ZONE_LABELS.get(zona, zona)
        celle = ""
        for cam in cams:
            ch  = cam["chiave"]
            src = src_map[ch]
            t_str = f" · {cam['temp']:.1f}°C" if cam.get("temp") is not None else ""
            cap   = (f"{cam['nome']}{t_str}").replace('"', "&quot;")
            alt   = cam["nome"].replace('"', "&quot;")
            celle += (
                f'<figure class="card" data-cap="{cap}">'
                f'<img src="{src}" loading="lazy" alt="{alt}" '
                f"onerror=\"this.closest('figure').style.display='none'\">"
                f'<figcaption>{cap}</figcaption>'
                f'</figure>'
            )
            n_foto += 1
        sezioni += (
            f'<section><h2>{label} <span class="cnt">{len(cams)}</span></h2>'
            f'<div class="grid">{celle}</div></section>'
        )

    modo = "📸 Snapshot congelato (foto fisse del momento)" if freeze \
           else "🔄 Live (le foto si aggiornano riaprendo)"

    return (_GALLERY_TEMPLATE
            .replace("__NOW__", now_exp)
            .replace("__CB__", str(cb))
            .replace("__COUNT__", str(n_foto))
            .replace("__MODE__", modo)
            .replace("__SEZIONI__", sezioni))

# ═══════════════════════════════════════════════════════════════════════════════
# RENDER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="meteo-header">Dashboard Meteo</div>', unsafe_allow_html=True)
st.markdown('<div class="meteo-sub">Italia · Europa · Mondo — Dati in tempo reale</div>', unsafe_allow_html=True)

webcam_links = leggi_webcam_links(DASHBOARD_CONF)

with st.spinner("Caricamento dati meteo…"):
    dati = fetch_current(STAZIONI)

now_str = datetime.now().strftime("%d %B %Y — %H:%M")
st.markdown(f'<div class="update-tag"><span class="dot-live"></span>{now_str} &nbsp;·&nbsp; Open-Meteo (ECMWF)</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# GALLERY WEBCAM + ESPORTAZIONE  ── IN TESTA, prima delle temperature ──────────
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("### 📷 Gallery Webcam")

zone_con_cam = {}
for zona in ZONE_ORDER:
    cams = [
        d for d in dati
        if d.get("zona") == zona and is_img_url(webcam_links.get(d["chiave"]))
    ]
    if cams:
        zone_con_cam[zona] = cams

if not zone_con_cam:
    st.info("Nessuna webcam configurata. Aggiungi URL immagine diretta (jpg/jpeg/png) in `dashboard.txt`.")
else:
    zone_tabs = list(zone_con_cam.keys())
    tab_labels = [f"{ZONE_LABELS[z].split()[0]} {z}" for z in zone_tabs]
    tabs = st.tabs(tab_labels)

    cb = int(datetime.now().timestamp() // 300)

    # ── Pannello di esportazione (sopra i tab) ──────────────────────────────
    st.markdown("#### ⬇️ Esporta gallery")

    label_to_zona = {ZONE_LABELS.get(z, z): z for z in zone_tabs}
    sezione_opts  = ["🌍 Tutte le sezioni"] + list(label_to_zona.keys())

    cexp1, cexp2, cexp3 = st.columns([2, 1, 1])
    with cexp1:
        sel_sezione = st.selectbox(
            "Cosa esportare",
            sezione_opts,
            key="gal_sel",
            help="Scegli una singola sezione (Sud, Nord, Mare, Laghi…) oppure tutte.",
        )
    with cexp2:
        freeze = st.checkbox(
            "📸 Congela foto",
            value=True,
            key="gal_freeze",
            help="Scarica le immagini ADESSO e le incorpora nel file: diventa una "
                 "fotografia fissa di questo momento, anche riaprendola domani.",
        )
    with cexp3:
        st.write("")
        prepara = st.button("🛠️ Prepara file", key="gal_prep", use_container_width=True)

    if prepara:
        if sel_sezione.startswith("🌍"):
            sub, suffix = zone_con_cam, "tutte"
        else:
            z = label_to_zona[sel_sezione]
            sub, suffix = {z: zone_con_cam[z]}, z.lower().replace(" ", "_")

        spin = "Scarico e congelo le immagini…" if freeze else "Genero la gallery…"
        with st.spinner(spin):
            html_export = genera_html_gallery(sub, webcam_links, cb, freeze=freeze)

        st.session_state["gal_html"]  = html_export
        st.session_state["gal_fname"] = (
            f"gallery_{suffix}_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
        )
        st.session_state["gal_meta"]  = f"{sel_sezione} · {'congelata' if freeze else 'live'}"

    if st.session_state.get("gal_html"):
        st.success(f"Pronta: {st.session_state.get('gal_meta','')}")
        st.download_button(
            label="⬇️ Scarica HTML gallery",
            data=st.session_state["gal_html"].encode("utf-8"),
            file_name=st.session_state["gal_fname"],
            mime="text/html",
            help="File HTML autonomo: foto cliccabili, grandi e nitide (lightbox).",
        )

    # ── Webcam a video, una scheda per tab ──────────────────────────────────
    for tab, zona in zip(tabs, zone_tabs):
        with tab:
            cams = zone_con_cam[zona]
            cols_per_row = 3
            for i in range(0, len(cams), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, cam in enumerate(cams[i:i+cols_per_row]):
                    url = webcam_links[cam["chiave"]]
                    url_cb = f"{url}?_cb={cb}" if "?" not in url else url
                    t_str = f" · {cam['temp']:.1f}°C" if cam.get("temp") is not None else ""
                    with cols[j]:
                        st.markdown(f"""
                        <div class="wcam-card">
                            <a href="{url}" target="_blank">
                                <img src="{url_cb}" class="wcam-img"
                                     alt="{cam['nome']}"
                                     onerror="this.src='';this.style.minHeight='80px'">
                            </a>
                            <div class="wcam-card-title">
                                {cam['nome']}{t_str}
                            </div>
                        </div>""", unsafe_allow_html=True)

st.markdown("---")

# ─── METRICHE ────────────────────────────────────────────────────────────────
ok_d = [d for d in dati if d.get("ok") and d.get("temp") is not None]
if ok_d:
    cold = min(ok_d, key=lambda x: x["temp"])
    hot  = max(ok_d, key=lambda x: x["temp"])
    mn   = min((d for d in ok_d if d.get("tmin") is not None), key=lambda x: x["tmin"])
    mx   = max((d for d in ok_d if d.get("tmax") is not None), key=lambda x: x["tmax"])
    c1,c2,c3,c4 = st.columns(4)
    for col,label,val,loc,color in [
        (c1,"Più Freddo",    f"{cold['temp']:.1f}°C", cold['nome'], "#0ea5e9"),
        (c2,"Più Caldo",     f"{hot['temp']:.1f}°C",  hot['nome'],  "#ea580c"),
        (c3,"Minima + Bassa",f"{mn['tmin']:.1f}°C",   mn['nome'],   "#2563eb"),
        (c4,"Massima + Alta",f"{mx['tmax']:.1f}°C",   mx['nome'],   "#dc2626"),
    ]:
        with col:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color}">{val}</div>
                <div class="metric-loc">{loc}</div>
            </div>""", unsafe_allow_html=True)

# ─── TABELLA ─────────────────────────────────────────────────────────────────
rows = ""
for zona in ZONE_ORDER:
    zona_dati = [d for d in dati if d.get("zona") == zona]
    if not zona_dati: continue
    rows += f'<tr class="sep"><td colspan="10">{ZONE_LABELS[zona]}</td></tr>'
    for d in zona_dati:
        if not d.get("ok"):
            rows += f'<tr><td class="nome">{d["nome"]}</td><td colspan="9" style="color:#ef4444;background:white">Errore</td></tr>'
            continue
        t  = d["temp"]; fe = d["feels"]
        url = webcam_links.get(d["chiave"])
        nome_cell = (f'<a href="{url}" target="_blank" rel="noopener">{d["nome"]}</a>'
                     if url else d["nome"])

        minmax = f'{d["tmin"]:.1f}° / {d["tmax"]:.1f}°' if d.get("tmin") is not None else "–"
        fz_str = f'{int(d["fz"])} m' if d.get("fz") is not None else "–"
        rows += f"""<tr>
  <td class="nome">{nome_cell} <span class="badge {d['badge']}">{d['zona']}</span></td>
  <td>{wmo_icon(d['wmo'])}</td>
  <td><span class="{tc(t)}">{t:.1f}°C</span></td>
  <td><span class="{tc(fe)}">{fe:.1f}°C</span></td>
  <td>{d['hum']:.0f}%</td>
  <td>{d['wind']:.0f} km/h {wdir(d['wdir'])}</td>
  <td>{d['pres']:.0f} hPa</td>
  <td>{minmax}</td>
  <td>{d['prec']:.1f} mm</td>
  <td>{fz_str}</td>
</tr>"""

st.markdown(f"""<div class="meteo-wrap"><table class="meteo-tbl">
<thead><tr>
  <th>Stazione</th><th>Cond.</th><th>Temp</th><th>Percepita</th>
  <th>Umidità</th><th>Vento</th><th>Pressione</th><th>Min / Max</th><th>Pioggia</th><th>Zero Term.</th>
</tr></thead>
<tbody>{rows}</tbody>
</table></div>""", unsafe_allow_html=True)

# ─── STORICO DA ARCHIVE API ───────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📈 Storico Temperature (Archive API)")
st.caption("Dati orari storici da Open-Meteo Archive — fino a ieri, fino a 90 giorni.")

import pandas as pd

col_sel, col_opt = st.columns([2, 1])
with col_sel:
    nomi_tutti = [d["nome"] for d in dati if d.get("ok")]
    default_sel = [n for n in ["Roma Centro", "Campo Imperatore", "Tromsø", "Miami"] if n in nomi_tutti]
    sel_stazioni = st.multiselect(
        "Seleziona stazioni (max 6 per leggibilità)",
        options=nomi_tutti,
        default=default_sel,
        max_selections=6,
    )
with col_opt:
    giorni = st.select_slider(
        "Periodo",
        options=[7, 14, 30, 60, 90],
        value=30,
        format_func=lambda x: f"{x} giorni"
    )
    risoluzione = st.radio("Risoluzione", ["Oraria", "Giornaliera"], horizontal=True)

if sel_stazioni:
    with st.spinner(f"Caricamento dati storici ({giorni}gg) per {len(sel_stazioni)} stazioni…"):
        frames_h = []   # orario
        frames_d = []   # giornaliero

        for nome in sel_stazioni:
            s_info = next((d for d in dati if d["nome"] == nome), None)
            if not s_info: continue
            storico = fetch_storico(s_info["lat"], s_info["lon"], s_info["tz"], giorni)
            if "error" in storico:
                st.warning(f"{nome}: {storico['error']}")
                continue

            if risoluzione == "Oraria":
                df_h = pd.DataFrame({
                    "Ora":  pd.to_datetime(storico["times"]),
                    nome:   storico["temp_h"],
                })
                df_h = df_h.set_index("Ora")
                frames_h.append(df_h)
            else:
                df_d = pd.DataFrame({
                    "Data":           pd.to_datetime(storico["dates"]),
                    f"{nome} max":    storico["tmax_d"],
                    f"{nome} min":    storico["tmin_d"],
                })
                df_d = df_d.set_index("Data")
                frames_d.append(df_d)

    if risoluzione == "Oraria" and frames_h:
        df_all = pd.concat(frames_h, axis=1).sort_index()
        st.line_chart(df_all)
        st.caption(f"Temperatura oraria · {giorni} giorni · {len(frames_h)} stazioni · Fonte: Open-Meteo Archive")

    elif risoluzione == "Giornaliera" and frames_d:
        df_all = pd.concat(frames_d, axis=1).sort_index()
        tab_max, tab_min = st.tabs(["🔴 Massime giornaliere", "🔵 Minime giornaliere"])
        with tab_max:
            cols_max = [c for c in df_all.columns if c.endswith(" max")]
            st.line_chart(df_all[cols_max].rename(columns=lambda c: c.replace(" max","")))
        with tab_min:
            cols_min = [c for c in df_all.columns if c.endswith(" min")]
            st.line_chart(df_all[cols_min].rename(columns=lambda c: c.replace(" min","")))
        st.caption(f"Temperature giornaliere · {giorni} giorni · Fonte: Open-Meteo Archive")

elif not sel_stazioni:
    st.info("Seleziona almeno una stazione per vedere il grafico storico.")

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""<div class="note-footer">
Dati attuali: Open-Meteo Forecast (ECMWF IFS) · Cache 15 min<br>
Dati storici: Open-Meteo Archive · Cache 1h · Disponibili fino a ieri<br>
🖼️ immagine diretta · 🌐 pagina webcam · Gallery aggiornata ogni 5 min
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
if st.button("🔄 Aggiorna ora"):
    st.cache_data.clear()
    st.rerun()