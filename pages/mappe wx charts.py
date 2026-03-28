import streamlit as st
from datetime import datetime, timezone

st.set_page_config(page_title="Mappe Meteo WX Charts", layout="wide")

st.title("🗺️ Mappe Meteo WX Charts")
st.markdown("### ECMWF Overview - Italia")

# Genera la data di oggi alle 12:00 UTC
oggi = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
data_str = oggi.strftime("%Y-%m-%dT12:00:00Z")

# URL diretto alla pagina che vuoi mostrare
iframe_url = f"https://www.wxcharts.com/api/content/ecmwf_op/italy/overview/{data_str}/{data_str}"

st.caption(f"**Run:** {oggi.strftime('%d %B %Y alle 12:00 UTC')}")

# ====================== IFRAME ======================
st.components.v1.iframe(
    src=iframe_url,          # meglio usare 'src=' esplicitamente
    height=950,              # aumenta se la mappa viene tagliata
    scrolling=True,
    width=None               # lascia che si adatti alla larghezza
)

st.divider()

# Link di backup (quasi sempre necessario)
st.markdown(f"""
**🔗 Se l'iframe non carica, apri qui:**
[🌐 Apri la mappa WX Charts in una nuova scheda]({iframe_url})
""", unsafe_allow_html=True)

if st.button("🔄 Aggiorna mappa con run di oggi"):
    st.rerun()

st.info("""
💡 **Nota importante**:  
Molti siti (incluso wxcharts.com) impediscono l’embedding tramite iframe per motivi di sicurezza (X-Frame-Options o Content-Security-Policy).  
Se vedi una pagina bianca, purtroppo non c’è molto da fare con l’iframe → usa il link sopra.
""")