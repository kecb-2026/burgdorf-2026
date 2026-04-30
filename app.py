import streamlit as st
import pandas as pd
from collections import Counter
import base64
import os

st.set_page_config(layout="wide", page_title="Burgdorf 2026 - KECB Cat Show", page_icon="🐾")

st.markdown(\"\"\"
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #1a4a9e; color: white; font-weight: bold; font-size: 1.1em; border: none; }
    .stButton>button:hover { background-color: #153a7a; color: white; }
    .winner-box { text-align: center; border: 15px solid #1a4a9e; padding: 40px; background-color: white; border-radius: 50px; box-shadow: 0px 15px 40px rgba(0,0,0,0.15); margin: 20px auto; max-width: 900px; }
    </style>
    \"\"\", unsafe_allow_html=True)

@st.cache_data(ttl=30)
def load_data():
    try:
        df = pd.read_excel("LABELS.xlsm", engine='openpyxl')
        for col in df.columns: df[col] = df[col].astype(str).str.strip()
        if 'Selection' in df.columns:
            df['is_bis_nom'] = df['Selection'].str.upper() == 'X'
        else:
            df['is_bis_nom'] = False
        return df
    except: return None

df_full = load_data()
if df_full is None:
    st.error("LABELS.xlsm fehlt!")
    st.stop()

CREDENTIALS = {"admin": "Burgdorf26", "steward": "ring26", "monitor": "hallenaufl"}
if 'auth' not in st.session_state: st.session_state.auth = None

if st.session_state.auth is None:
    pw = st.text_input("Passwort", type="password")
    if st.button("Login"):
        for role, cred in CREDENTIALS.items():
            if pw == cred: st.session_state.auth = role; st.rerun()
    st.stop()

tag = st.sidebar.radio("Tag", ["1", "2"])
df = df_full[df_full['Tag'] == tag]
view = st.sidebar.radio("Menü", ["BIS-Regie", "Ring-Regie", "Gewinner-Slide", "Steward-Tablett"])

if view == "BIS-Regie":
    st.title("🏆 BIS Regie (X-Logik)")
    bis_cats = df[df['is_bis_nom'] == True]
    for i, cat in bis_cats.iterrows():
        if st.button(f"Sieg für {cat['Käfignummer']}", key=i):
            st.session_state.sieger = cat['Käfignummer']
            st.session_state.titel = "BEST IN SHOW"
            st.balloons()

elif view == "Gewinner-Slide":
    if st.session_state.get('sieger'):
        s_id = st.session_state.sieger
        info = df[df['Käfignummer'] == s_id].iloc[0]
        st.markdown(f'<div class="winner-box"><h1>{s_id}</h1><h2>{info["Katzenname"]}</h2><p>{info["Besitzer"]}</p></div>', unsafe_allow_html=True)
        if st.button("Reset"): st.session_state.sieger = None; st.rerun()
    else: st.title("Warten auf Jury...")

elif view == "Steward-Tablett":
    st.title("📋 Ring-Nomination")
    r_wahl = st.selectbox("Richter", sorted(df['Richter'].unique()))
    noms = st.multiselect("Nominiert", sorted(df[df['Richter']==r_wahl]['Käfignummer'].unique()))
    if st.button("Speichern"): st.success("Übertragen!")
