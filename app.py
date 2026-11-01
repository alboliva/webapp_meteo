"""
app.py — punto d'ingresso (router).

Le pagine stanno in views/. Il menu laterale mostra solo le pagine pubbliche:
la pagina di amministrazione è registrata ma NON compare nel menu ed è
raggiungibile solo digitando l'indirizzo:  https://<tua-app>.streamlit.app/nimda
"""

import streamlit as st

st.set_page_config(
    page_title="Meteo Rismi",
    layout="wide",
    page_icon="🌤️",
    initial_sidebar_state="expanded",
)

P_BOLL  = st.Page("views/bollettini_nav.py",  title="Bollettini",      icon="📄", default=True)
P_DASH  = st.Page("views/dashboard.py",       title="Dashboard",       icon="🌡️", url_path="dashboard")
P_PREV  = st.Page("views/previsioni_roma.py", title="Previsioni Roma", icon="🌦️", url_path="previsioni_roma")
P_MAPPE = st.Page("views/mappe.py",           title="Mappe",           icon="🗺️", url_path="mappe")
P_ADMIN = st.Page("views/admin.py",           title="Amministrazione", icon="🔒", url_path="nimda")

PUBBLICHE = [P_BOLL, P_DASH, P_PREV, P_MAPPE]

# position="hidden": il menu automatico non viene disegnato; costruiamo il nostro
# con le sole pagine pubbliche, così /nimda resta "non mappata".
nav = st.navigation(PUBBLICHE + [P_ADMIN], position="hidden")

with st.sidebar:
    for p in PUBBLICHE:
        st.page_link(p)

nav.run()
