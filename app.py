import streamlit as st
import pandas as pd
import base64
import os

# --- 1. KONFIGURATION ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

st.markdown("""
    <style>
    .winner-box { text-align: center; border: 15px solid #1a4a9e; padding: 40px; background-color: white; border-radius: 50px; box-shadow: 0px 15px 40px rgba(0,0,0,0.15); margin: 20px auto; max-width: 900px; }
    .stButton>button { border-radius: 12px; height: 3em; font-weight: bold; background-color: #1a4a9e; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATEN LADEN (Angepasst an deine Excel-Struktur) ---
@st.cache_data(ttl=30)
def load_data():
    try:
        # Deine Datei hat in Zeile 1 (Index 0) leere Felder, Header ist in Zeile 2 (Index 1)
        df = pd.read_excel("LABELS.xlsm", engine='openpyxl', header=1)
        # Spaltennamen bereinigen
        df.columns = df.columns.astype(str).str.strip()
        # Inhalte bereinigen
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Excel-Fehler: {e}")
        return None

df_full = load_data()

# --- 3. LOGIN ---
CREDENTIALS = {"admin": "Burgdorf26", "steward": "ring26", "monitor": "hallenaufl"}
if 'auth' not in st.session_state: st.session_state.auth = None

if st.session_state.auth is None:
    st.title("🐾 Burgdorf 2026 - KECB Login")
    with st.form("login"):
        pw = st.text_input("Passwort", type="password")
        if st.form_submit_button("Anmelden"):
            if pw in CREDENTIALS.values():
                st.session_state.auth = [k for k, v in CREDENTIALS.items() if v == pw][0]
                st.rerun()
            st.error("Falsches Passwort")
    st.stop()

if df_full is None:
    st.error("Konnte LABELS.xlsm nicht laden.")
    st.stop()

# --- 4. TAGES-LOGIK ---
selected_tag = st.sidebar.radio("Tag wählen", ["Tag 1", "Tag 2"])

# Filter: Nur Katzen, die am gewählten Tag ein 'X' haben
if selected_tag in df_full.columns:
    df = df_full[df_full[selected_tag].str.upper() == 'X'].copy()
else:
    st.error(f"Spalte '{selected_tag}' nicht gefunden! Vorhanden: {list(df_full.columns)}")
    st.stop()

# --- 5. NAVIGATION ---
menu = ["Katzenaufruf", "BIS-Regie", "Gewinner-Slide"]
view = st.sidebar.radio("Menü", menu)

if view == "Katzenaufruf":
    st.title(f"📢 Aufruf - {selected_tag}")
    # Spaltenname für Richter je nach Tag wählen
    richter_col = "Richter Tag 1" if selected_tag == "Tag 1" else "Richter Tag 2"
    
    if richter_col in df.columns:
        r_list = sorted([r for r in df[richter_col].unique() if r != "nan"])
        r_wahl = st.selectbox("Richter / Ring", r_list)
        
        cats = df[df[richter_col] == r_wahl].sort_values('Katalog-Nr')
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Katzen im Ring")
            for _, cat in cats.iterrows():
                st.markdown(f"**Nr. {cat['Katalog-Nr']}** - {cat['Rasse']} ({cat['Ausstellungsklasse']})")
        with col2:
            st.subheader("Großanzeige")
            nr = st.text_input("Käfignummer für Aufruf")
            if nr:
                st.markdown(f"<div style='font-size:100px; color:red; text-align:center; border:5px solid red;'>RING {r_wahl}:<br>{nr}</div>", unsafe_allow_html=True)
    else:
        st.warning(f"Spalte '{richter_col}' nicht gefunden.")

elif view == "BIS-Regie":
    st.title("🏆 Best in Show")
    # In deiner Datei heißt die Spalte 'SELECTION'
    if 'SELECTION' in df.columns:
        bis_cats = df[df['SELECTION'].str.upper() == 'X']
        if not bis_cats.empty:
            cols = st.columns(len(bis_cats))
            for i, (idx, cat) in enumerate(bis_cats.iterrows()):
                with cols[i]:
                    if st.button(f"SIEG Nr. {cat['Katalog-Nr']}", key=idx):
                        st.session_state.sieger = cat['Katalog-Nr']
                        st.balloons()
        else:
            st.info("Keine Katzen mit 'X' in Spalte 'SELECTION' markiert.")
    else:
        st.error("Spalte 'SELECTION' fehlt.")

elif view == "Gewinner-Slide":
    if st.session_state.get('sieger'):
        s_id = st.session_state.sieger
        row = df[df['Katalog-Nr'] == s_id].iloc[0]
        st.markdown(f"""
            <div class="winner-box">
                <h1 style="font-size:200px; color:#1a4a9e;">{s_id}</h1>
                <h2 style="font-size:60px;">{row['Name']}</h2>
                <p style="font-size:30px;">{row['Rasse']} | {row['Farbe']}</p>
                <p style="font-size:25px;">Besitzer: {row['Besitzer Nachname']}</p>
            </div>
            """, unsafe_allow_html=True)
        if st.button("Reset"):
            st.session_state.sieger = None
            st.rerun()
    else:
        st.title("Warten auf die Jury...")
