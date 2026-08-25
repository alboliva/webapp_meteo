"""
Bollettino Navigator — navigatore bollettini meteo per Streamlit.

Struttura cartella bollettini/ attesa:
  bollettini/
    meteo/          → etichetta "METEO"
    neve/           → etichetta "NEVE"
    europa/         → etichetta "EUROPA"
    <qualsiasi>/    → etichetta in MAIUSCOLO dal nome cartella

Naming file: YYYYMMDD_<qualsiasi>.html  (es. 20260423_bollettino.html)
File PDF opzionale: stesso nome, estensione .pdf  (es. 20260423_bollettino.pdf)

Novità:
  • Condivisione con URL statico: ?bollettino=<categoria>/<file>.html
    apre direttamente quel bollettino (deep link).
  • Modalità schermo intero, con pulsante "Condividi" che copia il link
    negli appunti e pulsante fullscreen reale (Fullscreen API) dentro l'iframe.
"""

import streamlit as st
import os, re, json
from datetime import datetime, date
import calendar
from urllib.parse import quote, unquote

# ─────────────────────────────────────────────────────────────────────────────
# COSTANTI
# ─────────────────────────────────────────────────────────────────────────────
BOLLETTINI_DIR = os.path.join(os.getcwd(), "bollettini")
IFRAME_HEIGHT   = 920

# ─────────────────────────────────────────────────────────────────────────────
# CSS GLOBALE
# ─────────────────────────────────────────────────────────────────────────────
NAV_CSS = """
<style>
/* ── Category tabs ── */
.bcat-wrap { display:flex; gap:4px; margin-bottom:8px; flex-wrap:wrap; }
.bcat {
    padding: 4px 14px; border-radius: 20px; border: 1px solid #ccc8be;
    background: #f4f2ed; font-family: monospace; font-size: 0.7rem;
    font-weight: 600; letter-spacing: 0.06em; color: #666;
    cursor: pointer; transition: all .15s; white-space: nowrap;
}
.bcat:hover  { border-color: #999; color: #333; background: #ede9e2; }
.bcat.active { background: #185FA5; border-color: #185FA5; color: #fff; }

/* ── Edition selector ── */
.bedition-wrap { display:flex; gap:4px; flex-wrap:wrap; margin-top:4px; }
.bedition {
    padding: 3px 10px; border-radius: 14px;
    border: 1px solid #d4d0c4; background: #fff;
    font-family: monospace; font-size: 0.65rem; color: #555;
    cursor: pointer; transition: all .15s; white-space: nowrap;
}
.bedition:hover  { border-color: #888; color: #1a1a1a; }
.bedition.active { background: #E6F1FB; border-color: #185FA5; color: #0C447C; font-weight:600; }

/* ── Info strip ── */
.binfo-strip {
    background: #f4f2ed;
    border: 1px solid #ccc8be;
    border-radius: 8px;
    padding: 8px 14px;
    display: flex;
    align-items: center;
    gap: 10px;
    height: 38px;
    font-family: monospace;
    overflow: hidden;
}
.binfo-date  { font-weight:700; color:#185FA5; white-space:nowrap; font-size:0.82rem; }
.binfo-sep   { color:#ccc; }
.binfo-title { color:#555; font-size:0.72rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; flex:1; }
.binfo-size  { color:#bbb; font-size:0.62rem; white-space:nowrap; }
.binfo-count { color:#aaa; font-size:0.62rem; white-space:nowrap; }

/* ── Calendario ── */
.bcal-container {
    background: #fff;
    border: 1px solid #e0ddd5;
    border-radius: 12px;
    padding: 16px 20px 12px;
    max-width: 520px;
    margin-bottom: 4px;
}
.bcal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
}
.bcal-month-label {
    font-family: monospace;
    font-size: 0.85rem;
    font-weight: 600;
    color: #1a1a1a;
    letter-spacing: 0.03em;
}
.bcal-weekdays {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    margin-bottom: 6px;
    gap: 3px;
}
.bcal-weekdays span {
    text-align: center;
    font-family: monospace;
    font-size: 0.62rem;
    font-weight: 600;
    color: #aaa;
    letter-spacing: 0.08em;
    padding: 4px 0;
}
.bcal-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 3px;
}
.bcal-cell {
    aspect-ratio: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    font-family: monospace;
    font-size: 0.72rem;
    position: relative;
    cursor: default;
    color: #ccc;
}
.bcal-cell.has-doc {
    background: #f4f2ed;
    border: 1px solid #ddd9ce;
    color: #1a1a1a;
    font-weight: 600;
    cursor: pointer;
    transition: background .12s, border-color .12s, color .12s;
}
.bcal-cell.has-doc:hover {
    background: #E6F1FB;
    border-color: #85B7EB;
    color: #0C447C;
}
.bcal-cell.active {
    background: #185FA5 !important;
    border-color: #185FA5 !important;
    color: #fff !important;
}
.bcal-cell .bcal-dot {
    position: absolute;
    bottom: 4px;
    left: 50%;
    transform: translateX(-50%);
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: #185FA5;
}
.bcal-cell.active .bcal-dot {
    background: rgba(255,255,255,0.6);
}
.bcal-legend {
    display: flex;
    align-items: center;
    gap: 7px;
    margin-top: 12px;
    padding-top: 10px;
    border-top: 1px solid #ede9e2;
    font-family: monospace;
    font-size: 0.62rem;
    color: #aaa;
}
.bcal-legend-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #185FA5;
    flex-shrink: 0;
}
</style>
"""

