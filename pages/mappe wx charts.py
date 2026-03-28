import streamlit as st
from datetime import datetime, timezone, timedelta

st.set_page_config(page_title="Mappe Meteo WX Charts", layout="wide")

st.title("🗺️ Mappe Meteo WX Charts - ECMWF Italia")
st.markdown("### Previsione ECMWF - Panoramica Italia")

# ====================== DATA BASE ======================
oggi = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
data_oggi = oggi.strftime("%Y-%m-%dT12:00:00Z")
data_domani = (oggi + timedelta(days=1)).strftime("%Y-%m-%dT12:00:00Z")

st.caption(f"**Run:** {oggi.strftime('%d %B %Y alle 12:00 UTC')}")

# ====================== URL MAPPE ======================
base = "https://www.wxcharts.com/api/content/ecmwf_op/italy"

maps = {
    "Overview": f"{base}/overview/{data_oggi}/{data_oggi}",
    
    "Vento 10m (km/h)": f"https://www.wxcharts.com/?dataset=ecmwf_op&region=italy&element=wind10mkph&run=12&dtg={data_oggi.replace(':', '%3A')}&meteoModel=ecop&ensModel=eceps&chartRun=0",
    
    "Neve (Snow Depth)": f"https://www.wxcharts.com/?dataset=ecmwf_op&region=italy&element=snowdepth&run=12&dtg={data_oggi.replace(':', '%3A')}&meteoModel=ecop&ensModel=eceps&chartRun=0",
    
    "Anomalie Temperatura 850hPa": f"https://www.wxcharts.com/?dataset=ecmwf_op&region=italy&element=850temp_anom&run=12&dtg={data_oggi.replace(':', '%3A')}&meteoModel=ecop&ensModel=eceps&chartRun=0",
    
    "Pioggia (Accumulo 24h)": f"https://www.wxcharts.com/?dataset=ecmwf_op&region=italy&element=accprecip24&run=12&dtg={data_domani.replace(':', '%3A')}&meteoModel=ecop&ensModel=eceps&chartRun=0"
}

# ====================== GRIGLIA 2x2 ======================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌡️ Overview")
    st.components.v1.iframe(maps["Overview"], height=520, scrolling=True)
    
    st.subheader("❄️ Neve")
    st.components.v1.iframe(maps["Neve (Snow Depth)"], height=520, scrolling=True)

with col2:
    st.subheader("🌬️ Vento 10m")
    st.components.v1.iframe(maps["Vento 10m (km/h)"], height=520, scrolling=True)
    
    st.subheader("📈 Anomalie 850hPa")
    st.components.v1.iframe(maps["Anomalie Temperatura 850hPa"], height=520, scrolling=True)

# Pioggia su riga separata (più larga)
st.subheader("🌧️ Pioggia - Accumulo 24h")
st.components.v1.iframe(maps["Pioggia (Accumulo 24h)"], height=520, scrolling=True)

st.divider()

# Link di backup per tutte le mappe
st.markdown("### 🔗 Link diretti (se gli iframe rimangono bianchi)")
for nome, url in maps.items():
    st.markdown(f"**{nome}** → [Apri in nuova scheda]({url})")

if st.button("🔄 Aggiorna tutte le mappe con run di oggi"):
    st.rerun()

st.info("💡 **Nota**: wxcharts.com spesso blocca gli iframe. Se vedi pagine bianche, usa i link sopra per aprire ogni mappa individualmente.")