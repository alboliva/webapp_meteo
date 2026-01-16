import streamlit as st
import requests
from datetime import datetime, timedelta, timezone
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

# =============================================================================
# CONFIGURAZIONE
# =============================================================================

st.set_page_config(
    page_title="Meteo Rismi - Sintesi Automatica",
    layout="wide",
    page_icon="🌤️",
    initial_sidebar_state="expanded"
)

# ==================== ID VIDEO GIULIACCI (cambia manualmente) ====================
VIDEO_ID_GIULIACCI = "cz-qju5LcFk"   # ← CAMBIA QUESTO VALORE quando esce un nuovo video!

# =============================================================================
# FUNZIONI AUTOMATICHE
# =============================================================================

@st.cache_data(ttl=1800)  # 30 minuti
def get_openmeteo_data():
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        "latitude=41.9028&longitude=12.4964&"
        "current=temperature_2m,apparent_temperature,precipitation,pressure_msl,"
        "wind_speed_10m,wind_direction_10m,weathercode&"
        "hourly=freezing_level_height,snow_depth&"
        "daily=temperature_2m_max,temperature_2m_min,precipitation_sum&"
        "timezone=Europe/Rome"
    )
    try:
        return requests.get(url, timeout=10).json()
    except:
        return None


def analyze_weather_rules(data):
    if not data:
        return {}
    curr = data["current"]
    freezing = data["hourly"].get("freezing_level_height", [2500])[0]
    snow_cm = data["hourly"].get("snow_depth", [0])[0] * 100
    wind_dir = curr["wind_direction_10m"]
    afflusso_freddo = 20 <= wind_dir <= 100 and curr["wind_speed_10m"] > 12
    return {
        "pressione": "bassa" if curr["pressure_msl"] < 1012 else "alta" if curr["pressure_msl"] > 1020 else "neutra",
        "freddo": curr["temperature_2m"] < 8,
        "molto_freddo": curr["temperature_2m"] < 4,
        "instabilita": curr["precipitation"] > 0 or data["daily"]["precipitation_sum"][0] > 2,
        "neve_bassa_quota": freezing < 1400 and snow_cm > 0.05,
        "zero_termico": f"≈ {int(freezing)} m",
        "afflusso_freddo": afflusso_freddo,
        "gelate_notturne": curr["temperature_2m"] < 3
    }


def get_dynamic_snow_map():
    now = datetime.now(timezone.utc)
    start_hour = 12 if now.hour >= 13 else 0
    start = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=7)
    start_str = start.strftime("%Y-%m-%dT%H:00:00Z")
    end_str = end.strftime("%Y-%m-%dT%H:00:00Z")
    return f"https://www.wxcharts.com/api/contentwithoverlay/ecmwf_op/italy/snowdepth/{start_str}/{end_str}"


@st.cache_data(ttl=3600)
def get_giuliacci_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['it', 'it-IT'])
        text = "\n".join([f"[{int(entry['start']//60):02d}:{int(entry['start']%60):02d}] {entry['text']}" for entry in transcript_list])
        if len(text) > 3000:
            text = text[:3000] + "\n\n... (trascrizione parziale - vedi video completo)"
        return {"success": True, "text": text}
    except Exception as e:
        return {"success": False, "error": str(e)}


# =============================================================================
# PAGINA PRINCIPALE
# =============================================================================

st.title("Meteo Rismi – Sintesi Automatica")

with st.expander("Sommario Condizioni Meteo – Generato Automaticamente", expanded=True):
    data = get_openmeteo_data()
    
    if data:
        curr = data["current"]
        daily = data["daily"]
        rules = analyze_weather_rules(data)
        now_str = datetime.now().strftime("%d %B %Y – %H:%M")
        
        st.markdown(f"""
**Aggiornamento automatico — {now_str}**

**Roma / Lazio oggi**  
Temperatura attuale: **{curr['temperature_2m']:.1f}°C** (percepita {curr['apparent_temperature']:.1f}°C)  
Mass/Min attesa: **{daily['temperature_2m_max'][0]:.1f}°C** / **{daily['temperature_2m_min'][0]:.1f}°C**  
Precipitazioni odierne: **{daily['precipitation_sum'][0]:.1f} mm**  
Vento: {curr['wind_speed_10m']:.0f} km/h da {curr['wind_direction_10m']}°  
Pressione: {curr['pressure_msl']:.0f} hPa → **{rules['pressione']}**  
Zero termico: **{rules['zero_termico']}** → {"possibile neve bassa quota" if rules['neve_bassa_quota'] else "precipitazioni liquide o neve solo in alta quota"}
{"→ Gelate notturne probabili" if rules['gelate_notturne'] else ""}
        """)




st.subheader("Satellite + Precipitazioni (Wetterzentrale)")

# Mappa Wetterzentrale con parametri per mostrare satellite + precipitazioni
wetterzentrale_url = (
    "https://www.wetterzentrale.de/en/reanalysis.php?"
    "model=sat&"
    "var=413&"           # var=413 = satellite IR con overlay precipitazioni
    "map=1&"             # mappa Europa
    "run=latest"         # usa il run più recente disponibile
)

st.components.v1.iframe(
    wetterzentrale_url,
    height=300,
    scrolling=True
)

st.caption("Fonte: Wetterzentrale.de")
