import streamlit as st
from datetime import datetime, timezone

st.set_page_config(page_title="Mappe Meteo WX Charts", layout="wide")
st.title("Mappe Meteo WX Charts")
st.markdown("### ECMWF Overview - Italia")

# ====================== GENERA DATA ODIERNA ======================
# Usa le 12:00 UTC (come nel tuo esempio originale)
oggi = datetime.now(timezone.utc).replace(
    hour=12, minute=0, second=0, microsecond=0
)

data_str = oggi.strftime("%Y-%m-%dT12:00:00Z")

# Costruisci l'URL diretto dell'immagine
url_immagine = f"https://www.wxcharts.com/api/content/ecmwf_op/italy/overview/{data_str}/{data_str}"

st.caption(f"**Run:** {oggi.strftime('%d %B %Y alle 12:00 UTC')}")

# Mostra l'immagine dinamicamente
st.image(
    url_immagine,
    caption=f"ECMWF Overview Italia - {oggi.strftime('%d %B %Y')}",
    use_container_width=True
)

# Pulsante per aggiornare manualmente
if st.button("🔄 Aggiorna con data e ora attuale"):
    st.rerun()

# ====================== Opzione iframe (se la preferisci) ======================
st.divider()
st.markdown("### Versione Interattiva (Iframe)")

# Versione iframe con data dinamica
iframe_url = f"https://www.wxcharts.com/?dataset=ecmwf_op&region=italy&element=overview&run=12&dtg={data_str.replace(':', '%3A')}"

st.components.v1.iframe(
    iframe_url,
    height=800,
    scrolling=True
)