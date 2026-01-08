import streamlit as st

st.title("Previsioni Meteo Roma")

st.markdown("### Previsioni complete (orarie e giornaliere) da Meteoblue")
st.markdown("""
<iframe src="https://www.meteoblue.com/en/weather/widget/daily/rome_italy_3169070?geoloc=fixed&days=7&tempunit=C&windunit=kmh&layout=light" 
        width="100%" height="600" frameborder="0" allowtransparency="true" sandbox="allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox"></iframe>
""", unsafe_allow_html=True)

st.markdown("### Previsioni avanzate interattive (Windy)")
st.markdown("""
<iframe width="100%" height="600" src="https://embed.windy.com/embed2.html?lat=41.890&lon=12.492&detailLat=41.890&detailLon=12.492&zoom=8&level=surface&overlay=temp&product=ecmwf&menu=&message=true&marker=true&calendar=now&pressure=true&type=map&location=coordinates&detail=&metricWind=km/h&metricTemp=%C2%B0C" frameborder="0"></iframe>
""", unsafe_allow_html=True)