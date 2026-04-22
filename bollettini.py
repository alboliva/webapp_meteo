import streamlit as st
import os
from datetime import datetime

st.set_page_config(page_title="Bollettini Meteo", layout="wide", page_icon="📄")

# ─── CONFIGURAZIONE ──────────────────────────────────────────────────────────
# Cartella dove metti i bollettini HTML (relativa alla root del progetto)
_HERE         = os.path.dirname(os.path.abspath(__file__))
_ROOT         = os.path.dirname(_HERE)
BOLLETTINI_DIR = os.path.join(_ROOT, "bollettini")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@400;500;600&display=swap');

.boll-header {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem;
    color: #0f172a;
    letter-spacing: -0.02em;
    margin-bottom: 0;
}
.boll-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.78rem;
    font-weight: 500;
    color: #94a3b8;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
    margin-top: 4px;
}
.boll-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 10px;
    cursor: pointer;
    font-family: 'DM Sans', sans-serif;
}
.boll-card:hover { background: #f1f5f9; }
.boll-date {
    font-size: 0.65rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
}
.boll-title { font-size: 0.95rem; font-weight: 600; color: #0f172a; }
.how-to {
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 10px;
    padding: 14px 18px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.84rem;
    color: #0c4a6e;
    line-height: 1.7;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="boll-header">📄 Bollettini Meteo</div>', unsafe_allow_html=True)
st.markdown('<div class="boll-sub">Previsioni scientifiche · Roma, Lazio, Abruzzo</div>', unsafe_allow_html=True)

# ─── ISTRUZIONI SE CARTELLA NON ESISTE ───────────────────────────────────────
if not os.path.exists(BOLLETTINI_DIR):
    os.makedirs(BOLLETTINI_DIR, exist_ok=True)
    st.markdown(f"""
    <div class="how-to">
    <strong>Come aggiungere bollettini:</strong><br>
    1. Crea la cartella <code>bollettini/</code> nella root del progetto (creata automaticamente).<br>
    2. Salva ogni bollettino come file HTML con nome nel formato <code>YYYYMMDD_bollettino.html</code><br>
       &nbsp;&nbsp;&nbsp;Esempio: <code>20260422_bollettino.html</code><br>
    3. La pagina mostrerà automaticamente tutti i file presenti, dal più recente.<br><br>
    <strong>Formato consigliato:</strong> HTML generato da Pandoc (come il tuo bollettino attuale) — 
    viene visualizzato direttamente in-page senza plugin aggiuntivi.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─── LISTA BOLLETTINI DISPONIBILI ────────────────────────────────────────────
files = sorted(
    [f for f in os.listdir(BOLLETTINI_DIR) if f.lower().endswith(".html")],
    reverse=True   # più recente prima
)

if not files:
    st.markdown(f"""
    <div class="how-to">
    <strong>Nessun bollettino trovato.</strong><br>
    Aggiungi file HTML nella cartella <code>bollettini/</code> (root del progetto).<br>
    Nome consigliato: <code>YYYYMMDD_bollettino.html</code> — es. <code>20260422_bollettino.html</code>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─── SELEZIONE + VISUALIZZAZIONE ─────────────────────────────────────────────
col_list, col_view = st.columns([1, 3])

with col_list:
    st.markdown("**Archivio**")
    selected = st.radio(
        label="Scegli bollettino",
        options=files,
        format_func=lambda f: _format_filename(f),
        label_visibility="collapsed",
    )

def _format_filename(fname):
    """Cerca di estrarre la data dal nome file e la formatta."""
    base = fname.replace(".html","").replace("_bollettino","").replace("_meteo","")
    try:
        dt = datetime.strptime(base[:8], "%Y%m%d")
        return dt.strftime("%d %b %Y")
    except:
        return fname

with col_view:
    if selected:
        filepath = os.path.join(BOLLETTINI_DIR, selected)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Inietta CSS aggiuntivo per adattare il bollettino alla larghezza della colonna
            inject = """
            <style>
            body { max-width: 100% !important; padding: 20px 30px !important; font-size: 0.95rem; }
            img  { max-width: 100% !important; height: auto !important; }
            table { width: 100% !important; font-size: 0.85rem; }
            </style>
            """
            html_content = html_content.replace("</head>", inject + "</head>")

            st.components.v1.html(html_content, height=900, scrolling=True)

            # Bottone download
            st.download_button(
                label="⬇️ Scarica HTML",
                data=html_content.encode("utf-8"),
                file_name=selected,
                mime="text/html",
            )
        except Exception as e:
            st.error(f"Errore caricamento: {e}")