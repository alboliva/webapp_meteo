import streamlit as st
import requests
from datetime import datetime
import json
import os

st.set_page_config(page_title="Dashboard Meteo", layout="wide", page_icon="🌡️")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

section[data-testid="stSidebar"] { background: #f1f5f9 !important; }

.meteo-header {
    font-family: 'DM Serif Display', serif;
    font-size: 2.6rem;
    font-weight: 400;
    color: #0f172a;
    letter-spacing: -0.02em;
    margin-bottom: 0;
    line-height: 1.1;
}
.meteo-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.8rem;
    font-weight: 500;
    color: #94a3b8;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
    margin-top: 4px;
}
.update-tag {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: #94a3b8;
    margin-bottom: 1rem;
}
.dot-live {
    display: inline-block;
    width: 7px; height: 7px;
    background: #22c55e;
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

.metric-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 18px 20px;
    text-align: center;
    margin-bottom: 1rem;
}
.metric-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.65rem;
    font-weight: 600;
    color: #94a3b8;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.metric-value {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem;
    font-weight: 400;
    line-height: 1;
}
.metric-loc {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.7rem;
    font-weight: 500;
    color: #94a3b8;
    margin-top: 4px;
}

.meteo-wrap { overflow-x: auto; margin-top: 1rem; }
table.meteo-tbl {
    width: 100%;
    border-collapse: collapse;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.84rem;
    background: white;
}
table.meteo-tbl thead th {
    background: #1e293b;
    color: #94a3b8;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 10px 14px;
    white-space: nowrap;
    border: none;
    text-align: left;
}
table.meteo-tbl tbody tr { border-bottom: 1px solid #f1f5f9; }
table.meteo-tbl tbody tr:hover { background: #f8fafc !important; }
table.meteo-tbl tbody td {
    padding: 11px 14px;
    color: #334155;
    white-space: nowrap;
    border: none;
    background: white;
    font-size: 0.84rem;
}
table.meteo-tbl tbody td.nome { color: #0f172a; font-weight: 600; }
table.meteo-tbl tbody td.nome a {
    color: #1d4ed8;
    text-decoration: none;
    border-bottom: 1px dashed #93c5fd;
}
table.meteo-tbl tbody td.nome a:hover {
    color: #1e40af;
    border-bottom-color: #1e40af;
}
table.meteo-tbl tr.sep td {
    background: #f1f5f9 !important;
    color: #64748b;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    font-weight: 700;
    padding: 7px 14px;
}

.badge {
    display: inline-block;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.52rem;
    padding: 2px 6px;
    border-radius: 20px;
    margin-left: 6px;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    vertical-align: middle;
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

.note-footer {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    color: #cbd5e1;
    margin-top: 2rem;
    line-height: 1.8;
}
</style>
""", unsafe_allow_html=True)

# ─── STAZIONI ────────────────────────────────────────────────────────────────
# (lat, lon, nome, chiave-txt, zona, badge, timezone)
STAZIONI = [
    # ROMA
    (41.8967, 12.4822, "Roma Centro",           "roma_centro",           "Roma",   "b-roma",   "Europe/Rome"),
    (41.9147, 12.4178, "Roma Pineta Sacchetti",  "roma_pineta_sacchetti", "Roma",   "b-roma",   "Europe/Rome"),
    (41.9183, 12.4347, "Roma Monte Mario",        "roma_monte_mario",      "Roma",   "b-roma",   "Europe/Rome"),
    (41.8836, 12.4694, "Roma Gianicolo",          "roma_gianicolo",        "Roma",   "b-roma",   "Europe/Rome"),
    # COSTA
    (41.9736, 12.0631, "Marina di San Nicola",   "marina_san_nicola",     "Mare",   "b-mare",   "Europe/Rome"),
    # LAGHI
    (42.1089, 12.1667, "Bracciano",              "bracciano",             "Lago",   "b-lago",   "Europe/Rome"),
    (42.1608, 12.2458, "Trevignano Romano",      "trevignano_romano",     "Lago",   "b-lago",   "Europe/Rome"),
    # MONTI
    (41.7700, 12.7200, "Monte Cavo",             "monte_cavo",            "Monti",  "b-monti",  "Europe/Rome"),
    (41.8561, 13.7950, "Pescasseroli",           "pescasseroli",          "Monti",  "b-monti",  "Europe/Rome"),
    (41.8750, 13.0333, "Monte Livata",           "monte_livata",          "Monti",  "b-monti",  "Europe/Rome"),
    (42.2333, 13.5667, "Campo Imperatore",       "campo_imperatore",      "Monti",  "b-monti",  "Europe/Rome"),
    (41.9917, 14.1017, "Campo di Giove",         "campo_di_giove",        "Monti",  "b-monti",  "Europe/Rome"),
    (41.8500, 14.0667, "Roccaraso",              "roccaraso",             "Monti",  "b-monti",  "Europe/Rome"),
    (41.7833, 13.8167, "Forca d'Acero",          "forca_dacero",          "Monti",  "b-monti",  "Europe/Rome"),
    # NORD ITALIA
    (45.9383, 7.6267,  "Breuil-Cervinia",        "",                      "Nord",   "b-nord",   "Europe/Rome"),
    (46.5569, 11.7855, "Selva Val Gardena",       "",                      "Nord",   "b-nord",   "Europe/Rome"),
    (46.5750, 11.6722, "Ortisei",                 "",                      "Nord",   "b-nord",   "Europe/Rome"),
    (44.4056, 8.9463,  "Genova",                  "",                      "Nord",   "b-nord",   "Europe/Rome"),
    (44.9128, 8.6148,  "Alessandria",             "",                      "Nord",   "b-nord",   "Europe/Rome"),
    (44.9561, 6.8761,  "Sestriere",               "",                      "Nord",   "b-nord",   "Europe/Rome"),
    (45.7369, 7.3200,  "Aosta",                   "",                      "Nord",   "b-nord",   "Europe/Rome"),
    (46.1679, 9.8722,  "Sondrio",                 "",                      "Nord",   "b-nord",   "Europe/Rome"),
    (46.5286, 10.4528, "Passo dello Stelvio",     "",                      "Nord",   "b-nord",   "Europe/Rome"),
    # SUD ITALIA
    (38.1938, 15.5540, "Messina",                 "",                      "Sud",    "b-sud",    "Europe/Rome"),
    (38.1111, 15.6617, "Reggio Calabria",         "",                      "Sud",    "b-sud",    "Europe/Rome"),
    (38.1157, 13.3615, "Palermo",                 "",                      "Sud",    "b-sud",    "Europe/Rome"),
    (38.4833, 14.9667, "Lipari (Isole Eolie)",    "",                      "Sud",    "b-sud",    "Europe/Rome"),
    (37.0755, 15.2866, "Siracusa",                "",                      "Sud",    "b-sud",    "Europe/Rome"),
    # ESTERO
    (52.5200, 13.4050, "Berlino",                 "",                      "Estero", "b-estero", "Europe/Berlin"),
    (51.5074, -0.1278, "Londra",                  "",                      "Estero", "b-estero", "Europe/London"),
    (69.6489, 18.9551, "Tromsø",                  "",                      "Estero", "b-estero", "Europe/Oslo"),
    (52.2297, 21.0122, "Varsavia",                "",                      "Estero", "b-estero", "Europe/Warsaw"),
    (40.7128, -74.0060,"New York",                "",                      "Estero", "b-estero", "America/New_York"),
    (25.7617, -80.1918,"Miami",                   "",                      "Estero", "b-estero", "America/New_York"),
    (34.0522, -118.2437,"Los Angeles",            "",                      "Estero", "b-estero", "America/Los_Angeles"),
    (36.1699, -115.1398,"Las Vegas",              "",                      "Estero", "b-estero", "America/Los_Angeles"),
    (42.3601, -71.0589, "Boston",                 "",                      "Estero", "b-estero", "America/New_York"),
    (41.8781, -87.6298, "Chicago",                "",                      "Estero", "b-estero", "America/Chicago"),
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

# ─── PATH ────────────────────────────────────────────────────────────────────
_ROOT          = os.getcwd()
HISTORY_FILE   = os.path.join(_ROOT, "dashboard_history.json")
DASHBOARD_CONF = os.path.join(_ROOT, "dashboard.txt")

# ─── HELPER ──────────────────────────────────────────────────────────────────
def wmo_icon(code):
    if code is None: return "❓"
    if code == 0:    return "☀️"
    if code <= 2:    return "🌤️"
    if code <= 3:    return "☁️"
    if code <= 49:   return "🌫️"
    if code <= 59:   return "🌦️"
    if code <= 69:   return "🌧️"
    if code <= 79:   return "🌨️"
    if code <= 84:   return "🌧️"
    if code <= 99:   return "⛈️"
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

def leggi_webcam_links(filepath):
    links = {}
    if not os.path.exists(filepath):
        return links
    with open(filepath, "r", encoding="utf-8") as f:
        for riga in f:
            riga = riga.strip()
            if not riga or riga.startswith("#"):
                continue
            if "=" in riga:
                chiave, _, valore = riga.partition("=")
                url = valore.strip()
                links[chiave.strip()] = url if url else None
    return links

# ─── BATCH FETCH (1 sola chiamata per gruppo timezone) ───────────────────────
@st.cache_data(ttl=900)
def fetch_all_batch(stazioni):
    """
    Open-Meteo accetta liste di lat/lon separate da virgola nella stessa URL.
    Raggruppiamo per timezone e facciamo 1 request per gruppo → molto più veloce.
    """
    # Raggruppa per timezone
    from collections import defaultdict
    gruppi = defaultdict(list)
    for s in stazioni:
        gruppi[s[6]].append(s)   # s[6] = timezone

    risultati = {}   # chiave: (lat,lon) → dict dati

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
            r = requests.get(url, timeout=15)
            raw = r.json()

            # Se una sola stazione → API ritorna dict, non lista
            if isinstance(raw, dict):
                raw = [raw]

            for i, s in enumerate(lista):
                try:
                    d = raw[i]
                    c  = d["current"]
                    fz = d["hourly"].get("freezing_level_height", [None])[0]
                    risultati[(s[0], s[1])] = {
                        "ok":    True,
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

    # Ricostruisci lista ordinata come STAZIONI
    out = []
    for s in stazioni:
        key = (s[0], s[1])
        d = risultati.get(key, {"ok": False, "err": "no data"})
        out.append({
            "nome":   s[2],
            "chiave": s[3],
            "zona":   s[4],
            "badge":  s[5],
            **d
        })
    return out

# ─── STORICO ─────────────────────────────────────────────────────────────────
def carica_storico():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return []

def salva_storico(dati):
    storico = carica_storico()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    snap = {"ts": ts, "stazioni": {}}
    for d in dati:
        if d.get("ok") and d.get("temp") is not None:
            snap["stazioni"][d["nome"]] = {
                "temp": d["temp"],
                "hum":  d.get("hum"),
                "tmin": d.get("tmin"),
                "tmax": d.get("tmax"),
            }
    if storico and storico[-1].get("ts", "")[:13] == ts[:13]:
        storico[-1] = snap
    else:
        storico.append(snap)
    storico = storico[-500:]
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(storico, f)
    except:
        pass

# ═══════════════════════════════════════════════════════════════════════════════
# RENDER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="meteo-header">Dashboard Meteo</div>', unsafe_allow_html=True)
st.markdown('<div class="meteo-sub">Italia · Europa · Mondo — Dati in tempo reale</div>', unsafe_allow_html=True)

webcam_links = leggi_webcam_links(DASHBOARD_CONF)

with st.spinner("Caricamento dati meteo…"):
    dati = fetch_all_batch(STAZIONI)

salva_storico(dati)

now_str = datetime.now().strftime("%d %B %Y — %H:%M")
st.markdown(f'<div class="update-tag"><span class="dot-live"></span>{now_str} &nbsp;·&nbsp; Open-Meteo (ECMWF) — 1 chiamata API per zona</div>', unsafe_allow_html=True)

# ─── METRICHE ────────────────────────────────────────────────────────────────
ok = [d for d in dati if d.get("ok") and d.get("temp") is not None]
if ok:
    cold      = min(ok, key=lambda x: x["temp"])
    hot       = max(ok, key=lambda x: x["temp"])
    min_bassa = min((d for d in ok if d.get("tmin") is not None), key=lambda x: x["tmin"])
    max_alta  = max((d for d in ok if d.get("tmax") is not None), key=lambda x: x["tmax"])

    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, loc, color in [
        (c1, "Più Freddo",     f"{cold['temp']:.1f}°C",      cold['nome'],      "#0ea5e9"),
        (c2, "Più Caldo",      f"{hot['temp']:.1f}°C",       hot['nome'],       "#ea580c"),
        (c3, "Minima + Bassa", f"{min_bassa['tmin']:.1f}°C", min_bassa['nome'], "#2563eb"),
        (c4, "Massima + Alta", f"{max_alta['tmax']:.1f}°C",  max_alta['nome'],  "#dc2626"),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color}">{val}</div>
                <div class="metric-loc">{loc}</div>
            </div>""", unsafe_allow_html=True)

# ─── TABELLA ─────────────────────────────────────────────────────────────────
rows = ""
for zona in ZONE_ORDER:
    zona_dati = [d for d in dati if d.get("zona") == zona]
    if not zona_dati:
        continue
    rows += f'<tr class="sep"><td colspan="10">{ZONE_LABELS[zona]}</td></tr>'
    for d in zona_dati:
        if not d.get("ok"):
            rows += (f'<tr><td class="nome">{d["nome"]}</td>'
                     f'<td colspan="9" style="color:#ef4444;background:white">Errore: {d.get("err","–")}</td></tr>')
            continue

        t  = d["temp"]
        fe = d["feels"]

        link_url = webcam_links.get(d["chiave"]) if d["chiave"] else None
        nome_cell = f'<a href="{link_url}" target="_blank" rel="noopener">{d["nome"]}</a>' if link_url else d["nome"]

        minmax = f'{d["tmin"]:.1f}° / {d["tmax"]:.1f}°' if d.get("tmin") is not None else "–"
        fz_str = f'{int(d["fz"])} m' if d.get("fz") is not None else "–"
        prec   = f'{d["prec"]:.1f} mm' if d.get("prec") is not None else "–"

        rows += f"""
<tr>
  <td class="nome">{nome_cell} <span class="badge {d['badge']}">{d['zona']}</span></td>
  <td>{wmo_icon(d['wmo'])}</td>
  <td><span class="{tc(t)}">{t:.1f}°C</span></td>
  <td><span class="{tc(fe)}">{fe:.1f}°C</span></td>
  <td>{d['hum']:.0f}%</td>
  <td>{d['wind']:.0f} km/h {wdir(d['wdir'])}</td>
  <td>{d['pres']:.0f} hPa</td>
  <td>{minmax}</td>
  <td>{prec}</td>
  <td>{fz_str}</td>
</tr>"""

st.markdown(f"""
<div class="meteo-wrap">
<table class="meteo-tbl">
<thead><tr>
  <th>Stazione</th>
  <th>Cond.</th>
  <th>Temp</th>
  <th>Percepita</th>
  <th>Umidità</th>
  <th>Vento</th>
  <th>Pressione</th>
  <th>Min / Max</th>
  <th>Pioggia</th>
  <th>Zero Term.</th>
</tr></thead>
<tbody>{rows}</tbody>
</table>
</div>
""", unsafe_allow_html=True)

# ─── CHART STORICO ───────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📈 Storico Temperature")

storico = carica_storico()
if len(storico) >= 2:
    nomi_disponibili = sorted({
        nome for snap in storico for nome in snap.get("stazioni", {})
    })
    sel = st.multiselect(
        "Seleziona stazioni",
        options=nomi_disponibili,
        default=[n for n in ["Roma Centro", "Campo Imperatore", "Tromsø", "Miami"] if n in nomi_disponibili],
    )
    if sel:
        import pandas as pd
        records = []
        for snap in storico:
            ts = snap.get("ts", "")
            for nome in sel:
                val = snap.get("stazioni", {}).get(nome)
                if val:
                    records.append({"Ora": ts, "Stazione": nome,
                                    "Temp": val.get("temp"),
                                    "Min":  val.get("tmin"),
                                    "Max":  val.get("tmax")})
        df = __import__('pandas').DataFrame(records)
        df["Ora"] = __import__('pandas').to_datetime(df["Ora"])
        df = df.sort_values("Ora")
        tab1, tab2, tab3 = st.tabs(["🌡️ Temperatura", "🔵 Minima", "🔴 Massima"])
        with tab1:
            st.line_chart(df.pivot_table(index="Ora", columns="Stazione", values="Temp", aggfunc="mean"))
        with tab2:
            st.line_chart(df.pivot_table(index="Ora", columns="Stazione", values="Min",  aggfunc="mean"))
        with tab3:
            st.line_chart(df.pivot_table(index="Ora", columns="Stazione", values="Max",  aggfunc="mean"))
        st.caption(f"Snapshot: {len(storico)} · File: {HISTORY_FILE}")
else:
    st.info("Lo storico si accumula ad ogni visita. Torna più tardi per vedere i grafici. 📊")

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="note-footer">
Dati: Open-Meteo.com (ECMWF IFS) · Cache 15 min · Batch API: ~3 chiamate per 38 stazioni<br>
Webcam: configura dashboard.txt nella root del progetto
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
if st.button("🔄 Aggiorna ora"):
    st.cache_data.clear()
    st.rerun()