MONTHS_IT = ["", "Gen", "Feb", "Mar", "Apr", "Mag", "Giu",
             "Lug", "Ago", "Set", "Ott", "Nov", "Dic"]
MONTHS_IT_FULL = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
                  "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
WEEKDAYS = ["L", "M", "M", "G", "V", "S", "D"]

# Pulsante "schermo intero" (Fullscreen API) iniettato dentro il bollettino.
# Prova il fullscreen reale del browser; se il contesto non lo permette,
# avvisa l'utente (la modalità schermo intero di Streamlit resta comunque attiva).
FS_BUTTON = """
<div style="position:fixed;top:12px;right:18px;z-index:99999;">
  <button onclick="(function(){var e=document.documentElement;if(!document.fullscreenElement){if(e.requestFullscreen){e.requestFullscreen().catch(function(){alert('Schermo intero del browser non disponibile in questo riquadro: premi F11 per la modalita a tutto schermo.');});}else{alert('Premi F11 per la modalita a tutto schermo.');}}else{document.exitFullscreen();}})()"
    style="font-family:system-ui,sans-serif;font-size:0.78rem;font-weight:700;padding:8px 14px;border:none;border-radius:10px;background:#0f172a;color:#fff;cursor:pointer;box-shadow:0 4px 14px rgba(0,0,0,.25);">
    ⛶ Schermo intero
  </button>
</div>
"""


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _fmt_size(path: str) -> str:
    try:
        b = os.path.getsize(path)
        if b >= 1_048_576:
            return f"{b/1_048_576:.1f} MB"
        return f"{b/1024:.0f} KB"
    except Exception:
        return ""


def _parse_date(fname: str) -> date | None:
    m = re.match(r"(\d{4})(\d{2})(\d{2})", fname)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass
    return None


def _human_title(fname: str) -> str:
    base = re.sub(r"\.html$", "", fname, flags=re.I)
    base = re.sub(r"^\d{8}_?", "", base)
    base = re.sub(r"[_\-]+", " ", base).strip()
    return base.title() if base else fname


def _tag_for_category(cat: str) -> str:
    c = cat.lower()
    if "neve" in c or "ski" in c or "snow" in c:
        return "neve"
    if "eu" in c or "europa" in c:
        return "eu"
    return "meteo"


def _bollettino_id(full_path: str) -> str:
    """ID stabile e leggibile del bollettino: percorso relativo a bollettini/."""
    rel = os.path.relpath(full_path, BOLLETTINI_DIR)
    return rel.replace(os.sep, "/")


def _base_url() -> str:
    """Prova a ricostruire l'URL base del sito dagli header (se disponibili)."""
    try:
        h = st.context.headers
        host = h.get("Host") or h.get("host")
        proto = h.get("X-Forwarded-Proto") or h.get("x-forwarded-proto")
        if host:
            if not proto:
                proto = "http" if host.split(":")[0] in ("localhost", "127.0.0.1") else "https"
            return f"{proto}://{host}"
    except Exception:
        pass
    return ""


