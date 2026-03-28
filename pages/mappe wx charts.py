import streamlit as st
from datetime import datetime, timezone

st.set_page_config(page_title="Mappe Meteo WX Charts", layout="wide")

st.title("🗺️ Mappe Meteo WX Charts")
st.markdown("### ECMWF Overview - Italia")

oggi = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
data_str = oggi.strftime("%Y-%m-%dT12:00:00Z")

iframe_url = f"https://www.wxcharts.com/api/content/ecmwf_op/italy/overview/{data_str}/{data_str}"

st.caption(f"**Run:** {oggi.strftime('%d %B %Y alle 12:00 UTC')}")

st.success("✅ La mappa è pronta!")

st.markdown(f"""
<div style="text-align: center; padding: 30px 0;">
    <a href="{iframe_url}" target="_blank" style="background-color: #0066cc; color: white; padding: 18px 36px; 
    text-decoration: none; border-radius: 8px; font-size: 18px; font-weight: bold;">
        🌐 APRI LA MAPPA INTERATTIVA
    </a>
</div>
""", unsafe_allow_html=True)

st.info("🔗 Clicca sul pulsante sopra per aprire la mappa WX Charts in una nuova scheda.\n\n"
        "L'embedding diretto non è possibile perché il sito wxcharts blocca gli iframe per motivi di sicurezza.")

if st.button("🔄 Aggiorna con run di oggi (12 UTC)"):
    st.rerun()