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
"""

import streamlit as st
import os, re
from datetime import datetime, date, timedelta
import calendar

# ─────────────────────────────────────────────────────────────────────────────
# COSTANTI
# ─────────────────────────────────────────────────────────────────────────────
BOLLETTINI_DIR = os.path.join(os.getcwd(), "bollettini")
IFRAME_HEIGHT   = 920

# ─────────────────────────────────────────────────────────────────────────────
# CSS — iniettato una volta sola
# ─────────────────────────────────────────────────────────────────────────────
NAV_CSS = """
<style>
/* ── Navigator ── */
.bnav {
    display: flex;
    align-items: center;
    gap: 0;
    background: #f4f2ed;
    border: 1px solid #ccc8be;
    border-radius: 10px;
    overflow: hidden;
    height: 48px;
    font-family: monospace;
}
.bnav-btn {
    width: 40px; height: 48px;
    border: none; background: transparent;
    color: #444; font-size: 16px;
    cursor: pointer; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    transition: background .15s;
}
.bnav-btn:hover { background: #e8e4da; }
.bnav-btn:disabled { color: #bbb; cursor: default; }
.bnav-divider {
    width: 1px; height: 30px;
    background: #ccc8be; flex-shrink: 0;
}
.bnav-date-pill {
    padding: 0 14px; flex-shrink: 0;
    font-size: 0.8rem; font-weight: 600;
    color: #185FA5; white-space: nowrap;
    display: flex; align-items: center; gap: 6px;
}
.bnav-title {
    flex: 1; min-width: 0;
    padding: 0 12px;
    font-size: 0.75rem; color: #444;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    font-family: monospace;
}
.bnav-counter {
    padding: 0 12px; flex-shrink: 0;
    font-size: 0.68rem; color: #999;
    white-space: nowrap;
}
.bnav-size {
    padding: 0 10px 0 0; flex-shrink: 0;
    font-size: 0.65rem; color: #bbb; white-space: nowrap;
}

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

/* ── Mini calendar popup ── */
.bcal-btn {
    padding: 4px 12px; border-radius: 20px;
    border: 1px solid #ccc8be; background: #f4f2ed;
    font-family: monospace; font-size: 0.7rem; font-weight: 600;
    letter-spacing: 0.06em; color: #666; cursor: pointer;
    display: flex; align-items: center; gap: 5px;
    transition: all .15s;
}
.bcal-btn:hover { border-color: #999; color: #333; }

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

/* ── Tag pills ── */
.btag { display:inline-block; font-family:monospace; font-size:0.6rem;
        font-weight:600; letter-spacing:0.05em; text-transform:uppercase;
        padding:1px 7px; border-radius:10px; }
.btag-meteo { background:#E6F1FB; color:#0C447C; }
.btag-neve  { background:#E1F5EE; color:#085041; }
.btag-eu    { background:#FAEEDA; color:#633806; }
.btag-best  { background:#EAF3DE; color:#27500A; }

/* ── Date indicator dots in calendar ── */
.bdot { width:6px; height:6px; border-radius:50%; background:#185FA5;
        display:inline-block; margin:1px; }
</style>
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


def scan_bollettini(root: str) -> dict:
    """
    Returns:
      {
        "METEO": [ {fname, full_path, pdf_path, date, date_label, title, size_html, size_pdf}, ... ],
        "NEVE":  [ ... ],
        ...
      }
    Sorted by date DESC within each category.
    Order of categories: METEO first, NEVE second, then alphabetical.
    """
    result: dict[str, list] = {}

    if not os.path.isdir(root):
        return result

    # Subcategory folders
    subdirs = sorted(
        [d for d in os.listdir(root)
         if os.path.isdir(os.path.join(root, d))],
    )
    # Put METEO first, NEVE second
    def cat_order(d):
        dl = d.lower()
        if dl.startswith("meteo"):   return (0, d)
        if dl.startswith("neve") or dl.startswith("ski"): return (1, d)
        return (2, d)
    subdirs = sorted(subdirs, key=cat_order)

    for subdir in subdirs:
        cat_label = subdir.upper()
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

    # Also pick up HTML files directly in root (no subdir)
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
        # Deduplicate by full_path
        seen = set()
        deduped = []
        for doc in combined:
            if doc["full_path"] not in seen:
                seen.add(doc["full_path"])
                deduped.append(doc)
        result["METEO"] = deduped

    return result


def inject_viewer_css(html: str, is_dark: bool = False) -> str:
    """Inject responsive CSS for iframe viewing. Force light bg for dark docs."""
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
/* Force light background for dark-theme bollettini */
body { background:#f7f6f2!important; color:#1a1a1a!important; }
.hero, [class*="hero"] { background:linear-gradient(135deg,#ddeef5,#e4eff8)!important; }
</style>"""
    tag = "</head>" if "</head>" in html else "<body>"
    return html.replace(tag, overrides + "\n" + tag, 1)


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

    categories = list(catalog.keys())   # already ordered: METEO, NEVE, ...

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

    cat   = ss.bnav_cat
    docs  = catalog[cat]
    idx   = min(ss.bnav_idx, len(docs) - 1)
    total = len(docs)
    doc   = docs[idx]

    # ── Header ────────────────────────────────────────────────────────────────
    st.subheader("📄 Bollettino Meteo")

    # ── Category tabs (one line) ───────────────────────────────────────────────
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

    # Calendar toggle in same row
    cal_label = "📅 Data" if not ss.show_cal else "✕ Chiudi"
    if cat_cols[len(categories)].button(cal_label, key="bcal_toggle", use_container_width=True):
        ss.show_cal = not ss.show_cal
        st.rerun()

    st.divider()

    # ── Mini calendar popup ────────────────────────────────────────────────────
    if ss.show_cal:
        all_dates = sorted(
            {doc2["date"] for doc2 in docs if doc2["date"]},
            reverse=True,
        )
        if all_dates:
            # Month to show: current doc's date or latest
            ref_date = doc["date"] or all_dates[0]
            cal_year, cal_month = ref_date.year, ref_date.month

            prev_m_col, title_col, next_m_col = st.columns([1, 4, 1])
            prev_m = date(cal_year - (cal_month == 1), 12 if cal_month == 1 else cal_month - 1, 1)
            next_m = date(cal_year + (cal_month == 12), 1 if cal_month == 12 else cal_month + 1, 1)

            MONTHS_IT = ["","Gen","Feb","Mar","Apr","Mag","Giu",
                         "Lug","Ago","Set","Ott","Nov","Dic"]
            title_col.markdown(
                f"<div style='text-align:center;font-family:monospace;font-weight:600;"
                f"font-size:0.8rem;padding:4px 0;'>"
                f"{MONTHS_IT[cal_month]} {cal_year}</div>",
                unsafe_allow_html=True,
            )
            if prev_m_col.button("←", key="bcal_prev_m"):
                pass   # month navigation would need more state; simplified here

            # Date buttons — only dates that have docs
            doc_dates_set = set(all_dates)
            cal_matrix = calendar.monthcalendar(cal_year, cal_month)
            for week in cal_matrix:
                day_cols = st.columns(7)
                for wi, day_num in enumerate(week):
                    if day_num == 0:
                        continue
                    d_obj = date(cal_year, cal_month, day_num)
                    has_doc = d_obj in doc_dates_set
                    label = f"**{day_num}**" if has_doc else str(day_num)
                    is_cur = (d_obj == doc.get("date"))
                    btn_type = "primary" if is_cur else "secondary"
                    if has_doc:
                        if day_cols[wi].button(
                            str(day_num), key=f"bcal_{d_obj}",
                            type=btn_type,
                            help=d_obj.strftime("%-d %b %Y"),
                        ):
                            # Jump to first doc of that date in current category
                            for j, doc2 in enumerate(docs):
                                if doc2["date"] == d_obj:
                                    ss.bnav_idx = j
                                    ss.show_cal = False
                                    st.rerun()
                    else:
                        day_cols[wi].markdown(
                            f"<div style='text-align:center;color:#ccc;"
                            f"font-size:0.75rem;padding:4px 0;'>{day_num}</div>",
                            unsafe_allow_html=True,
                        )

        st.divider()

    # ── Single-row navigator ───────────────────────────────────────────────────
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
        # Central info strip
        tag_cls = _tag_for_category(cat)
        same_day_docs = [d2 for d2 in docs if d2["date"] == doc["date"]] if doc["date"] else [doc]
        edition_info = f" · edizione {same_day_docs.index(doc)+1}/{len(same_day_docs)}" if len(same_day_docs) > 1 else ""
        st.markdown(
            f"<div style='background:#f4f2ed;border:1px solid #ccc8be;border-radius:8px;"
            f"padding:8px 14px;display:flex;align-items:center;gap:10px;height:38px;"
            f"font-family:monospace;overflow:hidden;'>"
            f"<span style='font-weight:700;color:#185FA5;white-space:nowrap;font-size:0.82rem;'>"
            f"{doc['date_label']}</span>"
            f"<span style='color:#ccc;'>|</span>"
            f"<span style='color:#555;font-size:0.72rem;white-space:nowrap;overflow:hidden;"
            f"text-overflow:ellipsis;flex:1;'>{doc['title']}{edition_info}</span>"
            f"<span style='color:#bbb;font-size:0.62rem;white-space:nowrap;'>"
            f"HTML {doc['size_html']}"
            f"{(' · PDF ' + doc['size_pdf']) if doc['pdf_path'] else ''}"
            f"</span>"
            f"<span style='color:#aaa;font-size:0.62rem;white-space:nowrap;'>{idx+1}/{total}</span>"
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
            is_active = (ed["fname"] == doc["fname"])
            label = ed["title"] or ed["fname"]
            btn_style = "primary" if is_active else "secondary"
            if ed_cols[ei % 6].button(
                label[:30],
                key=f"bedition_{ei}",
                type=btn_style,
                use_container_width=True,
                help=f"{ed['size_html']}",
            ):
                ss.bnav_idx = docs.index(ed)
                st.rerun()

    # ── Download strip ─────────────────────────────────────────────────────────
    dl_cols = st.columns([2, 2, 6])
    try:
        with open(doc["full_path"], "rb") as f:
            html_bytes = f.read()
        with dl_cols[0]:
            st.download_button(
                label=f"⬇ HTML  {doc['size_html']}",
                data=html_bytes,
                file_name=doc["fname"],
                mime="text/html",
                use_container_width=True,
            )
    except Exception:
        pass

    if doc["pdf_path"]:
        try:
            with open(doc["pdf_path"], "rb") as f:
                pdf_bytes = f.read()
            pdf_fname = re.sub(r"\.html$", ".pdf", doc["fname"], flags=re.I)
            with dl_cols[1]:
                st.download_button(
                    label=f"⬇ PDF  {doc['size_pdf']}",
                    data=pdf_bytes,
                    file_name=pdf_fname,
                    mime="application/pdf",
                    use_container_width=True,
                )
        except Exception:
            pass

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