def inject_fs_button(html: str) -> str:
    if "</body>" in html:
        return html.replace("</body>", FS_BUTTON + "</body>", 1)
    return html + FS_BUTTON


def _share_button_component(url: str) -> str:
    """Pulsante 'Condividi' renderizzato dentro il componente HTML: il click è
    un gesto utente dentro l'iframe, quindi la copia negli appunti funziona
    anche con l'app pubblicata online. Fallback: execCommand e poi prompt()."""
    u = json.dumps(url)
    return f"""
    <style>
      html, body {{ margin:0; padding:0; }}
      .shbtn {{
        width:100%; height:40px; cursor:pointer; box-sizing:border-box;
        background:#ffffff; color:#31333F;
        border:1px solid rgba(49,51,63,0.20); border-radius:0.5rem;
        font-family:"Source Sans Pro", system-ui, sans-serif;
        font-size:0.95rem; font-weight:400;
        display:flex; align-items:center; justify-content:center; gap:6px;
        transition:border-color .15s, color .15s;
      }}
      .shbtn:hover {{ border-color:#FF4B4B; color:#FF4B4B; }}
      .shbtn.ok {{ border-color:#16a34a; color:#16a34a; }}
    </style>
    <button class="shbtn" id="shbtn">🔗 Condividi bollettino</button>
    <script>
    (function(){{
      const url = {u};
      const btn = document.getElementById('shbtn');
      function flash(txt){{
        const old = btn.innerHTML;
        btn.innerHTML = txt; btn.classList.add('ok');
        setTimeout(function(){{ btn.innerHTML = old; btn.classList.remove('ok'); }}, 1800);
      }}
      function legacy(){{
        try {{
          const ta = document.createElement('textarea');
          ta.value = url; ta.style.position='fixed'; ta.style.opacity='0';
          document.body.appendChild(ta); ta.focus(); ta.select();
          const ok = document.execCommand('copy'); document.body.removeChild(ta);
          if (ok) flash('✓ Copiato!'); else window.prompt('Copia il link (Cmd/Ctrl+C):', url);
        }} catch(e) {{ window.prompt('Copia il link (Cmd/Ctrl+C):', url); }}
      }}
      btn.addEventListener('click', function(){{
        if (navigator.clipboard && navigator.clipboard.writeText) {{
          navigator.clipboard.writeText(url).then(function(){{ flash('✓ Copiato!'); }}).catch(legacy);
        }} else {{ legacy(); }}
      }});
    }})();
    </script>
    """


def scan_bollettini(root: str) -> dict:
    result: dict[str, list] = {}

    if not os.path.isdir(root):
        return result

    subdirs = sorted(
        [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))],
    )

    def cat_order(d):
        dl = d.lower()
        if dl.startswith("meteo"):                    return (0, d)
        if dl.startswith("neve") or dl.startswith("ski"): return (1, d)
        return (2, d)
    subdirs = sorted(subdirs, key=cat_order)

    for subdir in subdirs:
        cat_label  = subdir.upper()
        subdir_path = os.path.join(root, subdir)
        files = sorted(
            [f for f in os.listdir(subdir_path) if f.lower().endswith(".html")],
            reverse=True,
        )
        docs = []
        for fname in files:
            full_path = os.path.join(subdir_path, fname)
            d = _parse_date(fname)
            pdf_fname = re.sub(r"\.html$", ".pdf", fname, flags=re.I)
            pdf_path  = os.path.join(subdir_path, pdf_fname)
            pdf_path  = pdf_path if os.path.isfile(pdf_path) else None
            docs.append(dict(
                fname      = fname,
                full_path  = full_path,
                pdf_path   = pdf_path,
                date       = d,
                date_label = d.strftime("%-d %b %Y") if d else "—",
                title      = _human_title(fname),
                size_html  = _fmt_size(full_path),
                size_pdf   = _fmt_size(pdf_path) if pdf_path else None,
                category   = cat_label,
            ))
        if docs:
            result[cat_label] = docs

    root_files = sorted(
        [f for f in os.listdir(root) if f.lower().endswith(".html")],
        reverse=True,
    )
    if root_files:
        docs = []
        for fname in root_files:
            full_path = os.path.join(root, fname)
            d = _parse_date(fname)
            pdf_path  = re.sub(r"\.html$", ".pdf", full_path, flags=re.I)
            pdf_path  = pdf_path if os.path.isfile(pdf_path) else None
            docs.append(dict(
                fname      = fname,
                full_path  = full_path,
                pdf_path   = pdf_path,
                date       = d,
                date_label = d.strftime("%-d %b %Y") if d else "—",
                title      = _human_title(fname),
                size_html  = _fmt_size(full_path),
                size_pdf   = _fmt_size(pdf_path) if pdf_path else None,
                category   = "METEO",
            ))
        existing = result.get("METEO", [])
        combined = sorted(existing + docs, key=lambda x: x["fname"], reverse=True)
        seen, deduped = set(), []
        for doc in combined:
            if doc["full_path"] not in seen:
                seen.add(doc["full_path"])
                deduped.append(doc)
        result["METEO"] = deduped

    return result


