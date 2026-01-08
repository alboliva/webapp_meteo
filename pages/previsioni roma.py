import streamlit as st

st.title("Previsioni Meteo Roma")

# st.markdown("### Previsioni complete (orarie e giornaliere) da Meteoblue")
st.markdown("""
<iframe src="https://www.meteoblue.com/it/tempo/widget/meteogram/roma_italia_3169070?geoloc=fixed&temperature_units=CELSIUS&windspeed_units=KILOMETER_PER_HOUR&precipitation_units=MILLIMETER&forecast_days=4&layout=bright&autowidth=auto&user_key=2e2679f1d09611f6&embed_key=9c2daca7cdbb6426&sig=ec704368eda16bc0c704a15cfbd0b2f6296c8d90590ae916006ef5e1ea61ef61" frameborder="0" scrolling="NO" allowtransparency="true" sandbox="allow-same-origin allow-scripts allow-popups allow-popups-to-escape-sandbox" style="width: 100%;height: 700px;border: 0;overflow: hidden;"></iframe>
""", unsafe_allow_html=True)


st.markdown("### Previsioni avanzate interattive (Windy)")
st.markdown("""
<iframe width="100%" height="600" src="https://embed.windy.com/embed2.html?lat=41.890&lon=12.492&detailLat=41.890&detailLon=12.492&zoom=8&level=surface&overlay=temp&product=ecmwf&menu=&message=true&marker=true&calendar=now&pressure=true&type=map&location=coordinates&detail=&metricWind=km/h&metricTemp=%C2%B0C" frameborder="0"></iframe>
""", unsafe_allow_html=True)