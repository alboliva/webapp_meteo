import os
from datetime import datetime

import streamlit as st

from common import (STAZIONI, ZONE_LABELS, ZONE_ORDER, build_webcams, cache_bust,
                    fetch_current, leggi_webcam_config, tc, wdir, wmo_icon, zone_con_webcam)
from gallery_export import genera_html_gallery

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
.update-tag { font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; color: #94a3b8; margin-bottom: 1rem; }
.dot-live {
    display: inline-block; width: 7px; height: 7px;
    background: #22c55e; border-radius: 50%; margin-right: 6px; animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
.metric-card {
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 14px; padding: 18px 20px; text-align: center; margin-bottom: 1rem;
}
.metric-label {
    font-family: 'DM Sans', sans-serif; font-size: 0.65rem; font-weight: 600; color: #94a3b8;
    letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 6px;
}
.metric-value { font-family: 'DM Serif Display', serif; font-size: 2.2rem; font-weight: 400; line-height: 1; }
.metric-loc { font-family: 'DM Sans', sans-serif; font-size: 0.7rem; font-weight: 500; color: #94a3b8; margin-top: 4px; }
.meteo-wrap { overflow-x: auto; margin-top: 1rem; }
table.meteo-tbl { width: 100%; border-collapse: collapse; font-family: 'DM Sans', sans-serif; font-size: 0.84rem; background: white; }
table.meteo-tbl thead th {
    background: #1e293b; color: #94a3b8; font-size: 0.62rem; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; padding: 10px 14px; white-space: nowrap; border: none; text-align: left;
}
table.meteo-tbl tbody tr { border-bottom: 1px solid #f1f5f9; }
table.meteo-tbl tbody tr:hover { background: #f8fafc !important; }
table.meteo-tbl tbody td { padding: 11px 14px; color: #334155; white-space: nowrap; border: none; background: white; font-size: 0.84rem; }
table.meteo-tbl tbody td.nome { color: #0f172a; font-weight: 600; }
table.meteo-tbl tbody td.nome a { color: #1d4ed8; text-decoration: none; border-bottom: 1px dashed #93c5fd; }
table.meteo-tbl tbody td.nome a:hover { color: #1e40af; }
table.meteo-tbl tr.sep td {
    background: #f1f5f9 !important; color: #64748b; font-size: 0.65rem; letter-spacing: 0.15em;
    text-transform: uppercase; font-weight: 700; padding: 7px 14px;
}
.badge {
    display: inline-block; font-size: 0.52rem; padding: 2px 6px; border-radius: 20px; margin-left: 6px;
    font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; vertical-align: middle;
}
.b-roma   { background:#dbeafe; color:#1d4ed8; }
.b-monti  { background:#dcfce7; color:#15803d; }
.b-lago   { background:#ede9fe; color:#7c3aed; }
.b-mare   { background:#cffafe; color:#0e7490; }
.b-nord   { background:#fce7f3; color:#9d174d; }
.b-sud    { background:#fff7ed; color:#c2410c; }
.b-estero { background:#f1f5f9; color:#475569; }
.tc-vc { color:#2563eb; font-weight:700; } .tc-c { color:#0ea5e9; font-weight:700; }
.tc-co { color:#06b6d4; font-weight:700; } .tc-m { color:#16a34a; font-weight:700; }
.tc-w  { color:#ca8a04; font-weight:700; } .tc-h { color:#ea580c; font-weight:700; }
.wcam-card { background: white; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; margin-bottom: 16px; }
.wcam-card-title {
    font-family: 'DM Sans', sans-serif; font-size: 0.75rem; font-weight: 600; color: #475569;
    padding: 6px 10px; background: #f8fafc; border-top: 1px solid #f1f5f9; text-align: center;
}
.wcam-img { width: 100%; display: block; min-height: 120px; background: #f1f5f9; }
.note-footer { font-family: 'IBM Plex Mono', monospace; font-size: 0.62rem; color: #cbd5e1; margin-top: 2rem; line-height: 1.8; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="meteo-header">Dashboard Meteo</div>', unsafe_allow_html=True)
st.markdown('<div class="meteo-sub">Italia · Europa · Mondo — Dati in tempo reale</div>', unsafe_allow_html=True)

webcam_cfg = leggi_webcam_config()

with st.spinner("Caricamento dati meteo…"):
    dati = fetch_current(STAZIONI)

now_str = datetime.now().strftime("%d %B %Y — %H:%M")
st.markdown(f'<div class="update-tag"><span class="dot-live"></span>{now_str} &nbsp;·&nbsp; Open-Meteo (ECMWF)</div>',
            unsafe_allow_html=True)

webcams      = build_webcams(dati, webcam_cfg)
zone_con_cam = zone_con_webcam(webcams)

# ═══════════════════════════════════════════════════════════════════════════════
# GALLERY WEBCAM
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("### 📷 Gallery Webcam")

if not zone_con_cam:
    st.info("Nessuna webcam configurata. Aggiungi URL immagine diretta (jpg/jpeg/png) in `dashboard.txt`.")
else:
    zone_tabs = list(zone_con_cam.keys())
    tabs = st.tabs([f"{ZONE_LABELS[z].split()[0]} {z}" for z in zone_tabs])
    cb = int(datetime.now().timestamp() // 300)

    for tab, zona in zip(tabs, zone_tabs):
        with tab:
            cams = zone_con_cam[zona]
            for i in range(0, len(cams), 3):
                cols = st.columns(3)
                for j, cam in enumerate(cams[i:i + 3]):
                    t_str = f" · {cam['temp']:.1f}°C" if cam.get("temp") is not None else ""
                    with cols[j]:
                        st.markdown(f"""
                        <div class="wcam-card">
                            <a href="{cam['url']}" target="_blank">
                                <img src="{cache_bust(cam['url'], cb)}" class="wcam-img" alt="{cam['nome']}"
                                     onerror="this.src='';this.style.minHeight='80px'">
                            </a>
                            <div class="wcam-card-title">{cam['nome']}{t_str}</div>
                        </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ESPORTA GALLERY (foto congelate al momento dell'export)
# ═══════════════════════════════════════════════════════════════════════════════
if zone_con_cam:
    st.markdown("#### ⬇️ Esporta gallery")

    cams_by_key   = {c["chiave"]: c for c in webcams if c["is_img"]}
    label_to_zona = {ZONE_LABELS.get(z, z): z for z in zone_con_cam}
    OPT_ALL, OPT_ONE = "🌍 Tutte le sezioni", "📷 Una sola webcam"
    scope_opts = [OPT_ALL] + list(label_to_zona) + [OPT_ONE]

    e1, e2, e3 = st.columns([2, 1, 1])
    with e1:
        scope = st.selectbox("Cosa esportare", scope_opts, key="gal_scope",
                             help="Tutte le sezioni, una sezione (Centro, Monti, Sud…) oppure una singola webcam.")
        cam_sel = None
        if scope == OPT_ONE:
            cam_sel = st.selectbox("Webcam", list(cams_by_key), key="gal_cam",
                                   format_func=lambda k: cams_by_key[k]["nome"])
    with e2:
        freeze = st.checkbox("📸 Congela foto", value=True, key="gal_freeze",
                             help="Scarica le immagini ADESSO e le incorpora nel file: diventa una "
                                  "fotografia fissa di questo momento, anche riaprendola domani.")
    with e3:
        st.write("")
        prepara = st.button("🛠️ Prepara file", key="gal_prep", width="stretch")

    if prepara:
        if scope == OPT_ALL:
            sub, suffix, titolo = zone_con_cam, "tutte", "Gallery Webcam"
        elif scope == OPT_ONE:
            cam = cams_by_key[cam_sel]
            sub, suffix, titolo = {cam["zone"][0]: [cam]}, cam_sel, f"Webcam · {cam['nome']}"
        else:
            z = label_to_zona[scope]
            sub, suffix, titolo = {z: zone_con_cam[z]}, z.lower(), f"Gallery Webcam · {z}"

        with st.spinner("Scarico e congelo le immagini…" if freeze else "Genero la gallery…"):
            html_export = genera_html_gallery(sub, int(datetime.now().timestamp() // 300),
                                              freeze=freeze, titolo=titolo)
        st.session_state["gal_html"]  = html_export
        st.session_state["gal_fname"] = f"gallery_{suffix}_{datetime.now():%Y%m%d_%H%M}.html"
        st.session_state["gal_meta"]  = f"{scope if scope != OPT_ONE else titolo} · {'congelata' if freeze else 'live'}"

    if st.session_state.get("gal_html"):
        st.success(f"Pronta: {st.session_state.get('gal_meta', '')}")
        st.download_button(
            label="⬇️ Scarica HTML gallery",
            data=st.session_state["gal_html"].encode("utf-8"),
            file_name=st.session_state["gal_fname"],
            mime="text/html",
            help="File HTML autonomo: foto cliccabili, grandi e nitide (lightbox).",
        )

st.markdown("---")

# ─── METRICHE ────────────────────────────────────────────────────────────────
ok_d = [d for d in dati if d.get("ok") and d.get("temp") is not None]
if ok_d:
    cold = min(ok_d, key=lambda x: x["temp"])
    hot  = max(ok_d, key=lambda x: x["temp"])
    mn   = min((d for d in ok_d if d.get("tmin") is not None), key=lambda x: x["tmin"])
    mx   = max((d for d in ok_d if d.get("tmax") is not None), key=lambda x: x["tmax"])
    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, loc, color in [
        (c1, "Più Freddo",     f"{cold['temp']:.1f}°C", cold['nome'], "#0ea5e9"),
        (c2, "Più Caldo",      f"{hot['temp']:.1f}°C",  hot['nome'],  "#ea580c"),
        (c3, "Minima + Bassa", f"{mn['tmin']:.1f}°C",   mn['nome'],   "#2563eb"),
        (c4, "Massima + Alta", f"{mx['tmax']:.1f}°C",   mx['nome'],   "#dc2626"),
    ]:
        with col:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color}">{val}</div>
                <div class="metric-loc">{loc}</div>
            </div>""", unsafe_allow_html=True)

# ─── TABELLA ─────────────────────────────────────────────────────────────────
links = {k: c["url"] for k, c in webcam_cfg.items()}
rows = ""
for zona in ZONE_ORDER:
    zona_dati = [d for d in dati if d.get("zona") == zona]
    if not zona_dati:
        continue
    rows += f'<tr class="sep"><td colspan="10">{ZONE_LABELS[zona]}</td></tr>'
    for d in zona_dati:
        if not d.get("ok"):
            rows += (f'<tr><td class="nome">{d["nome"]}</td>'
                     f'<td colspan="9" style="color:#ef4444;background:white">Errore</td></tr>')
            continue
        t = d["temp"]; fe = d["feels"]
        url = links.get(d["chiave"])
        nome_cell = f'<a href="{url}" target="_blank" rel="noopener">{d["nome"]}</a>' if url else d["nome"]
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

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""<div class="note-footer">
Dati attuali: Open-Meteo Forecast (ECMWF IFS) · Cache 15 min<br>
🖼️ immagine diretta · 🌐 pagina webcam · Gallery aggiornata ogni 5 min
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
if st.button("🔄 Aggiorna ora"):
    fetch_current.clear()
    st.rerun()