def inject_viewer_css(html: str, is_dark: bool = False) -> str:
    overrides = """
<style>
body  { max-width:100%!important; padding:16px 24px!important;
        font-size:0.92rem; box-sizing:border-box; }
img   { max-width:100%!important; height:auto!important; }
table { width:100%!important; font-size:0.83rem; }
.two-col   { display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; }
.three-col { display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; }
.island-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; }
@media(max-width:860px){
  .two-col,.three-col,.island-grid { grid-template-columns:1fr!important; }
}
</style>"""
    if is_dark:
        overrides += """
<style>
body { background:#f7f6f2!important; color:#1a1a1a!important; }
.hero, [class*="hero"] { background:linear-gradient(135deg,#ddeef5,#e4eff8)!important; }
</style>"""
    tag = "</head>" if "</head>" in html else "<body>"
    return html.replace(tag, overrides + "\n" + tag, 1)


# ─────────────────────────────────────────────────────────────────────────────
# CALENDARIO
# ─────────────────────────────────────────────────────────────────────────────

def render_calendar(docs: list, current_doc: dict, cal_year: int, cal_month: int) -> tuple[int | None, int | None]:
    """
    Renders the redesigned calendar.
    Returns (new_idx, None) if a date button was clicked, else (None, None).
    Also returns (None, 'prev') or (None, 'next') for month navigation.
    """
    doc_dates_set = {doc2["date"] for doc2 in docs if doc2["date"]}

    # ── Month navigation header ──────────────────────────────────────────────
    col_prev, col_title, col_today, col_next = st.columns([1, 5, 2, 1])

    with col_prev:
        prev_clicked = st.button("←", key="bcal_prev_m", use_container_width=True)
    with col_title:
        st.markdown(
            f"<div style='text-align:center;font-family:monospace;font-weight:600;"
            f"font-size:0.88rem;padding:6px 0;color:#1a1a1a;letter-spacing:0.03em;'>"
            f"{MONTHS_IT_FULL[cal_month]} {cal_year}</div>",
            unsafe_allow_html=True,
        )
    with col_today:
        today_clicked = st.button("oggi", key="bcal_today", use_container_width=True)
    with col_next:
        next_clicked = st.button("→", key="bcal_next_m", use_container_width=True)

    if prev_clicked:
        return None, "prev"
    if next_clicked:
        return None, "next"
    if today_clicked:
        return None, "today"

    # ── Weekday headers ──────────────────────────────────────────────────────
    wd_cols = st.columns(7)
    for i, wd in enumerate(WEEKDAYS):
        wd_cols[i].markdown(
            f"<div style='text-align:center;font-family:monospace;font-size:0.62rem;"
            f"font-weight:600;color:#bbb;letter-spacing:0.08em;padding:2px 0;'>{wd}</div>",
            unsafe_allow_html=True,
        )

    # ── Calendar grid ────────────────────────────────────────────────────────
    first_weekday = date(cal_year, cal_month, 1).weekday()  # 0=Mon
    days_in_month = calendar.monthrange(cal_year, cal_month)[1]

    cells: list[date | None] = [None] * first_weekday
    for d in range(1, days_in_month + 1):
        cells.append(date(cal_year, cal_month, d))
    while len(cells) % 7 != 0:
        cells.append(None)

    today = date.today()
    clicked_idx = None

    for row_start in range(0, len(cells), 7):
        week = cells[row_start:row_start + 7]
        cols = st.columns(7)
        for ci, day_date in enumerate(week):
            with cols[ci]:
                if day_date is None:
                    st.markdown(
                        "<div style='aspect-ratio:1;display:flex;align-items:center;"
                        "justify-content:center;'></div>",
                        unsafe_allow_html=True,
                    )
                    continue

                has_doc  = day_date in doc_dates_set
                is_active = (current_doc.get("date") == day_date)
                is_today  = (day_date == today)

                if has_doc:
                    btn_style = "primary" if is_active else "secondary"
                    label = f"**{day_date.day}**"
                    if st.button(
                        label,
                        key=f"bcal_day_{day_date}",
                        type=btn_style,
                        use_container_width=True,
                        help=day_date.strftime("%-d %b %Y"),
                    ):
                        for j, doc2 in enumerate(docs):
                            if doc2["date"] == day_date:
                                clicked_idx = j
                                break
                else:
                    color = "#bbb" if is_today else "#d5d2ca"
                    weight = "600" if is_today else "400"
                    border = "1px solid #ccc" if is_today else "none"
                    st.markdown(
                        f"<div style='text-align:center;font-family:monospace;"
                        f"font-size:0.72rem;font-weight:{weight};color:{color};"
                        f"padding:6px 0;border-radius:8px;border:{border};'>"
                        f"{day_date.day}</div>",
                        unsafe_allow_html=True,
                    )

    st.markdown(
        "<div style='display:flex;align-items:center;gap:7px;margin-top:8px;"
        "padding-top:8px;border-top:1px solid #ede9e2;font-family:monospace;"
        "font-size:0.62rem;color:#aaa;'>"
        "<span style='width:8px;height:8px;border-radius:50%;background:#185FA5;"
        "flex-shrink:0;display:inline-block;'></span>"
        "Bollettino disponibile</div>",
        unsafe_allow_html=True,
    )

    return clicked_idx, None


