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
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m&timezone=Europe/Rome"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        temp = data["current"]["temperature_2m"]
        return f"{temp:.1f} °C"
    except:
        return "N/A"

def leggi_webcam():
    webcam = []
    if not os.path.exists(DATA_FILE):
        st.error(f"File {DATA_FILE} non trovato! Crea data.txt nella root.")
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            parti = linea.split(",", 3)
            if len(parti) != 4:
                continue
            try:
                lat = float(parti[0])
                lon = float(parti[1])
                nome = parti[2].strip()
                url = parti[3].strip()
                temp = get_temperature(lat, lon)
                webcam.append({"lat": lat, "lon": lon, "nome": nome, "url": url, "temp": temp})
            except:
                pass
    return webcam

def crea_mappa(gruppi_webcam):
    m = folium.Map(location=[41.8719, 12.5674], zoom_start=6, tiles="CartoDB positron")
    for (lat, lon), cams in gruppi_webcam.items():
        nome_tooltip = cams[0]["nome"] + (f" (+{len(cams)-1} altre)" if len(cams) > 1 else "")
        immagini_html = ""
        for cam in cams:
            immagini_html += f"""
                <div style="margin-bottom: 20px; text-align: center;">
                    <strong>{cam['nome']}</strong><br>
                    <span style="color: #555;">{cam['temp']}</span><br>
                    <img src="{cam['url']}" width="280" style="border-radius: 8px; margin-top: 8px;">
                </div>
            """
        html_popup = f'<div style="width:{POPUP_CONTENT_WIDTH}px; max-height:{POPUP_HEIGHT}px; overflow-y:auto; padding:10px;">{immagini_html}</div>'
        iframe = folium.IFrame(html_popup, width=POPUP_CONTENT_WIDTH + 30, height=POPUP_HEIGHT + 20)
        popup = folium.Popup(iframe, max_width=360)
        folium.Marker(
            [lat, lon],
            popup=popup,
            tooltip=nome_tooltip,
            icon=folium.Icon(color="red", icon="camera", prefix="fa")
        ).add_to(m)
    return m

def crea_galleria(webcam_list):
    st.subheader("Galleria Webcam")

    # ==================== PARAMETRI FACILI DA MODIFICARE ====================
    CARD_HEIGHT = 220          # ←←← Altezza totale della card bianca (aumenta/diminuisci qui)
    CARD_WIDTH = 220           # Larghezza approssimativa della card (per uniformità)
    IMAGE_HEIGHT = "97%"      # L'immagine riempie tutta la card
    TITLE_FONT_SIZE = "0.9em"  # Dimensione titolo
    TITLE_PADDING = "15px"     # Spazio interno del titolo
    ROW_SPACING = 40           # ←←← Spazio verticale tra una riga di card e la successiva

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
        background: linear-gradient(to bottom, rgba(0,0,0,0.7), transparent);
        color: white;
        font-weight: bold;
        font-size: {TITLE_FONT_SIZE};
        padding: {TITLE_PADDING};
        text-align: center;
        border-radius: 12px 12px 0 0;
        pointer-events: none;  /* Permette click sotto */
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

            st.markdown(f"""
            <div class="webcam-card">
                <a href="{cam['url']}" target="_blank" style="display:block; height:100%; width:100%;">
                    <img src="{cam['url']}" class="webcam-image" alt="{cam['nome']}">
                    <div class="webcam-title-overlay">
                        {cam['nome']}{temp_part}
                    </div>
                </a>
            </div>
            """, unsafe_allow_html=True)

# ==================== MAIN ====================
st.title("Webcam e Mappa Interattiva Italia")

webcam_list = leggi_webcam()

if webcam_list:
    st.write(f"Trovate {len(webcam_list)} webcam.")

    gruppi = defaultdict(list)
    for cam in webcam_list:
        key = (round(cam["lat"], 4), round(cam["lon"], 4))
        gruppi[key].append(cam)

    mappa = crea_mappa(gruppi)
    folium_static(mappa, width=800, height=500)

    crea_galleria(webcam_list)
else:
    st.info("Aggiungi webcam nel file data.txt per visualizzare mappa e galleria.")