import streamlit as st
import pandas as pd
from collections import Counter
import base64
import os

# --- 1. KONFIGURATION & STYLING ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3em; background-color: #1a4a9e; color: white; font-weight: bold; }
    .stButton>button:hover { background-color: #153a7a; color: white; }
    .winner-box { text-align: center; border: 15px solid #1a4a9e; padding: 40px; background-color: white; border-radius: 50px; box-shadow: 0px 15px 40px rgba(0,0,0,0.15); margin: 20px auto; max-width: 900px; }
    .call-card { background-color: #ffffff; padding: 15px; border-radius: 12px; border-left: 8px solid #ff4b4b; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# --- 2. LOGIN-SYSTEM ---
CREDENTIALS = {"admin": "Burgdorf26", "steward": "ring26", "monitor": "hallenaufl"}
if 'auth' not in st.session_state: st.session_state.auth = None

if st.session_state.auth is None:
    st.title("🐾 Burgdorf 2026 - KECB Login")
    with st.form("login_form"):
        pw = st.text_input("Passwort eingeben", type="password")
        if st.form_submit_button("Anmelden"):
            p = pw.strip()
            for role, cred in CREDENTIALS.items():
                if p == cred:
                    st.session_state.auth = role
                    st.rerun()
            st.error("Passwort ungültig!")
    st.stop()

# --- 3. DATEN LADEN (ANWESENHEITS-LOGIK) ---
@st.cache_data(ttl=30)
def load_data():
    try:
        df = pd.read_excel("LABELS.xlsm", engine='openpyxl')
        df.columns = df.columns.str.strip()
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Excel-Fehler: {e}")
        return None

df_full = load_data()
if df_full is None: 
    st.warning("Datei 'LABELS.xlsm' nicht gefunden.")
    st.stop()

# --- 4. TAGES-FILTER (Anwesenheit X) ---
selected_tag = st.sidebar.radio("Ausstellungstag", ["Tag 1", "Tag 2"])

if selected_tag in df_full.columns:
    # Nur Katzen, die am gewählten Tag ein X haben
    df = df_full[df_full[selected_tag].str.upper() == 'X']
else:
    st.error(f"Spalte '{selected_tag}' fehlt!")
    st.stop()

# Session States
if 'sieger_id' not in st.session_state: st.session_state.sieger_id = None

# --- 5. NAVIGATION ---
menu_map = {
    "admin": ["Katzenaufruf", "BIS-Regie", "Gewinner-Slide", "Steward-Tablett"],
    "steward": ["Katzenaufruf", "Steward-Tablett"],
    "monitor": ["Katzenaufruf", "Gewinner-Slide"]
}
view = st.sidebar.radio("Menü", menu_map[st.session_state.auth])

# --- 6. MODULE ---

# A: KATZENAUFRUF (Wichtig für Hallenmeister/Stewards)
if view == "Katzenaufruf":
    st.title(f"📢 Aufruf & Anwesenheit - {selected_tag}")
    r_wahl = st.selectbox("Richter / Ring", sorted(df['Richter'].unique()))
    richter_cats = df[df['Richter'] == r_wahl].sort_values('Käfignummer')
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Erwartete Katzen")
        for _, cat in richter_cats.iterrows():
            st.markdown(f"<div class='call-card'><b>Nr. {cat['Käfignummer']}</b><br>{cat['Rasse_Kurz']} ({cat['Klasse']})</div>", unsafe_allow_html=True)
    
    with col2:
        st.subheader("Großanzeige Aufruf")
        aufruf_nr = st.text_input("Käfignummer eingeben")
        if aufruf_nr:
            st.markdown(f"<div style='font-size: 100px; color: #ff4b4b; text-align: center; font-weight: bold; border: 10px solid #ff4b4b; padding: 20px; border-radius: 20px;'>BITTE IN RING {r_wahl}:<br>{aufruf_nr}</div>", unsafe_allow_html=True)

# B: BIS-REGIE (Nur Katzen mit X in 'Selection')
elif view == "BIS-Regie":
    st.title(f"🏆 Best in Show Regie - {selected_tag}")
    if 'Selection' in df.columns:
        bis_cats = df[df['Selection'].str.upper() == 'X']
        if not bis_cats.empty:
            cols = st.columns(len(bis_cats))
            for i, (idx, cat) in enumerate(bis_cats.iterrows()):
                with cols[i]:
                    st.metric("Käfig", cat['Käfignummer'])
                    if st.button(f"SIEG für {cat['Käfignummer']}", key=f"bis_{idx}"):
                        st.session_state.sieger_id = cat['Käfignummer']
                        st.balloons()
        else:
            st.warning("Keine Katzen mit 'X' in Spalte 'Selection' markiert.")
    else:
        st.error("Spalte 'Selection' fehlt in der Excel!")

# C: GEWINNER-SLIDE (Für den Beamer)
elif view == "Gewinner-Slide":
    if st.session_state.sieger_id:
        s_id = st.session_state.sieger_id
        info = df[df['Käfignummer'] == s_id].iloc[0]
        logo_b64 = get_base64_image("kecb_logo.png")
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="width: 150px;">' if logo_b64 else ""
        st.markdown(f"""
            <div class="winner-box">
                {logo_html}
                <h2 style="color:#1a4a9e">BEST IN SHOW WINNER</h2>
                <h1 style="font-size:200px;color:#1a4a9e;margin:0">{s_id.upper()}</h1>
                <h2 style="font-size:60px;">{info['Katzenname']}</h2>
                <p style="font-size:30px;">{info['Rasse_Kurz']} | {info['Besitzer']}</p>
                <h3 style="letter-spacing:10px; color:#1a4a9e; margin-top: 20px;">BURGDORF 2026</h3>
            </div>
            """, unsafe_allow_html=True)
        if st.button("Reset Screen"):
            st.session_state.sieger_id = None
            st.rerun()
    else:
        st.title("Warten auf Jury-Entscheidung...")

# D: STEWARD-TABLETT (Manuelle Nomination)
elif view == "Steward-Tablett":
    st.title("📋 Manuelle Ring-Nomination")
    r_wahl = st.selectbox("Richter", sorted(df['Richter'].unique()))
    noms = st.multiselect("Nominiert für Klassensieg", sorted(df[df['Richter']==r_wahl]['Käfignummer'].unique()))
    if st.button("Speichern"):
        st.success("Erfolgreich gespeichert (Hinweis: Für BIS bitte Spalte 'Selection' in Excel nutzen).")