# ─────────────────────────────────────────────────────────────────────────────
# MODALITÀ SCHERMO INTERO
# ─────────────────────────────────────────────────────────────────────────────

def render_fullscreen(doc: dict, cat: str):
    """Modalità schermo intero: nasconde sidebar/header e mostra il bollettino
    a tutta larghezza. Pulsante per uscire + pulsante fullscreen reale (Fullscreen
    API) dentro l'iframe del bollettino."""
    st.markdown("""
    <style>
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"],
    header { display: none !important; }
    .block-container { padding: 0.6rem 1.2rem 0 1.2rem !important; max-width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

    top1, top2 = st.columns([6, 1])
    with top1:
        st.markdown(
            f"""<div style="font-family:monospace;font-size:1rem;color:#0f172a;">
                <b>{doc['title']}</b>
                <span style="color:#64748b;font-size:0.8rem;"> &nbsp;·&nbsp; {cat} &nbsp;·&nbsp; {doc['date_label']}</span>
            </div>""",
            unsafe_allow_html=True,
        )
    with top2:
        if st.button("✕ Esci", key="bnav_fs_exit", use_container_width=True):
            st.session_state.bnav_fs = False
            st.rerun()

    try:
        with open(doc["full_path"], "r", encoding="utf-8") as f:
            html = f.read()
        is_dark = any(c in html for c in ["#0a1628", "#0d1b2a", "bg-deep:#0"])
        html = inject_viewer_css(html, is_dark=is_dark)
        html = inject_fs_button(html)
        st.components.v1.html(html, height=1500, scrolling=True)
    except Exception as e:
        st.error(f"Errore apertura file: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="Meteo Rismi",
        layout="wide",
        page_icon="🌤️",
        initial_sidebar_state="expanded",
    )

    st.markdown(NAV_CSS, unsafe_allow_html=True)

    # ── Scan ──────────────────────────────────────────────────────────────────
    catalog = scan_bollettini(BOLLETTINI_DIR)

    if not catalog:
        st.subheader("📄 Bollettino Meteo")
        st.info(
            f"Crea la cartella `bollettini/` con sottocartelle `meteo/`, `neve/`, ecc.\n\n"
            f"Path cercato: `{BOLLETTINI_DIR}`"
        )
        return

    categories = list(catalog.keys())

    # ── Session state ─────────────────────────────────────────────────────────
    ss = st.session_state
    if "bnav_cat" not in ss:
        ss.bnav_cat = categories[0]
    if ss.bnav_cat not in catalog:
        ss.bnav_cat = categories[0]
    if "bnav_idx" not in ss:
        ss.bnav_idx = 0
    if "show_cal" not in ss:
        ss.show_cal = False
    if "bnav_fs" not in ss:
        ss.bnav_fs = False
    if "cal_year" not in ss or "cal_month" not in ss:
        today = date.today()
        ss.cal_year  = today.year
        ss.cal_month = today.month

    # ── Deep link: ?bollettino=<categoria>/<file>.html ───────────────────────
    # Apre direttamente il bollettino condiviso (una sola volta per sessione,
    # così l'utente può poi navigare liberamente).
    if "bollettino" in st.query_params and not ss.get("_bnav_deep_done"):
        bid = unquote(st.query_params["bollettino"]).replace("/", os.sep)
        target_full = os.path.normpath(os.path.join(BOLLETTINI_DIR, bid))
        found = None
        for c, docs2 in catalog.items():
            for j, d2 in enumerate(docs2):
                if os.path.normpath(d2["full_path"]) == target_full:
                    found = (c, j)
                    break
            if found:
                break
        if found:
            ss.bnav_cat, ss.bnav_idx = found
        ss["_bnav_deep_done"] = True

    cat   = ss.bnav_cat
    docs  = catalog[cat]
    idx   = min(ss.bnav_idx, len(docs) - 1)
    total = len(docs)
    doc   = docs[idx]

    # Sync calendar to current doc's date on first open
    if doc.get("date"):
        ref = doc["date"]
        if "cal_year" not in ss:
            ss.cal_year  = ref.year
            ss.cal_month = ref.month

    # ── MODALITÀ SCHERMO INTERO ────────────────────────────────────────────────
    if ss.bnav_fs:
        render_fullscreen(doc, cat)
        return

    # ── Header ────────────────────────────────────────────────────────────────
    st.subheader("📄 Bollettino Meteo")

    # ── Category tabs ─────────────────────────────────────────────────────────
    cat_cols = st.columns(len(categories) + 2)
    for i, c in enumerate(categories):
        is_active = (c == cat)
        btn_label = f"{'●' if is_active else '○'} {c}"
        if cat_cols[i].button(
            btn_label,
            key=f"bcat_{c}",
            help=f"{len(catalog[c])} bollettini",
            use_container_width=True,
        ):
            ss.bnav_cat = c
            ss.bnav_idx = 0
            ss.show_cal = False
            st.rerun()

    cal_label = "📅 Data" if not ss.show_cal else "✕ Chiudi"
    if cat_cols[len(categories)].button(cal_label, key="bcal_toggle", use_container_width=True):
        ss.show_cal = not ss.show_cal
        if ss.show_cal and doc.get("date"):
            ss.cal_year  = doc["date"].year
            ss.cal_month = doc["date"].month
        st.rerun()

    st.divider()

    # ── Calendario ────────────────────────────────────────────────────────────
    if ss.show_cal:
        all_dates = sorted({d2["date"] for d2 in docs if d2["date"]}, reverse=True)

        if all_dates:
            new_idx, nav_action = render_calendar(
                docs        = docs,
                current_doc = doc,
                cal_year    = ss.cal_year,
                cal_month   = ss.cal_month,
            )

            if nav_action == "prev":
                if ss.cal_month == 1:
                    ss.cal_year  -= 1
                    ss.cal_month  = 12
                else:
                    ss.cal_month -= 1
                st.rerun()
            elif nav_action == "next":
                if ss.cal_month == 12:
                    ss.cal_year  += 1
                    ss.cal_month  = 1
                else:
                    ss.cal_month += 1
                st.rerun()
            elif nav_action == "today":
                t = date.today()
                ss.cal_year  = t.year
                ss.cal_month = t.month
                st.rerun()
            elif new_idx is not None:
                ss.bnav_idx = new_idx
                ss.show_cal = False
                st.rerun()

        st.divider()

    # ── Navigator row ─────────────────────────────────────────────────────────
    nc1, nc2, nc3, nc4, nc5 = st.columns([1, 1, 6, 1, 1])

    with nc1:
        if st.button("←", key="bnav_prev",
                     disabled=(idx >= total - 1),
                     help="Precedente",
                     use_container_width=True):
            ss.bnav_idx = idx + 1
            st.rerun()

    with nc2:
        if st.button("↑", key="bnav_newest",
                     disabled=(idx == 0),
                     help="Più recente",
                     use_container_width=True):
            ss.bnav_idx = 0
            st.rerun()

    with nc3:
        same_day_docs  = [d2 for d2 in docs if d2["date"] == doc["date"]] if doc["date"] else [doc]
        edition_info   = f" · edizione {same_day_docs.index(doc)+1}/{len(same_day_docs)}" if len(same_day_docs) > 1 else ""
        st.markdown(
            f"<div class='binfo-strip'>"
            f"<span class='binfo-date'>{doc['date_label']}</span>"
            f"<span class='binfo-sep'>|</span>"
            f"<span class='binfo-title'>{doc['title']}{edition_info}</span>"
            f"<span class='binfo-size'>HTML {doc['size_html']}"
            f"{(' · PDF ' + doc['size_pdf']) if doc['pdf_path'] else ''}</span>"
            f"<span class='binfo-count'>{idx+1}/{total}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    with nc4:
        if st.button("↓", key="bnav_oldest",
                     disabled=(idx == total - 1),
                     help="Più vecchio",
                     use_container_width=True):
            ss.bnav_idx = total - 1
            st.rerun()

    with nc5:
        if st.button("→", key="bnav_next",
                     disabled=(idx <= 0),
                     help="Successivo",
                     use_container_width=True):
            ss.bnav_idx = idx - 1
            st.rerun()

    # ── Same-day edition switcher ──────────────────────────────────────────────
    same_day = [d2 for d2 in docs if d2["date"] == doc["date"]] if doc["date"] else []
    if len(same_day) > 1:
        ed_cols = st.columns(min(len(same_day), 6))
        for ei, ed in enumerate(same_day):
            is_active  = (ed["fname"] == doc["fname"])
            label      = ed["title"] or ed["fname"]
            btn_style  = "primary" if is_active else "secondary"
            if ed_cols[ei % 6].button(
                label[:30],
                key=f"bedition_{ei}",
                type=btn_style,
                use_container_width=True,
                help=f"{ed['size_html']}",
            ):
                ss.bnav_idx = docs.index(ed)
                st.rerun()

    # ── Azioni: Scarica HTML · (PDF) · Schermo intero · Condividi ──────────────
    has_pdf = bool(doc["pdf_path"])
    action_cols = st.columns(4 if has_pdf else 3)
    ci = 0

    try:
        with open(doc["full_path"], "rb") as f:
            html_bytes = f.read()
        action_cols[ci].download_button(
            label=f"⬇ HTML  {doc['size_html']}",
            data=html_bytes,
            file_name=doc["fname"],
            mime="text/html",
            use_container_width=True,
        )
    except Exception:
        html_bytes = None
    ci += 1

    if has_pdf:
        try:
            with open(doc["pdf_path"], "rb") as f:
                pdf_bytes = f.read()
            pdf_fname = re.sub(r"\.html$", ".pdf", doc["fname"], flags=re.I)
            action_cols[ci].download_button(
                label=f"⬇ PDF  {doc['size_pdf']}",
                data=pdf_bytes,
                file_name=pdf_fname,
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception:
            pass
        ci += 1

    if action_cols[ci].button("⛶ Schermo intero", key="bnav_fs_btn", use_container_width=True):
        ss.bnav_fs = True
        st.rerun()
    ci += 1

    # Condividi → pulsante (dentro il componente) che copia il link al click.
    # Funziona anche con l'app online, dove la copia automatica sarebbe bloccata.
    bid = _bollettino_id(doc["full_path"])
    base = _base_url()
    share_url = f"{base}/?bollettino={quote(bid)}" if base else f"?bollettino={quote(bid)}"
    with action_cols[ci]:
        st.components.v1.html(_share_button_component(share_url), height=44)

    st.divider()

    # ── Render bollettino ──────────────────────────────────────────────────────
    try:
        with open(doc["full_path"], "r", encoding="utf-8") as f:
            html_content = f.read()

        is_dark = any(c in html_content for c in ["#0a1628", "#0d1b2a", "bg-deep:#0"])
        html_content = inject_viewer_css(html_content, is_dark=is_dark)
        st.components.v1.html(html_content, height=IFRAME_HEIGHT, scrolling=True)

    except Exception as e:
        st.error(f"Errore apertura file: {e}")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()