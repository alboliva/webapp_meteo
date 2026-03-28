import streamlit as st
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
import tempfile
import os

st.set_page_config(page_title="Mappe Meteo WX Charts", layout="wide")
st.title("🗺️ Mappe Meteo WX Charts")
st.markdown("### ECMWF Overview - Italia (Screenshot)")

# ====================== DATA ======================
oggi = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
data_str = oggi.strftime("%Y-%m-%dT12:00:00Z")

url = f"https://www.wxcharts.com/api/content/ecmwf_op/italy/overview/{data_str}/{data_str}"

st.caption(f"**Run:** {oggi.strftime('%d %B %Y alle 12:00 UTC')}")

# ====================== FUNZIONE SCREENSHOT ======================
@st.cache_data(ttl=3600)  # cache di 1 ora
def take_screenshot(url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1400, "height": 900})   # dimensione buona per la mappa
        
        page.goto(url, wait_until="networkidle", timeout=30000)
        
        # Aspetta che la mappa sia caricata (puoi aumentare se necessario)
        page.wait_for_timeout(4000)
        
        # Screenshot full page
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            screenshot_path = tmp.name
            page.screenshot(path=screenshot_path, full_page=True)
        
        browser.close()
        return screenshot_path

# ====================== ESECUZIONE ======================
try:
    with st.spinner("📸 Sto catturando lo screenshot della mappa... (può richiedere 5-10 secondi)"):
        img_path = take_screenshot(url)
        
        st.image(img_path, use_container_width=True)
        
        # Bottone per scaricare l'immagine
        with open(img_path, "rb") as file:
            st.download_button(
                label="⬇️ Scarica lo screenshot",
                data=file,
                file_name=f"wxcharts_ecmwf_italy_{data_str[:10]}.png",
                mime="image/png"
            )
        
        # Pulizia file temporaneo (opzionale)
        os.unlink(img_path)

except Exception as e:
    st.error(f"❌ Errore durante lo screenshot: {e}")
    st.info("Prova ad usare il link diretto qui sotto:")

st.divider()

st.markdown(f"[🔗 Apri la mappa originale in una nuova scheda]({url})")

if st.button("🔄 Aggiorna screenshot (run di oggi)"):
    st.cache_data.clear()
    st.rerun()