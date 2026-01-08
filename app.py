import streamlit as st
import requests  # Per API meteo opzionale

# Configurazione app
st.set_page_config(page_title="App Meteo Roma", layout="wide")

# Funzione per fetchare dati meteo da OpenWeatherMap (opzionale, registrati per una API key gratuita su openweathermap.org)
def get_meteo_summary(city="Roma"):
    api_key = "LA_TUA_API_KEY"  # Sostituisci con la tua key
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=it"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            return f"Temperatura: {data['main']['temp']}°C, Condizioni: {data['weather'][0]['description']}, Umidità: {data['main']['humidity']}%"
        else:
            return "Errore nel fetchare dati meteo."
    except:
        return "Connessione fallita."

# Home page
def home_page():
    st.title("Benvenuto in Meteo Rismi")
    
    # Riquadro sommario
    with st.expander("Sommario Condizioni Meteo", expanded=True):
        # Testo personalizzato
        custom_text = st.text_area(
            "Inserisci il tuo testo personalizzato:",
            value="Oggi a Roma: Cielo sereno con possibili nuvole nel pomeriggio. Consigli: Porta un ombrello!"
        )
        st.write(custom_text)
        
        # Aggiungi summary meteo automatico (opzionale)
        meteo_auto = get_meteo_summary()
        st.write(f"Dati reali: {meteo_auto}")
        
        # Carrellata di video (sostituisci con URL reali pubblici)
        st.subheader("Video Meteo da Social/Web")
        video_urls = [
            "https://www.facebook.com/reel/1959266798340685"
        ]
        
        # Input per aggiungere URL
        new_url = st.text_input("Aggiungi URL video:")
        if new_url:
            video_urls.append(new_url)
        
        # Visualizza in colonne (carousel semplice)
        cols = st.columns(min(len(video_urls), 4))  # Max 4 per riga
        for i, url in enumerate(video_urls):
            with cols[i % 4]:
                st.video(url)
                st.caption(f"Video {i+1}")


# Esegui home (Streamlit gestisce multi-page automaticamente)
home_page()