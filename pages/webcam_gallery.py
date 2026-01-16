import streamlit as st
from streamlit_folium import folium_static
import folium
import requests
from collections import defaultdict
import os

DATA_FILE = "data.txt"
POPUP_HEIGHT = 200
POPUP_CONTENT_WIDTH = 320

# ==================== FUNZIONI ====================
def get_temperature(lat, lon):
    """Temperatura attuale da Open-Meteo"""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m&timezone=Europe/Rome"
    try:
        response = requests.get(url, timeout=8)
        data = response.json()
        temp = data["current"]["temperature_2m"]
        return f"{temp:.1f} °C"
    except:
        return "N/A"

def get_altitude(lat, lon):
    """Altitudine in metri da Open-Elevation (gratuita, no key)"""
    url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
    try:
        response = requests.get(url, timeout=8)
        data = response.json()
        if 'results' in data and len(data['results']) > 0:
            alt = data['results'][0].get('elevation')
            if alt is not None:
                return f"{int(alt)} m"
    except:
        pass
    return "N/A"  # se fallisce

def leggi_webcam():
    webcam = []
    if not os.path.exists(DATA_FILE):
        st.error(f"File {DATA_FILE} non trovato! Crea data.txt nella root.")
        return []
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            # Escludi righe vuote o commentate con #
            if not linea or linea.startswith("#"):
                continue
            parti = linea.split(",", 3)
            if len(parti) != 4:
                continue
            try:
                lat = float(parti[0].strip())
                lon = float(parti[1].strip())
                nome = parti[2].strip()
                url = parti[3].strip()
                is_youtube = "youtube.com/embed" in url.lower() or "youtu.be" in url.lower()
                temp = get_temperature(lat, lon)
                alt = get_altitude(lat, lon)  # ← ALTITUDINE!
                webcam.append({
                    "lat": lat,
                    "lon": lon,
                    "nome": nome,
                    "url": url,
                    "temp": temp,
                    "alt": alt,               # ← aggiunto
                    "is_youtube": is_youtube
                })
            except Exception:
                pass  # salta righe malformate
    
    return webcam

def crea_galleria(webcam_list):
    # ==================== PARAMETRI FACILI DA MODIFICARE ====================
    CARD_HEIGHT = 260
    CARD_WIDTH = 240
    IMAGE_HEIGHT = "97%"
    TITLE_FONT_SIZE = "0.9em"
    TITLE_PADDING = "14px"
    ROW_SPACING = 60
    CARD_HORIZONTAL_GAP = 16

    # ==================== CSS ====================
    st.markdown(f"""
    <style>
    .webcam-card {{
        position: relative;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.12);
        overflow: hidden;
        height: {CARD_HEIGHT}px;
        width: {CARD_WIDTH}px;
        margin-bottom: {ROW_SPACING}px;
        transition: transform 0.2s, box-shadow 0.2s;
        display: flex;
        flex-direction: column;
    }}
    .webcam-card:hover {{
        transform: translateY(-8px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.18);
    }}
    .webcam-image {{
        width: 100%;
        height: {IMAGE_HEIGHT};
        object-fit: cover;
        flex-grow: 1;
    }}
    .webcam-title-overlay {{
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        background: linear-gradient(to bottom, rgba(0,0,0,0.75), transparent);
        color: white;
        font-weight: bold;
        font-size: {TITLE_FONT_SIZE};
        padding: {TITLE_PADDING};
        text-align: center;
        border-radius: 12px 12px 0 0;
        pointer-events: none;
        z-index: 2;
    }}
    .youtube-container {{
        position: relative;
        width: 100%;
        height: 100%;
        flex-grow: 1;
    }}
    .youtube-iframe {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        border: none;
    }}
    div[data-testid="column"] {{
        padding-left: {CARD_HORIZONTAL_GAP}px !important;
        padding-right: {CARD_HORIZONTAL_GAP}px !important;
    }}
    div[data-testid="stHorizontalBlock"] {{
        justify-content: center !important;
        gap: {CARD_HORIZONTAL_GAP * 1.5}px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # ==================== 3 COLONNE FISSE ====================
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]

    for index, cam in enumerate(webcam_list):
        col = cols[index % 3]
        with col:
            temp_part = f", {cam['temp']}" if cam['temp'] != "N/A" else ""
            alt_part = f", {cam['alt']}" if cam['alt'] != "N/A" else ""
            titolo_completo = f"{cam['nome']}{temp_part}{alt_part}"
            
            if cam["is_youtube"]:
                yt_params = "?autoplay=0&mute=0&loop=1&rel=0&modestbranding=1&controls=1"
                embed_url = cam["url"] + yt_params
                st.markdown(f"""
                <div class="webcam-card">
                    <div class="youtube-container">
                        <iframe
                            class="youtube-iframe"
                            src="{embed_url}"
                            frameborder="0"
                            allowfullscreen
                        ></iframe>
                    </div>
                    <div class="webcam-title-overlay">
                        {titolo_completo} 🎥 LIVE
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="webcam-card">
                    <a href="{cam['url']}" target="_blank" style="display:block; height:100%; width:100%;">
                        <img src="{cam['url']}" class="webcam-image" alt="{cam['nome']}" loading="lazy">
                        <div class="webcam-title-overlay">
                            {titolo_completo}
                        </div>
                    </a>
                </div>
                """, unsafe_allow_html=True)

# ==================== MAIN ====================
st.title("Webcam Gallery Italia")
webcam_list = leggi_webcam()
if webcam_list:
    st.write(f"Trovate {len(webcam_list)} webcam / live stream.")
    gruppi = defaultdict(list)
    for cam in webcam_list:
        key = (round(cam["lat"], 4), round(cam["lon"], 4))
        gruppi[key].append(cam)
    crea_galleria(webcam_list)
else:
    st.info("Aggiungi webcam o live stream nel file data.txt per visualizzare la galleria.")