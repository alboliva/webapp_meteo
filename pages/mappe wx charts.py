import streamlit as st
from datetime import datetime, timezone, timedelta

st.set_page_config(page_title="Mappe Meteo WX", layout="wide")

st.title("🗺️ Mappe Meteo WX")
# st.markdown("### ECMWF - Italia")

# ====================== DATE ======================
oggi = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
data_oggi = oggi.strftime("%Y-%m-%dT12:00:00Z")
data_domani = (oggi + timedelta(days=1)).strftime("%Y-%m-%dT12:00:00Z")

st.caption(f"**Run:** {oggi.strftime('%d %B %Y alle 12:00 UTC')}")

# ====================== URL MAPPE (versione /api/content/) ======================
maps = {
    "🌡️ Overview": f"https://www.wxcharts.com/api/content/ecmwf_op/italy/overview/{data_oggi}/{data_oggi}",
    
    "🌬️ Vento 10m (km/h)": f"https://www.wxcharts.com/api/content/ecmwf_op/italy/wind10mkph/{data_oggi}/{data_oggi}",
    
    "❄️ Neve (Snow Depth)": f"https://www.wxcharts.com/api/content/ecmwf_op/italy/snowdepth/{data_oggi}/{data_oggi}",
    
    "📊 Anomalie 850hPa": f"https://www.wxcharts.com/api/content/ecmwf_op/italy/850temp_anom/{data_oggi}/{data_oggi}",
    
    "🌧️ Pioggia (Accumulo 24h)": f"https://www.wxcharts.com/api/content/ecmwf_op/italy/accprecip24/{data_oggi}/{data_domani}"
}

# ====================== GRIGLIA PULSANTI ======================
st.markdown("### Seleziona la mappa da aprire")

col1, col2 = st.columns(2)

with col1:
    for nome, url in list(maps.items())[:3]:
        st.markdown(f"""
        <a href="{url}" target="_blank" style="text-decoration: none;">
            <div style="background: linear-gradient(135deg, #1e40af, #3b82f6); 
                        color: white; 
                        padding: 22px 15px; 
                        border-radius: 12px; 
                        margin: 10px 0; 
                        text-align: center;
                        font-size: 18px;
                        font-weight: 600;
                        box-shadow: 0 4px 15px rgba(30, 64, 175, 0.3);">
                {nome}
            </div>
        </a>
        """, unsafe_allow_html=True)

with col2:
    for nome, url in list(maps.items())[3:]:
        st.markdown(f"""
        <a href="{url}" target="_blank" style="text-decoration: none;">
            <div style="background: linear-gradient(135deg, #1e40af, #3b82f6); 
                        color: white; 
                        padding: 22px 15px; 
                        border-radius: 12px; 
                        margin: 10px 0; 
                        text-align: center;
                        font-size: 18px;
                        font-weight: 600;
                        box-shadow: 0 4px 15px rgba(30, 64, 175, 0.3);">
                {nome}
            </div>
        </a>
        """, unsafe_allow_html=True)

st.divider()

if st.button("🔄 Aggiorna tutte le mappe con il run di oggi"):
    st.rerun()

st.info("💡 Clicca sui pulsanti blu per aprire ogni mappa in una **nuova scheda**.\n"
        "Le mappe si aggiornano automaticamente ogni giorno.")