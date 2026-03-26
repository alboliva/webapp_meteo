import streamlit as st
from datetime import datetime, timezone

st.set_page_config(page_title="Mappe Meteo WX Charts", layout="wide")

st.title("Mappe Meteo WX Charts")
st.markdown("### ECMWF Overview - Italia")

# Genera la data di oggi alle 12:00 UTC
oggi = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
data_str = oggi.strftime("%Y-%m-%dT12:00:00Z")

# URL per l'iframe dinamico
dtg_encoded = data_str.replace(":", "%3A")   # : deve diventare %3A nell'URL

iframe_url = (
    f"https://www.wxcharts.com/?dataset=ecmwf_op"
    f"&region=italy"
    f"&element=overview"
    f"&run=12"
    f"&dtg={dtg_encoded}"
)

st.caption(f"**Run ECMWF:** {oggi.strftime('%d %B %Y alle 12:00 UTC')}")

# Mostra l'iframe
st.components.v1.iframe(iframe_url, height=850, scrolling=True)

# Pulsante di aggiornamento
if st.button("🔄 Aggiorna con data odierna (12z)"):
    st.rerun()

st.info("Se la mappa non appare subito, aspetta qualche secondo o clicca su 'Aggiorna'.")