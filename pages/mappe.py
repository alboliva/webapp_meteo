import streamlit as st

st.title("Mappe Meteo Interattive")

st.markdown("### Mappa completa (vento, pioggia, temperatura, radar) - Windy")
st.markdown("""
<iframe width="100%" height="700" src="https://embed.windy.com/embed2.html?lat=41.902&lon=12.496&detailLat=41.902&detailLon=12.496&zoom=6&level=surface&overlay=rain&product=ecmwf&menu=&message=&marker=&calendar=now&pressure=&type=map&location=coordinates&detail=&metricWind=km/h&metricTemp=%C2%B0C&metricRain=mm" frameborder="0"></iframe>
""", unsafe_allow_html=True)
