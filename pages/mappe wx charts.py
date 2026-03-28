import streamlit as st
from datetime import datetime, timezone

st.set_page_config(page_title="Mappe Meteo WX Charts", layout="wide")
st.title("🗺️ Mappe Meteo WX Charts")
st.markdown("### ECMWF Overview - Italia")

# Genera data odierna alle 12:00 UTC
oggi = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
data_str = oggi.strftime("%Y-%m-%dT12:00:00Z")
dtg_encoded = data_str.replace(":", "%3A")

iframe_url = f"https://www.wxcharts.com/?dataset=ecmwf_op&region=italy&element=overview&run=12&dtg={dtg_encoded}"

st.caption(f"**Run:** {oggi.strftime('%d %B %Y alle 12:00 UTC')}")

# Iframe corretto (senza sandbox)
st.components.v1.iframe(
    iframe_url,
    height=850,
    scrolling=True
)

st.divider()

# Link di backup
st.markdown(f"""
[**🔗 Apri la mappa WX Charts in una nuova scheda**]({iframe_url})
""", unsafe_allow_html=True)

if st.button("🔄 Aggiorna mappa con data odierna"):
    st.rerun()

st.info("💡 Se l'iframe resta bianco o non carica bene, usa il link sopra per aprire la mappa in una nuova scheda.")