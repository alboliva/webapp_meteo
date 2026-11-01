"""
Pagina amministrazione — raggiungibile solo da URL diretto (/nimda), non compare nel menu.
Password: "teresina" (si può cambiare con admin_password in .streamlit/secrets.toml).
"""

import hmac

import pandas as pd
import streamlit as st

from common import STAZIONI, fetch_current, fetch_storico

DEFAULT_PWD = "teresina"


def _password():
    try:
        return st.secrets.get("admin_password", DEFAULT_PWD)
    except Exception:
        return DEFAULT_PWD


# ─── LOGIN ───────────────────────────────────────────────────────────────────
ss = st.session_state
if not ss.get("admin_ok"):
    st.markdown("## 🔒 Area riservata")
    with st.form("login", border=True):
        pwd = st.text_input("Password", type="password")
        if st.form_submit_button("Entra"):
            if hmac.compare_digest(pwd.encode(), _password().encode()):
                ss.admin_ok = True
                st.rerun()
            else:
                st.error("Password errata.")
    st.stop()

# ─── HEADER ──────────────────────────────────────────────────────────────────
h1, h2 = st.columns([6, 1])
h1.markdown("## 🛠️ Amministrazione")
if h2.button("Esci", width="stretch"):
    ss.admin_ok = False
    st.rerun()

dati = fetch_current(STAZIONI)

# ═══ STORICO TEMPERATURE (Archive API) — solo admin ═══
st.markdown("### 📈 Storico Temperature (Archive API)")
st.caption("Dati orari storici da Open-Meteo Archive — fino a ieri, fino a 90 giorni.")
col_sel, col_opt = st.columns([2, 1])
with col_sel:
    nomi_tutti = [d["nome"] for d in dati if d.get("ok")] or [s[2] for s in STAZIONI]
    default_sel = [n for n in ["Roma Centro", "Campo Imperatore", "Tromsø", "Miami"] if n in nomi_tutti]
    sel_stazioni = st.multiselect("Seleziona stazioni (max 6)", nomi_tutti, default=default_sel,
                                  max_selections=6)
with col_opt:
    giorni = st.select_slider("Periodo", options=[7, 14, 30, 60, 90], value=30,
                              format_func=lambda x: f"{x} giorni")
    risoluzione = st.radio("Risoluzione", ["Oraria", "Giornaliera"], horizontal=True)

if sel_stazioni:
    frames_h, frames_d = [], []
    with st.spinner(f"Caricamento dati storici ({giorni}gg)…"):
        for nome in sel_stazioni:
            s_info = next((d for d in dati if d["nome"] == nome), None)
            if not s_info:
                continue
            storico = fetch_storico(s_info["lat"], s_info["lon"], s_info["tz"], giorni)
            if "error" in storico:
                st.warning(f"{nome}: {storico['error']}")
                continue
            if risoluzione == "Oraria":
                frames_h.append(pd.DataFrame({"Ora": pd.to_datetime(storico["times"]),
                                              nome: storico["temp_h"]}).set_index("Ora"))
            else:
                frames_d.append(pd.DataFrame({"Data": pd.to_datetime(storico["dates"]),
                                              f"{nome} max": storico["tmax_d"],
                                              f"{nome} min": storico["tmin_d"]}).set_index("Data"))

    if risoluzione == "Oraria" and frames_h:
        st.line_chart(pd.concat(frames_h, axis=1).sort_index())
        st.caption(f"Temperatura oraria · {giorni} giorni · Fonte: Open-Meteo Archive")
    elif risoluzione == "Giornaliera" and frames_d:
        df_all = pd.concat(frames_d, axis=1).sort_index()
        t_max, t_min = st.tabs(["🔴 Massime giornaliere", "🔵 Minime giornaliere"])
        with t_max:
            cm = [c for c in df_all.columns if c.endswith(" max")]
            st.line_chart(df_all[cm].rename(columns=lambda c: c.replace(" max", "")))
        with t_min:
            cm = [c for c in df_all.columns if c.endswith(" min")]
            st.line_chart(df_all[cm].rename(columns=lambda c: c.replace(" min", "")))
        st.caption(f"Temperature giornaliere · {giorni} giorni · Fonte: Open-Meteo Archive")
else:
    st.info("Seleziona almeno una stazione.")
