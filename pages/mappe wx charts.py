import streamlit as st
import os
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
import io

# ====================== INSTALLAZIONE PLAYWRIGHT (una sola volta) ======================
if not os.path.exists("/home/appuser/.cache/ms-playwright"):
    with st.spinner("⚙️ Prima installazione di Playwright... (può richiedere 30-60 secondi)"):
        os.system("playwright install chromium --with-deps")

st.set_page_config(page_title="Mappe Meteo WX Charts", layout="wide")
st.title("🗺️ Mappe Meteo WX Charts")
st.markdown("### ECMWF Overview - Italia (Screenshot)")

# Data e URL
oggi = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
data_str = oggi.strftime("%Y-%m-%dT12:00:00Z")
url = f"https://www.wxcharts.com/api/content/ecmwf_op/italy/overview/{data_str}/{data_str}"

st.caption(f"**Run:** {oggi.strftime('%d %B %Y alle 12:00 UTC')}")

@st.cache_data(ttl=3600)
def take_screenshot_bytes(url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 1000})
        page.goto(url, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(6000)        # tempo per caricare la mappa
        screenshot_bytes = page.screenshot(full_page=True, type="png")
        browser.close()
        return screenshot_bytes

# ====================== Esecuzione ======================
try:
    with st.spinner("📸 Cattura dello screenshot in corso..."):
        img_bytes = take_screenshot_bytes(url)
        
        st.image(img_bytes, use_container_width=True, caption="ECMWF Overview - Italia")

    st.download_button(
        label="⬇️ Scarica immagine PNG",
        data=img_bytes,
        file_name=f"ecmwf_italy_{data_str[:10]}.png",
        mime="image/png"
    )

except Exception as e:
    st.error(f"❌ Errore: {e}")
    st.markdown(f"[🔗 Apri la mappa direttamente]({url})")

st.divider()
if st.button("🔄 Aggiorna screenshot"):
    st.cache_data.clear()
    st.rerun()