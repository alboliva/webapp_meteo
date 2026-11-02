"""
app.py — punto d'ingresso (router).

Le pagine stanno in views/. Il menu laterale mostra solo le pagine pubbliche:
la pagina di amministrazione è registrata ma NON compare nel menu ed è
raggiungibile solo digitando l'indirizzo:  https://<tua-app>.streamlit.app/nimda
"""

from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Meteo Rismi",
    layout="wide",
    page_icon="🌤️",
    initial_sidebar_state="expanded",
)

BASE  = Path(__file__).resolve().parent
VIEWS = BASE / "views"

PAGINE = [
    # file                  titolo              icona  url_path           pubblica
    ("bollettini_nav.py",  "Bollettini",       "📄", "bollettini",      True),
    ("dashboard.py",       "Dashboard",        "🌡", "dashboard",       True),
    ("previsioni_roma.py", "Previsioni Roma",  "🌦", "previsioni_roma", True),
    ("mappe.py",           "Mappe",            "🗺", "mappe",           True),
    ("admin.py",           "Amministrazione",  "🔒", "nimda",           False),
]

# ─── Controlli: Streamlit abbastanza recente e file presenti ─────────────────
if not hasattr(st, "Page") or not hasattr(st, "navigation"):
    st.error(
        f"La versione di Streamlit installata ({st.__version__}) è troppo vecchia. "
        "Nel file **requirements.txt** (nella root del repo) scrivi `streamlit>=1.50`, "
        "poi da Streamlit Cloud fai **Reboot app**."
    )
    st.stop()

mancanti = [f"views/{f}" for f, *_ in PAGINE if not (VIEWS / f).is_file()]
if mancanti:
    presenti = sorted(p.name for p in VIEWS.glob("*.py")) if VIEWS.is_dir() else []
    st.error(
        "Mancano questi file nel repo:\n\n"
        + "\n".join(f"- `{m}`" for m in mancanti)
        + f"\n\nCartella `views/` {'trovata' if VIEWS.is_dir() else '**NON trovata**'} in `{BASE}`"
        + (f" — contiene: {', '.join(presenti)}" if presenti else "")
        + "\n\nCarica la cartella **views** (con i 5 file dentro) nella root del repo, "
          "accanto ad `app.py`."
    )
    st.stop()

# ─── Navigazione ─────────────────────────────────────────────────────────────
pagine, pubbliche = [], []
for i, (f, titolo, icona, url, pubblica) in enumerate(PAGINE):
    p = st.Page(VIEWS / f, title=titolo, icon=icona, url_path=url, default=(i == 0))
    pagine.append(p)
    if pubblica:
        pubbliche.append(p)

# position="hidden": niente menu automatico; disegniamo il nostro con le sole
# pagine pubbliche, così /nimda resta "non mappata".
nav = st.navigation(pagine, position="hidden")

with st.sidebar:
    for p in pubbliche:
        st.page_link(p)

nav.run()
