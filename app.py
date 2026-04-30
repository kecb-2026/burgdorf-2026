import streamlit as st
import pandas as pd
from collections import Counter
import base64
import os

# --- 1. KONFIGURATION & STYLING ---
st.set_page_config(layout="wide", page_title="Burgdorf 2026 - KECB Cat Show", page_icon="🐾")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #1a4a9e; color: white; font-weight: bold; font-size: 1.1em; border: none; }
    .stButton>button:hover { background-color: #153a7a; color: white; }
    .winner-box { text-align: center; border: 15px solid #1a4a9e; padding: 40px; background-color: white; border-radius: 50px; box-shadow: 0px 15px 40px rgba(0,0,0,0.15); margin: 20px auto; max-width: 900px; }
    .judge-card { background-color: #ffffff; padding: 15px; border-radius: 12px; border-left: 8px solid #1a4a9e; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# --- 2. LOGIN-SYSTEM ---
CREDENTIALS = {"admin": "Burgdorf26", "richter": "judge26", "steward": "ring26", "monitor": "hallenaufl"}
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

# --- 3. DATEN LADEN (MIT BIS-X-LOGIK) ---
@st.cache_data(ttl=30)
def load_data():
    try:
        df = pd.read_excel("LABELS.xlsm", engine='openpyxl')
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        
        if 'Selection' in df.columns:
            df['is_bis_nom'] = df['Selection'].str.upper() == 'X'
        else:
            df['is_bis_nom'] = False
        return df
    except Exception as e:
        st.error(f"Excel-Fehler: {e}")
        return None

df_full = load_data()
if df_full is None: 
    st.warning("Bitte stelle sicher, dass 'LABELS.xlsm' im Verzeichnis liegt.")
    st.stop()

# Filter & State
selected_tag = st.sidebar.radio("Tag", ["1", "2"])
df = df_full[df_full['Tag'] == selected_tag]

if 'rings' not in st.session_state:
    st.session_state.rings = {r: {"nom": []} for r in df_full['Richter'].unique()}
if 'sieger_id' not in st.session_state: st.session_state.sieger_id = None
if 'akt_kl' not in st.session_state: st.session_state.akt_kl = ""

# --- 4. NAVIGATION ---
menu_map = {
    "admin": ["BIS-Regie", "Ring-Regie", "Gewinner-Slide", "Steward-Tablett"],
    "richter": ["BIS-Regie", "Ring-Regie"],
    "steward": ["Steward-Tablett"],
    "monitor": ["Gewinner-Slide"]
}
view = st.sidebar.radio("Menü", menu_map[st.session_state.auth])

# --- 5. BEREICHE ---

if view == "BIS-Regie":
    st.title("🏆 Best in Show - Regie (X-Logik)")
    bis_cats = df[df['is_bis_nom'] == True]
    if not bis_cats.empty:
        cols = st.columns(len(bis_cats))
        for i, (idx, cat) in enumerate(bis_cats.iterrows()):
            with cols[i]:
                st.subheader(f"Nr. {cat['Käfignummer'].upper()}")
                if st.button(f"Sieg: {cat['Käfignummer']}", key=f"bis_{idx}"):
                    st.session_state.sieger_id = cat['Käfignummer']
                    st.session_state.akt_kl = "BEST IN SHOW"
                    st.balloons()
    else:
        st.warning("Keine BIS-Nominationen (X) in der Excel gefunden.")

elif view == "Gewinner-Slide":
    if st.session_state.sieger_id:
        s_id = st.session_state.sieger_id
        info = df[df['Käfignummer'] == s_id].iloc[0]
        logo_b64 = get_base64_image("kecb_logo.png")
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="width: 150px;">' if logo_b64 else ""
        st.markdown(f"""
            <div class="winner-box">
                {logo_html}
                <h2 style="color:#1a4a9e">{st.session_state.akt_kl}</h2>
                <h1 style="font-size:180px;color:#1a4a9e;margin:0">{s_id.upper()}</h1>
                <h2 style="font-size:50px;">{info['Katzenname']}</h2>
                <p style="font-size:25px;">{info['Rasse_Kurz']} | {info['Besitzer']}</p>
                <h3 style="letter-spacing:8px; color:#1a4a9e;">BURGDORF 2026</h3>
            </div>
            """, unsafe_allow_html=True)
        if st.button("Reset Screen"):
            st.session_state.sieger_id = None
            st.rerun()
    else:
        st.title("Warten auf die Jury...")

elif view == "Steward-Tablett":
    st.title("📋 Ring-Nomination")
    r_wahl = st.selectbox("Richter", sorted(df['Richter'].unique()))
    k_ring = df[df['Richter'] == r_wahl]
    noms = st.multiselect("Nominiert", sorted(k_ring['Käfignummer'].unique()))
    if st.button("Speichern"):
        st.session_state.rings[r_wahl]["nom"] = [{"nr": n, "kl": df[df['Käfignummer']==n].iloc[0]['Klasse']} for n in noms]
        st.success("An Regie übertragen!")

elif view == "Ring-Regie":
    st.title("🏆 Ring-Regie (Klassensieger)")
    r_all = sorted(df['Richter'].unique())
    for r in r_all:
        for n in st.session_state.rings[r]["nom"]:
            if st.button(f"Sieg für Nr. {n['nr']} (Richter {r})", key=f"ring_{r}_{n['nr']}"):
                st.session_state.sieger_id = n['nr']
                st.session_state.akt_kl = f"KLASSENSIEGER (KL. {n['kl']})"
                st.balloons()
