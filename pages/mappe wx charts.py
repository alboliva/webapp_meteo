import streamlit as st
from datetime import datetime, timezone

st.set_page_config(page_title="Mappe Meteo WX Charts", layout="wide")
st.title("🗺️ Mappe Meteo WX Charts")
st.markdown("### ECMWF Overview - Italia")

# ====================== DATA E ORA ======================
oggi = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)

# Formato richiesto da wxcharts (es. 2026-03-28T12:00:00Z)
data_str = oggi.strftime("%Y-%m-%dT12:00:00Z")

# URL diretto alla pagina che vuoi inglobare
iframe_url = f"https://www.wxcharts.com/api/content/ecmwf_op/italy/overview/{data_str}/{data_str}"

st.caption(f"**Run:** {oggi.strftime('%d %B %Y alle 12:00 UTC')}")

# ====================== IFRAME ======================
st.components.v1.iframe(
    iframe_url,
    height=900,           # Puoi aumentare se serve più spazio
    scrolling=True
)

st.divider()

# Link di backup (molto utile perché l'iframe spesso non carica bene)
st.markdown(f"""
[**🔗 Apri la mappa completa in una nuova scheda**]({iframe_url})
""", unsafe_allow_html=True)

if st.button("🔄 Aggiorna con run di oggi (12 UTC)"):
    st.rerun()

st.info("💡 **Nota importante**: Se l'iframe rimane bianco o non carica, usa il link sopra. wxcharts.com spesso blocca l'embedding tramite iframe per motivi di sicurezza.")