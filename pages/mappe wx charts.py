import streamlit as st

st.title("Mappe Meteo WX Charts")

st.markdown("### Mappe Meteo WX Charts")
st.markdown("""
<iframe width="100%" height="700" src="https://www.wxcharts.com/?dataset=ecmwf_op&region=italy&element=overview&run=12&dtg=2026-03-26T12%3A00%3A00Z&meteoModel=ecop&ensModel=eceps&chartRun=0&lat=51.5&lon=0.12" frameborder="0"></iframe>
""", unsafe_allow_html=True)
