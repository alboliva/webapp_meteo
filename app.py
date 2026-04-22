import streamlit as st
import requests
from datetime import datetime, timedelta, timezone
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import os

# =============================================================================
# CONFIGURAZIONE
# =============================================================================

st.set_page_config(
    page_title="Meteo Rismi",
    layout="wide",
    page_icon="🌤️",
    initial_sidebar_state="expanded"
)

# =============================================================================
# BOLLETTINI METEO
# =============================================================================

st.subheader("📄 Bollettino Meteo")

BOLLETTINI_DIR = os.path.join(os.getcwd(), "bollettini")

if os.path.exists(BOLLETTINI_DIR):
    files = sorted(
        [f for f in os.listdir(BOLLETTINI_DIR) if f.lower().endswith(".html")],
        reverse=True   # più recente prima
    )

    if files:
        def fmt_bollettino(fname):
            base = fname.replace(".html", "")
            for i in range(len(base) - 7):
                chunk = base[i:i+8]
                if chunk.isdigit():
                    try:
                        return datetime.strptime(chunk, "%Y%m%d").strftime("%d %b %Y")
                    except:
                        pass
            return fname

        selected = st.selectbox(
            "Seleziona bollettino",
            options=files,
            format_func=fmt_bollettino
        )

        filepath = os.path.join(BOLLETTINI_DIR, selected)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Adatta larghezza al container Streamlit
            inject = """
<style>
body {
    max-width: 100% !important;
    padding: 20px 30px !important;
    font-size: 0.93rem;
}
img  { max-width: 100% !important; height: auto !important; }
table { width: 100% !important; font-size: 0.85rem; }
</style>"""
            html_content = html_content.replace("</head>", inject + "\n</head>")

            st.components.v1.html(html_content, height=900, scrolling=True)

            st.download_button(
                label="⬇️ Scarica bollettino HTML",
                data=html_content.encode("utf-8"),
                file_name=selected,
                mime="text/html"
            )

        except Exception as e:
            st.error(f"Errore apertura file: {e}")

    else:
        st.info("Nessun bollettino trovato nella cartella `bollettini/`. Aggiungi file HTML con nome `YYYYMMDD_bollettino.html`.")

else:
    st.info(
        f"Crea la cartella `bollettini/` nella root del progetto e inserisci i file HTML.\n\n"
        f"Path cercato: `{BOLLETTINI_DIR}`"
    )