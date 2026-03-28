import streamlit as st
from datetime import datetime, timezone, timedelta

st.set_page_config(page_title="Mappe Meteo WX Charts", layout="wide")

st.title("🗺️ Mappe Meteo WX Charts")
st.markdown("### ECMWF - Italia")

# ====================== DATE ======================
oggi = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
data_oggi_str = oggi.strftime("%Y-%m-%dT12:00:00Z")
data_oggi_encoded = data_oggi_str.replace(":", "%3A")

data_domani = oggi + timedelta(days=1)
data_domani_str = data_domani.strftime("%Y-%m-%dT12:00:00Z")
data_domani_encoded = data_domani_str.replace(":", "%3A")

st.caption(f"**Run:** {oggi.strftime('%d %B %Y alle 12:00 UTC')}")

# ====================== URL DELLE MAPPE ======================
maps = {
    "🌡️ Overview": f"https://www.wxcharts.com/api/content/ecmwf_op/italy/overview/{data_oggi_str}/{data_oggi_str}",
    
    "🌬️ Vento 10m (km/h)": f"https://www.wxcharts.com/?dataset=ecmwf_op&region=italy&element=wind10mkph&run=12&dtg={data_oggi_encoded}",
    
    "❄️ Neve (Snow Depth)": f"https://www.wxcharts.com/?dataset=ecmwf_op&region=italy&element=snowdepth&run=12&dtg={data_oggi_encoded}",
    
    "📊 Anomalie Temperatura 850hPa": f"https://www.wxcharts.com/?dataset=ecmwf_op&region=italy&element=850temp_anom&run=12&dtg={data_oggi_encoded}",
    
    "🌧️ Pioggia (Accumulo 24h)": f"https://www.wxcharts.com/?dataset=ecmwf_op&region=italy&element=accprecip24&run=12&dtg={data_domani_encoded}"
}

# ====================== GRIGLIA CON PULSANTI ======================
st.markdown("### Seleziona la mappa da visualizzare")

col1, col2 = st.columns(2)

with col1:
    for nome, url in list(maps.items())[:3]:   # Prime 3 mappe nella prima colonna
        st.markdown(f"""
        <a href="{url}" target="_blank" style="text-decoration: none;">
            <div style="background: linear-gradient(135deg, #1e3a8a, #3b82f6); 
                        color: white; 
                        padding: 20px; 
                        border-radius: 12px; 
                        margin: 12px 0; 
                        text-align: center;
                        font-size: 18px;
                        font-weight: 600;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                {nome}
            </div>
        </a>
        """, unsafe_allow_html=True)

with col2:
    for nome, url in list(maps.items())[3:]:   # Le restanti nella seconda colonna
        st.markdown(f"""
        <a href="{url}" target="_blank" style="text-decoration: none;">
            <div style="background: linear-gradient(135deg, #1e3a8a, #3b82f6); 
                        color: white; 
                        padding: 20px; 
                        border-radius: 12px; 
                        margin: 12px 0; 
                        text-align: center;
                        font-size: 18px;
                        font-weight: 600;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                {nome}
            </div>
        </a>
        """, unsafe_allow_html=True)

# Pioggia la mettiamo più grande, centrata sotto
st.markdown(f"""
<a href="{maps['🌧️ Pioggia (Accumulo 24h)']}" target="_blank" style="text-decoration: none;">
    <div style="background: linear-gradient(135deg, #166534, #4ade80); 
                color: white; 
                padding: 24px; 
                border-radius: 12px; 
                margin: 20px 0; 
                text-align: center;
                font-size: 20px;
                font-weight: 700;
                box-shadow: 0 6px 15px rgba(0,0,0,0.2);">
        🌧️ Pioggia (Accumulo 24h) — {data_domani.strftime('%d %B')}
    </div>
</a>
""", unsafe_allow_html=True)

st.divider()

if st.button("🔄 Aggiorna tutte le mappe con il run di oggi"):
    st.rerun()

st.info("💡 Clicca sui pulsanti colorati per aprire ogni mappa in una **nuova scheda**.")