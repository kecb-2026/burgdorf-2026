
# -*- coding: utf-8 -*-

"""
Projekt: Cat Show App der KECB Katzenausstellung
Copyright (c) 2026 Brigitte Portner
Alle Rechte vorbehalten
"""




import streamlit as st
import pandas as pd
import re
import time
from streamlit_autorefresh import st_autorefresh
import qrcode
from io import BytesIO

# --- 1. SETUP & STYLING ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

# Zentrale Logo URL
LOGO_URL = "logo_kecb.png"

st.markdown("""
    <style>
    @keyframes blinker { 50% { opacity: 0.1; } }
    @keyframes fadeIn { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }

@keyframes flashGreen {
    0% { background-color: #1a4a9e; }
    50% { background-color: #28a745; }
    100% { background-color: #1a4a9e; }
}

	.voted-flash {
    		animation: flashGreen 2s ease-in-out;
	}
    /* Greift NUR noch auf die Buttons im Home-Menü zu: */
    .home-buttons div.stButton > button {
        width: 100% !important;
        height: 50px !important;
        background-color: #1a4a9e !important; /* Feste blaue Hintergrundfarbe */
        color: white !important; /* Weiße Schrift auf blauem Grund */
    }

    /* Login Container */
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px;
        background-color: #f8f9fa;
        border-radius: 20px;
        border: 2px solid #1a4a9e;
        max-width: 400px;
        margin: 5% auto;
    }

    /* Erzeugt einheitliche Höhen für alle Boxen in einer Zeile */
    .grid-wrapper {
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    /* --- STEWARD CARDS STYLES (ORIGINAL WIEDERHERGESTELLT) --- */
    /* Der Kasten umschließt jetzt das Meta-Grid UND die Buttons */
    .steward-card-wrapper {
        background-color: #f8f9fa !important; /* Karte komplett hellgrau */
        border: 1px solid #dcdcdc !important;
        border-radius: 12px !important;
        padding: 16px 16px 12px 16px !important;
        margin-bottom: 25px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    }
    
    .steward-card-wrapper.gerichtet {
        border: 1px dashed #cccccc !important;
        opacity: 0.6 !important;
    }
    
    .card-header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 2px solid #1a4a9e;
        padding-bottom: 6px;
        margin-bottom: 12px;
    }
    .card-cat-number {
        font-size: 22px !important;
        font-weight: 800;
        color: #1a4a9e;
    }
    .card-meta-main {
        font-size: 15px !important;
        font-weight: 700;
        color: #222;
    }
    .grid-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6px 12px;
        margin-bottom: 12px;
    }
    .card-meta-sub {
        font-size: 13px !important;
        color: #555;
    }
    .meta-label {
        font-weight: 600;
        color: #666;
        text-transform: uppercase;
        font-size: 11px !important;
        letter-spacing: 0.5px;
    }

    /* --- GLOBALE BUTTONS (DASHBOARD) --- */
    div.stButton > button, .stButton button {
        width: 100% !important;
        height: 50px !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
        font-size: 12px !important;
        transition: all 0.2s ease;
        margin-bottom: 5px;
        border: 2px solid #1a4a9e !important;
        color: white !important;
    }

    /* --- BUTTONS SPEZIFISCH IM STEWARD PANEL VERKLEINERN --- */
    div[data-testid="stHorizontalBlock"] div.stButton > button {
        height: 35px !important;
        min-height: 35px !important;
        min-width: 100px !important;
        padding: 0px 5px !important;
        font-size: 8px !important;
        line-height: 1 !important;
        border-radius: 8px !important;
    }

    /* Spalten-spezifische Button-Farben für das Steward-Pult */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
        background-color: #007bff !important;
        border: 2px solid #0056b3 !important;
        color: white !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
        background-color: #28a745 !important;
        border: 2px solid #1e7e34 !important;
        color: white !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {
        background-color: #ffc107 !important;
        border: 2px solid #d39e00 !important;
        color: black !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(4) button {
        background-color: #6c757d !important;
        border: 2px solid #545b62 !important;
        color: white !important;
    }

    /* Hover Effekte */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button:hover { background-color: #0069d9 !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button:hover { background-color: #218838 !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button:hover { background-color: #e0a800 !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(4) button:hover { background-color: #5a6268 !important; }

    /* Blinken für aktive Container-Wrapper im Python-Code */
    .button-class button, .st-blink-btn button, .blink-active button {
        animation: blinker 1.3s linear infinite !important;
        box-shadow: 0 0 15px rgba(0,0,0,0.2) !important;
    }

    /* Dashboard & Richter-Layout Styles */
    .judge-header-box { 
        background-color: #1a4a9e; color: white; padding: 8px; border-radius: 10px; text-align: center; 
        font-size: 12px !important; text-transform: uppercase; font-weight: bold; 
        margin-bottom: 10px; border: 2px solid #0d2a5e; height: 60px; 
        display: flex; align-items: center; justify-content: center; 
    }
    
    .class-label-box { 
        background-color: #e9ecef; color: #1a4a9e; padding: 5px; border-radius: 10px; text-align: center; 
        font-size: 11px !important; text-transform: uppercase; font-weight: 800; 
        border: 2px solid #1a4a9e; display: flex; align-items: center; justify-content: center; 
        height: 90px; width: 100%; line-height: 1.1; 
    }

    .cat-card, .placeholder-box { height: 95px; padding: 5px; border: 2px solid #1a4a9e; text-align: center; background-color: #f0f0f0; border-radius: 14px; margin-bottom: 5px; min-height: 90px; display: flex; flex-direction: column; justify-content: center; align-items: center; }
    .placeholder-box { height: 95px; border: 1px solid #d1d1d1; background-color: #f2f2f2 !important; color: #999999; }
    .winner-card { height: 99px; border: 1px solid #ff4d4d !important; background-color: #ffcccc !important; color: #b21f2d !important; }
    .cat-number { font-size: 28px !important; font-weight: 900 !important; color: #1a4a9e; line-height: 1.0; }
    .cat-details { font-size: 14px !important; color: #333; font-weight: bold; margin-top: 2px; line-height: 1.1; }

    /* Richter Initialen Kreise */
    .judge-initials-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 4px;
        margin-top: 8px;
        padding-top: 6px;
        border-top: 1px solid #eee;
    }
    .judge-circle {
        width: 24px;
        height: 24px;
        background-color: #008800;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
        font-weight: bold;
        cursor: help;
    }

    /* Overlay als zentrierte Box (80% Größe) */
    .winner-overlay {
        position: fixed;
        top: 10%; left: 10%; 
        width: 80vw; height: 80vh;
        background-color: white;
        z-index: 9999999;
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        text-align: center;
        border-radius: 40px;
        box-shadow: 0px 0px 100px rgba(0,0,0,0.5);
        border: 15px solid #1a4a9e;
        padding: 40px;
        animation: fadeIn 0.5s ease-out;
    }
    .overlay-backdrop {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: rgba(0,0,0,0.7);
        z-index: 9999998;
    }

    /* Titel Anpassungen Overlay */
    .ov-header {
        font-size: 24px !important; font-weight: 500; color: #333;
        text-transform: uppercase;
        border-bottom: 2px solid #ccc; width: 80%;
        padding-bottom: 15px; margin-bottom: 30px;
    }
    .ov-cat-name {
        font-size: 45px !important; font-weight: 900;
        text-transform: uppercase; color: #000;
        margin-bottom: 20px; line-height: 1.1;
        width: 90%; word-wrap: break-word;
    }
    .ov-owner {
        font-size: 30px !important; font-style: italic; color: #444;
    }
    
    /* Klasse für Hauptüberschriften neben dem Logo */
    .header-text {
        text-transform: uppercase !important;
        font-size: 26px !important;
        font-weight: bold;
        color: #1a4a9e;
        margin: 0 !important;
    }
    
    /* Tags */
    .tag-container { margin-top: 4px; display: flex; justify-content: center; flex-wrap: wrap; gap: 3px; }
    .tag { font-weight: bold; padding: 4px 8px; border-radius: 6px; font-size: 11px; text-transform: uppercase; color: white; }
    .tag-zumrichten { background-color: #007bff; }
    .tag-biv { background-color: #28a745; animation: blinker 1.5s linear infinite; }
    .tag-nom { background-color: #ffc107; color: black; animation: blinker 1s linear infinite; }

    /* --- ERGÄNZUNG: CSS ABSOLUT SPEZIFISCH AUF STEWARD-CARDS BESCHRÄNKEN --- */
    .steward-card-wrapper div[data-testid="stHorizontalBlock"] div.stButton > button {
        height: 25px !important;
        min-height: 25px !important;
        min-width: 10px !important;
        padding: 0px 5px !important;
        font-size: 8px !important;
        line-height: 1 !important;
        border-radius: 8px !important;
    }
                

    .steward-card-wrapper div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { background-color: #007bff !important; border: 2px solid #0056b3 !important; color: white !important; }
    .steward-card-wrapper div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { background-color: #28a745 !important; border: 2px solid #1e7e34 !important; color: white !important; }
    .steward-card-wrapper div[data-testid="stHorizontalBlock"] > div:nth-child(3) button { background-color: #ffc107 !important; border: 2px solid #d39e00 !important; color: black !important; }
    .steward-card-wrapper div[data-testid="stHorizontalBlock"] > div:nth-child(4) button { background-color: #6c757d !important; border: 2px solid #545b62 !important; color: white !important; }
    .steward-card-wrapper div[data-testid="stHorizontalBlock"] > div:nth-child(1) button:hover { background-color: #0069d9 !important; }
    .steward-card-wrapper div[data-testid="stHorizontalBlock"] > div:nth-child(2) button:hover { background-color: #218838 !important; }
    .steward-card-wrapper div[data-testid="stHorizontalBlock"] > div:nth-child(3) button:hover { background-color: #e0a800 !important; }
    .steward-card-wrapper div[data-testid="stHorizontalBlock"] > div:nth-child(4) button:hover { background-color: #5a6268 !important; }
    
        
</style>


</style>

    """, unsafe_allow_html=True)

# --- 2. GLOBALER SPEICHER ---
class GlobalStore:
    def __init__(self):
        self.data = {} 
        self.active_overlay = None
        self.overlay_start_time = 0

@st.cache_resource
def get_store():
    return GlobalStore()

store = get_store()


# --- 3. SESSION STATE & URL PARAMETER (FIXED: DAUERHAFT EINGELOGGT) ---
q_params = st.query_params

# 1. Prüfen, ob Zugangsdaten direkt in der URL stecken (Erzwingt das Login bei jedem Rerun)
if "auth" in q_params and q_params["auth"] == "true":
    st.session_state.authenticated = True
    st.session_state.user_role = q_params.get("role", "Public")
    
       # Falls eine bestimmte Ansicht in der URL steht, diese erzwingen
    if "view" in q_params:
        v_param = q_params["view"].lower()
        if v_param == "steward": st.session_state.view = "Steward_Panel"
        elif v_param == "richter": st.session_state.view = "Judge_Voting"
        elif v_param == "admin": st.session_state.view = "Home"
        elif v_param == "bis-admin": st.session_state.view = "BIS_Admin_Control"
        elif v_param == "qr": st.session_state.view = "QR_Codes"



# 2. Standard-Fallbacks, falls nichts in der URL steht
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = "Public"
if "view" not in st.session_state:
    st.session_state.view = "Dashboard"

# Falls man manuell über das Menü navigiert, ohne URL-Parameter zu verlieren
if "view" in q_params and not st.session_state.authenticated:
    v_param = q_params["view"].lower()
    if v_param == "katzenaufruf": st.session_state.view = "Dashboard"
    elif v_param == "bis": st.session_state.view = "BIS_Public"
    elif v_param in ["admin", "steward", "richter", "bis-admin"]:
        st.session_state.view = "Login"
        st.session_state.target_role = v_param
        

# NEU: Richter-Parameter aus der URL sichern, falls übergeben
if "judge" in q_params: 
    st.session_state.url_judge = q_params["judge"]
elif "url_judge" not in st.session_state: 
    st.session_state.url_judge = "--"


def logout():
    st.session_state.authenticated = False
    st.session_state.user_role = "Public"
    st.session_state.view = "Dashboard"
    st.query_params.clear() # Löscht die Login-Parameter aus der URL beim Logout
    st.rerun()


# --- 4. HILFSFUNKTIONEN ---
def display_header_with_logo(text):
    col_text, col_logo = st.columns([5, 1]) 
    with col_text:
        st.markdown(f"<p class='header-text'>{text}</p>", unsafe_allow_html=True)
    with col_logo:
        st.markdown("<div style='display: flex; justify-content: flex-end;'>", unsafe_allow_html=True)
        st.image(LOGO_URL, width=150)
        st.markdown("</div>", unsafe_allow_html=True)

def render_overlay_html(row):
    kat_nr = str(row.get('KATALOG-NR', '')).replace('.0', '')
    rasse = row.get('RASSE', '')
    farbe = row.get('FARBE', '')
    name_gross = str(row.get('NAME', '')).upper()
    besitzer = f"{row.get('BESITZER VORNAME', '')} {row.get('BESITZER NACHNAME', '')}"
    return f"""
        <div class="overlay-backdrop"></div>
        <div class="winner-overlay">
            <div class="ov-header">{kat_nr}. {rasse} {farbe}</div>
            <div class="ov-cat-name">{name_gross}</div>
            <div class="ov-owner">{besitzer}</div>
            <div style="margin-top: 50px;">
                
                <div style="font-weight: bold; font-size: 22px; color: #1a4a9e; margin-top: 10px;">KECB BURGDORF 2026</div>
            </div>
        </div>
    """

def roman_to_numeric(text):
    roman_map = {'IX': '9', 'VIII': '8', 'VII': '7', 'VI': '6', 'IV': '4', 'V': '5', 'III': '3', 'II': '2', 'I': '1'}
    if pd.isna(text) or text == "": return ""
    res = str(text).upper()
    for rom, num in roman_map.items():
        res = re.sub(rf'\b{rom}\b', num, res)
    return res

@st.cache_data(ttl=1)
def load_labels():
    try:
        df = pd.read_excel("LABELS.xlsx", engine='openpyxl', header=0)
        df.columns = [str(c).strip().upper() for c in df.columns]
        df['KLASSE_INTERNAL'] = df['AUSSTELLUNGSKLASSE'] if 'AUSSTELLUNGSKLASSE' in df.columns else df.get('KLASSE', '')
        if 'KATALOG-NR' in df.columns:
            df['KAT_STR'] = df['KATALOG-NR'].astype(str).str.replace('.0', '', regex=False)
        return df
    except:
        return None

def get_full_label(row):
    r = row.get('RASSE_KURZ', row.get('RASSE', ''))
    fg_col = [c for c in row.index if "FARBGRUPPE" in c or "FARB-GRUPPE" in c]
    fg_val = row[fg_col[0]] if fg_col else row.get('FARBGRUPPE', '')
    g = roman_to_numeric(fg_val)
    e = row.get('FARBE', '')
    return f"{r} {g} ({e})".strip() if g else f"{r} ({e})".strip()

def set_view(name):
    store.active_overlay = None   
    st.session_state.view = name
    st.rerun()


# --- 5. NAVIGATION & ZUGRIFF ---
access_map = {
    "Public": ["Dashboard", "BIS_Public", "Login"],
    "Richter": ["Judge_Voting", "Dashboard", "BIS_Public"],
    "Steward": ["Steward_Panel", "Dashboard", "BIS_Public"],
    "Admin": ["Home", "Dashboard", "BIS_Public", "Judge_Voting", "Steward_Panel", "BIS_Admin_Control", "Admin_Panel", "QR_Codes"]
}

available_views = access_map.get(st.session_state.user_role, ["Dashboard"])
st.sidebar.image(LOGO_URL, width=150)

st.session_state.view = st.sidebar.radio("Menü:", available_views, 
    index=available_views.index(st.session_state.view) if st.session_state.view in available_views else 0)
	
if st.session_state.view != "BIS_Public":
    store.active_overlay = None	

if st.session_state.authenticated:
    if st.sidebar.button("Abmelden"): logout()
elif st.session_state.view != "Login":
    if st.sidebar.button("🔒 Interner Login"): set_view("Login")

# --- Copyright Bereich ---
st.sidebar.markdown("---") # Trennlinie für saubere Optik
st.sidebar.markdown(
    """
    <div style="font-size: 0.8em; color: gray; text-align: center;">
        © 2026 Brigitte Portner<br>
        Alle Rechte vorbehalten.
    </div>
    """, 
    unsafe_allow_html=True
)
    
# --- 6. VIEWS ---

# LOGIN VIEW
if st.session_state.view == "Login":
    st.markdown("""
        <style>
        div.stButton > button {
            background-color: #ffffff !important;
            color: #1a4a9e !important;
            border: 2px solid #1a4a9e !important;
            border-radius: 10px !important;
            font-weight: bold !important;
            width: 100% !important;
            display: block !important;
            transition: all 0.2s ease-in-out;
        }
        div.stButton > button:hover {
            background-color: #1a4a9e !important;
            color: #ffffff !important;
        }
        .login-container {
            border: 2px solid #1a4a9e !important;
            border-radius: 15px;
            padding: 20px;
            background-color: transparent;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.image(LOGO_URL, width=150)
    st.markdown("<h2 style='text-align:center; color:#1a4a9e; text-transform: uppercase; font-size: 20px;'>Interner Bereich</h2>", unsafe_allow_html=True)
    
    role_map = {"admin": "Admin", "steward": "Steward", "richter": "Richter", "bis-admin": "Admin"}
    target = st.session_state.get("target_role", "Richter")
    role_list = ["Admin", "Steward", "Richter"]
    def_idx = role_list.index(role_map.get(target, "Richter"))

    role_input = st.selectbox("Rolle wählen:", role_list, index=def_idx)
    password = st.text_input("Passwort:", type="password")
    
    if st.button("Anmelden"):
        if role_input == "Admin" and password == "admin2026":
            st.session_state.user_role, st.session_state.authenticated = "Admin", True
            st.query_params.update(auth="true", role="Admin") 
            set_view("Home")
        elif role_input == "Steward" and password == "steward2026":
            st.session_state.user_role, st.session_state.authenticated = "Steward", True
            st.query_params.update(auth="true", role="Steward") 
            set_view("Steward_Panel")
        elif role_input == "Richter" and password == "judge2026":
            st.session_state.user_role, st.session_state.authenticated = "Richter", True
            st.query_params.update(auth="true", role="Richter") 
            set_view("Judge_Voting")
        else:
            st.error("Passwort ungültig.")
    
    if st.button("Abbrechen"): set_view("Dashboard")
    st.markdown("</div>", unsafe_allow_html=True)


# HOME (ADMIN NUR)
elif st.session_state.view == "Home":
    display_header_with_logo("🐾 KECB Burgdorf 2026")
    st.markdown('<div class="home-buttons">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📢 LIVE-DASHBOARD"):
            st.query_params.update({"view": "katzenaufruf"})
            set_view("Dashboard")
            st.rerun()
        if st.button("🏆 BEST IN SHOW (PUBLIC)"):
            st.query_params.update({"view": "bis"})
            set_view("BIS_Public")
            st.rerun()
        if st.button("🗳️ RICHTER-VOTING"):
            st.query_params.update({"view": "richter", "auth": "true", "role": "Richter"})
            set_view("Judge_Voting")
            st.rerun()
    with col2:
        if st.button("📝 STEWARD-PULT"):
            st.query_params.update({"view": "steward", "auth": "true", "role": "Steward"})
            set_view("Steward_Panel")
            st.rerun()
        if st.button("👨‍⚖️ BIS ADMIN / CONTROL"):
            st.query_params.update({"view": "bis-admin", "auth": "true", "role": "Admin"})
            set_view("BIS_Admin_Control")
            st.rerun()
        if st.button("⚙️ ADMIN-KONSOLE (RESET)"):
            st.query_params.update({"view": "admin", "auth": "true", "role": "Admin"})
            set_view("Admin_Panel")
            st.rerun()
            # NEU: Der Button für die QR-Zentrale direkt im Admin-Menü
        if st.button("📱 QR-CODE ZENTRALE"):
            st.query_params.update({"view": "qr", "auth": "true", "role": "Admin"})
            set_view("QR_Codes")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    st.subheader("⚙️ System-Einstellungen (Admin-Steuerung)")
    
    # 1. Richter-Fixierung
    if "steward_lock" not in st.session_state:
        st.session_state.steward_lock = True
    st.session_state.steward_lock = st.toggle(
        "Richter-Auswahl für Stewards sperren (Lockdown)", 
        value=st.session_state.steward_lock
    )

    # 2. Navigation-Sichtbarkeit
    if "show_nav" not in st.session_state:
        st.session_state.show_nav = True
    st.session_state.show_nav = st.toggle(
        "Haupt-Navigation für Stewards/Richter anzeigen", 
        value=st.session_state.show_nav
    )

# BIS ADMIN CONTROL
elif st.session_state.view == "BIS_Admin_Control":
    display_header_with_logo("👨‍⚖️ BIS Control Center")
    df_full = load_labels()
    if df_full is not None:
        sel_cat = st.selectbox("Kategorie verwalten:", sorted(df_full['KATEGORIE'].unique()))
        bis_defs = [("Adult Male", [1,3,5,7,9], "M"), ("Adult Female", [1,3,5,7,9], "W"), ("Neuter Male", [2,4,6,8,10], "M"), ("Neuter Female", [2,4,6,8,10], "W"), ("Junior 8-12 Male", [11], "M"), ("Junior 8-12 Female", [11], "W"), ("Kitten 4-8 Male", [12], "M"), ("Kitten 4-8 Female", [12], "W")]
        
        for label, klassen, geschl in bis_defs:
            with st.expander(f"KLASSE: {label}", expanded=True):
                c_ctrl, c_votes = st.columns([1, 1.2])
                v_prefix = f"v_{sel_cat}_{label}_"
                with c_ctrl:
                    st.markdown("**Steuerung**")
                    key_reveal = f"reveal_{sel_cat}_{label}"; key_winner_reveal = f"winner_reveal_{sel_cat}_{label}"; key_override = f"override_{sel_cat}_{label}"
                    store.data[key_reveal] = st.checkbox("Nominationen anzeigen", value=store.data.get(key_reveal, False), key=f"cb1_{key_reveal}")
                    store.data[key_winner_reveal] = st.checkbox("BIS Gewinner anzeigen", value=store.data.get(key_winner_reveal, False), key=f"cb2_{key_winner_reveal}")
                    pool = df_full[(df_full['SELECTION'].astype(str).str.upper() == 'X') & (df_full['KATEGORIE'] == sel_cat) & (df_full['KLASSE_INTERNAL'].isin(klassen)) & (df_full['GESCHLECHT'].astype(str).str.upper() == geschl)]
                    options = ["Automatisch (Stimmen)"] + sorted(pool['KAT_STR'].unique().tolist())
                    store.data[key_override] = st.selectbox(f"Gewinner festlegen:", options, index=options.index(store.data.get(key_override, "Automatisch (Stimmen)")) if store.data.get(key_override) in options else 0, key=f"sb_{key_override}")
                    
                    final_nr = None
                    if store.data[key_override] != "Automatisch (Stimmen)": final_nr = store.data[key_override]
                    elif "votes" in store.data:
                        vts = [v for k, v in store.data["votes"].items() if k.startswith(v_prefix) and v != "Keine Wahl"]
                        if vts: final_nr = pd.Series(vts).value_counts().index[0]
                    if final_nr and st.button(f"🏆 OVERLAY ZEIGEN (#{final_nr})", key=f"btn_ov_{sel_cat}_{label}"):
                        w_match = df_full[df_full['KAT_STR'] == str(final_nr)]
                        if not w_match.empty:
                            store.active_overlay = m_w = w_match.iloc[0].to_dict()
                            store.overlay_start_time = time.time()
                            if "local_overlay_end" in st.session_state:
                                st.session_state.local_overlay_end = 0
                        st.success(f"Overlay für #{final_nr} wurde gestartet!")
        
                with c_votes:
                    st.markdown("**Stimmen-Details**")
                    if "votes" in store.data:
                        current_votes = {k.replace(v_prefix, ""): v for k, v in store.data["votes"].items() if k.startswith(v_prefix) and v != "Keine Wahl"}
                        if current_votes:
                            vote_df = pd.DataFrame([{"Richter": r, "Wahl (Kat Nr.)": f"#{v}"} for r, v in current_votes.items()])
                            st.table(vote_df)
                            summary = pd.Series(current_votes.values()).value_counts()
                            st.write("**Zwischenstand:**")
                            for nr, count in summary.items(): st.write(f"Katze #{nr}: {count} Stimme(n)")

# BIS PUBLIC VIEW
# BIS PUBLIC VIEW NEW
# BIS PUBLIC VIEW NEW
elif st.session_state.view == "BIS_Public":
    if hasattr(store, 'active_overlay') and store.active_overlay:
        if time.time() - store.overlay_start_time < 20:
            st.markdown(render_overlay_html(store.active_overlay), unsafe_allow_html=True)
            time.sleep(1); st.rerun() 
        else: store.active_overlay = None; st.rerun()

    def get_initials(name):
        parts = str(name).split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return str(name)[:2].upper()

    display_header_with_logo("🏆 Best in Show")
    df_full = load_labels()
    
    if df_full is not None:
        # --- STABILE WIDGET-INITIALISIERUNG ---
        # Holt den exakten Zustand vor dem Rerun ab, damit nichts zurückspringt
        current_tag = st.session_state.get('bis_stable_tag', 'TAG 1')
        available_cats = sorted(df_full['KATEGORIE'].unique())
        current_cat = st.session_state.get('bis_stable_cat', available_cats[0])

        # Indices berechnen (Fallback auf 0, falls Werte beim Datenladen variieren)
        tag_index = ["TAG 1", "TAG 2"].index(current_tag) if current_tag in ["TAG 1", "TAG 2"] else 0
        cat_index = available_cats.index(current_cat) if current_cat in available_cats else 0

        # Widgets erzwingen den Zustand über den Index
        tag_selection = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"], index=tag_index)
        tag = tag_selection.upper()
        sel_cat = st.selectbox("Kategorie:", available_cats, index=cat_index)
        
        # Zustand sofort für den nächsten Durchlauf einfrieren
        st.session_state['bis_stable_tag'] = tag
        st.session_state['bis_stable_cat'] = sel_cat
        # --------------------------------------

        bis_defs = [
            ("Adult Male", [1,3,5,7,9], "M"), ("Adult Female", [1,3,5,7,9], "W"), 
            ("Neuter Male", [2,4,6,8,10], "M"), ("Neuter Female", [2,4,6,8,10], "W"), 
            ("Junior 8-12 Male", [11], "M"), ("Junior 8-12 Female", [11], "W"), 
            ("Kitten 4-8 Male", [12], "M"), ("Kitten 4-8 Female", [12], "W")
        ]
        
        r_col = f"RICHTER {tag}"
        judges = sorted([r for r in df_full[df_full[tag].astype(str).str.upper() == 'X'][r_col].unique() if str(r) != "nan"])

        # --- CSS-LOGIK FÜR GRÜNE RICHTER IM HEADER ---
        style_rules = ""
        for label, klassen, geschl in bis_defs:
            if not store.data.get(f"winner_reveal_{sel_cat}_{label}", False):
                prefix = f"v_{sel_cat}_{label}_"
                abgestimmte = [key.replace(prefix, "") for key, val in store.data.get("votes", {}).items() 
                               if key.startswith(prefix) and val != "Keine Wahl" and val != "Keine Wahl/Not chosen yet"]
                for j in abgestimmte:
                    style_rules += f".judge-{str(j).replace(' ', '_')} {{ background-color: #28a745 !important; }}"
        
        if style_rules:
            st.markdown(f"<style>{style_rules}</style>", unsafe_allow_html=True)

        # --- STATISCHER HEADER (oben, einmalig) ---
        cols = st.columns([0.8] + [1.2]*len(judges) + [0.8])
        cols[0].empty()
        for i, j in enumerate(judges):
            clean_id = str(j).replace(" ", "_")
            cols[i+1].markdown(f"<div class='judge-header-box judge-{clean_id}'>{j}</div>", unsafe_allow_html=True)
        cols[-1].markdown("<div class='judge-header-box' style='background-color:#b21f2d;'>BIS</div>", unsafe_allow_html=True)

        # --- KATZEN-ZEILEN ---
        for label, klassen, geschl in bis_defs:
            r_cols = st.columns([0.8] + [1.2]*len(judges) + [0.8])
            r_cols[0].markdown(f"<div class='class-label-box'>{label}</div>", unsafe_allow_html=True)
            
            show_noms = store.data.get(f"reveal_{sel_cat}_{label}", False)
            winner_revealed = store.data.get(f"winner_reveal_{sel_cat}_{label}", False)
            
            for i, j in enumerate(judges):
                with r_cols[i+1]:
                    if show_noms:
                        m = df_full[(df_full['SELECTION'].astype(str).str.upper() == 'X') & (df_full[r_col] == j) & (df_full['KATEGORIE'] == sel_cat) & (df_full['KLASSE_INTERNAL'].isin(klassen)) & (df_full['GESCHLECHT'].astype(str).str.upper() == geschl)]
                        if not m.empty:
                            kat_nr = m.iloc[0]['KAT_STR']
                            circles_html = ""
                            if winner_revealed:
                                prefix = f"v_{sel_cat}_{label}_"
                                all_votes = store.data.get("votes", {})
                                voters = [v_key.replace(prefix, "") for v_key, v_val in all_votes.items() if v_key.startswith(prefix) and str(v_val) == str(kat_nr)]
                                if voters:
                                    circles = "".join([f"<div class='judge-circle' title='{v}'>{get_initials(v)}</div>" for v in voters])
                                    circles_html = f"<div class='judge-initials-container'>{circles}</div>"

                            st.markdown(f"<div class='cat-card'><div class='cat-number'>{kat_nr}</div><div class='cat-details'>{get_full_label(m.iloc[0])}</div>{circles_html}</div>", unsafe_allow_html=True)
                        else: st.markdown("<div class='placeholder-box'>–</div>", unsafe_allow_html=True)
                    else: st.markdown("<div class='placeholder-box'>🔒</div>", unsafe_allow_html=True)
            
            with r_cols[-1]:
                if winner_revealed:
                    prefix = f"v_{sel_cat}_{label}_"
                    winner_nr = store.data.get(f"override_{sel_cat}_{label}", "Automatisch (Stimmen)")
                    if winner_nr == "Automatisch (Stimmen)" and "votes" in store.data:
                        vts = [v for k, v in store.data["votes"].items() if k.startswith(prefix) and v != "Keine Wahl"]
                        if vts: winner_nr = pd.Series(vts).value_counts().index[0]
                    if winner_nr and winner_nr != "Automatisch (Stimmen)":
                        m_w = df_full[df_full['KAT_STR'] == str(winner_nr)]
                        if not m_w.empty: st.markdown(f"<div class='cat-card winner-card'><div class='cat-number'>{winner_nr}</div><div class='cat-details'>{get_full_label(m_w.iloc[0])}</div></div>", unsafe_allow_html=True)
                else: st.markdown("<div class='placeholder-box'>🔒</div>", unsafe_allow_html=True)

    time.sleep(3); st.rerun()
    
# LIVE DASHBOARD
elif st.session_state.view == "Dashboard":
    display_header_with_logo("📢 Live-Aufruf & Status")
    tag = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"]).upper()
    df_full = load_labels()
    if df_full is not None:
        r_col = f"RICHTER {tag}"
        df_tag = df_full[df_full[tag].astype(str).str.upper() == 'X'].copy()
        judges = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
        if judges:
            cols = st.columns(len(judges))
            for i, j in enumerate(judges):
                with cols[i]:
                    st.markdown(f"<div class='judge-header-box'>{j}</div>", unsafe_allow_html=True)
                    
                    judge_entries = []
                    for k, v in store.data.items():
                        if "|" in k and k.split("|")[1] == j:
                            flags = v.get("flags", {}) if isinstance(v, dict) else {}
                            beim_richten = flags.get("Zum Richten", False) and not flags.get("Gerichtet", False)
                            nominiert = flags.get("NOM", False)
                            biv = flags.get("BIV", False)
                            
                            if beim_richten or nominiert or biv:
                                judge_entries.append({"key": k, "data": v if isinstance(v, dict) else {"flags": {}}})
                    
                    judge_entries.sort(key=lambda x: x["data"].get("timestamp", 0))
                    
                    for entry in judge_entries:
                        kat_nr = entry["key"].split("|")[0]
                        flags = entry["data"].get("flags", {})
                        m = df_tag[df_tag['KAT_STR'] == kat_nr]
                        if not m.empty:
                            tags = "".join([f"<span class='tag tag-{t.lower().replace(' ', '')}'>{t}</span> " for t, val in flags.items() if val and t != "Gerichtet"])
                            if tags: 
                                st.markdown(f"""
                                    <div class='cat-card'>
                                        <div class='cat-number'>{kat_nr}</div>
                                        <div class='cat-details'>{get_full_label(m.iloc[0])}</div>
                                        <div class='tag-container'>{tags}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                            
    st_autorefresh(interval=10000, key="dash_refresh")


# --- CORRECTIONS ONLY IN THE STEWARD PANEL ---
# --- CORRECTIONS ONLY IN THE STEWARD PANEL ---
elif st.session_state.view == "Steward_Panel":
    display_header_with_logo("📝 Steward-Pult")
    df_full = load_labels()
    
    if df_full is not None:
        # 1. Prüfen, ob ein Richter via QR-Code übergeben wurde
        url_judge_name = st.session_state.get("url_judge", "--")
        
        # 2. Automatisch ermitteln, an welchem Tag dieser Richter arbeitet
        url_day = st.query_params.get("day", "1")
        default_tag_idx = 1 if url_day == "2" else 0
        
        if url_judge_name != "--":
            # Wenn der Richter nicht in Tag 1, aber in Tag 2 existiert -> Umschalten auf Tag 2
            j_t1 = [r for r in df_full['RICHTER TAG 1'].unique() if str(r) != "nan"] if 'RICHTER TAG 1' in df_full.columns else []
            j_t2 = [r for r in df_full['RICHTER TAG 2'].unique() if str(r) != "nan"] if 'RICHTER TAG 2' in df_full.columns else []
            
            if url_judge_name in j_t2 and url_judge_name not in j_t1:
                default_tag_idx = 1 # Setzt den Radio-Button auf "Tag 2"
        
        # Sidebar Radio-Button mit dem dynamischen Default-Index
        tag = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"], index=default_tag_idx).upper()
        
        r_col = f"RICHTER {tag}"
        all_j = sorted([r for r in df_full[df_full[tag].astype(str).str.upper() == 'X'][r_col].unique() if str(r) != "nan"])
        
        # Berechnen des Default-Index für die Richter-Selectbox
        default_idx = 0
        if url_judge_name in all_j:
            default_idx = all_j.index(url_judge_name) + 1 # +1 wegen dem "--" Eintrag
            
        mein_richter = st.selectbox("Richter wählen:", ["--"] + all_j, index=default_idx)

        if mein_richter != "--":
            df_richter_alle = df_full[(df_full[tag].astype(str).str.upper() == 'X') & (df_full[r_col] == mein_richter)]
            verfuegbare_kategorien = sorted(list(set([str(cat).replace('.0', '') for cat in df_richter_alle['KATEGORIE'].unique() if pd.notna(cat)])))
            meine_kategorie = st.selectbox("Kategorie wählen:", verfuegbare_kategorien)
            
            df_j = df_richter_alle[df_richter_alle['KATEGORIE'].astype(str).str.replace('.0', '') == meine_kategorie].sort_values('KATALOG-NR')
            st.divider()
            
            for _, row in df_j.iterrows():
                nr = row['KAT_STR']
                k = f"{nr}|{mein_richter}"
                
                # Spalten flexibel auslesen
                klasse = row.get('KLASSE_INTERNAL', row.get('AUSSTELLUNGSKLASSE', row.get('KLASSE', 'N/A')))
                fg_cols = [c for c in row.index if "FARBGRUPPE" in c or "FARB-GRUPPE" in c]
                farbgruppe = row[fg_cols[0]] if fg_cols else row.get('FARBGRUPPE', 'N/A')
                if pd.isna(farbgruppe) or str(farbgruppe).strip().lower() == "nan": farbgruppe = "N/A"
                
                geschlecht = row.get('GESCHLECHT', 'N/A')
                geb_cols = [c for c in row.index if "GEB" in c or "GEBURT" in c]
                geb_datum = row[geb_cols[0]] if geb_cols else row.get('GEB_DATUM', 'N/A')
                if isinstance(geb_datum, pd.Timestamp): geb_datum = geb_datum.strftime('%d.%m.%Y')
                elif pd.isna(geb_datum) or str(geb_datum).strip().lower() == "nan": geb_datum = "N/A"
                
                if k not in store.data or not isinstance(store.data[k], dict) or "flags" not in store.data[k]: 
                    store.data[k] = {
                        "flags": {"Zum Richten": False, "BIV": False, "NOM": False, "Gerichtet": False},
                        "timestamp": 0
                    }
                
                flags = store.data[k]["flags"]
                card_class = "steward-card-wrapper gerichtet" if flags.get("Gerichtet") else "steward-card-wrapper"
                
                # --- START DES GRAUEN RECHTECKS ---
                # Wir öffnen das div mit der Klasse steward-card-wrapper.
                st.markdown(f"""
                <div class="{card_class}">
                    <div class="card-header-row">
                        <span class="card-cat-number">Nr. {nr}</span>
                        <span class="card-meta-main">{get_full_label(row)}</span>
                    </div>
                    <div class="grid-container">
                        <span class="card-meta-sub"><span class="meta-label">Klasse:</span> {klasse}</span>
                        <span class="card-meta-sub"><span class="meta-label">Farbgruppe:</span> {farbgruppe}</span>
                        <span class="card-meta-sub"><span class="meta-label">Geschlecht:</span> {geschlecht}</span>
                        <span class="card-meta-sub"><span class="meta-label">Geboren:</span> {geb_datum}</span>
                    </div>
                    <div style="border-top: 1px solid #e2e2e2; padding-top: 10px; margin-top: 12px; margin-bottom: 8px;"></div>
                """, unsafe_allow_html=True)
                
                # Die originalen Spalten für die Buttons
                c1, c2, c3, c4 = st.columns(4, vertical_alignment="center")
                
                # BUTTON 1: AUFRUFEN (Blau)
                is_rich = flags.get("Zum Richten")
                with c1:
                    # Hier nutzen wir nun auch die blinkende Klasse, wenn aktiv
                    if is_rich: st.markdown('<div class="st-blink-btn">', unsafe_allow_html=True)
                    if st.button("⚠️ [ AKTIV ] AUFGERUFEN ⚠️" if is_rich else "AUFRUFEN", key=f"btn_rich_{k}"):
                        store.data[k]["flags"]["Zum Richten"] = not is_rich
                        if store.data[k]["flags"]["Zum Richten"]:
                            store.data[k]["flags"]["Gerichtet"] = False
                            store.data[k]["timestamp"] = time.time()
                        st.rerun()
                    if is_rich: st.markdown('</div>', unsafe_allow_html=True)
                
                # BUTTON 2: BIV (Grün)
                is_biv = flags.get("BIV")
                with c2:
                    if is_biv: st.markdown('<div class="st-blink-btn">', unsafe_allow_html=True)
                    if st.button("⚠️ [ AKTIV ] BIV ⚠️" if is_biv else "BIV", key=f"btn_biv_{k}"):
                        store.data[k]["flags"]["BIV"] = not is_biv
                        store.data[k]["timestamp"] = time.time()
                        st.rerun()
                    if is_biv: st.markdown('</div>', unsafe_allow_html=True)
                
                # BUTTON 3: NOMINIEREN (Gelb)
                is_nom = flags.get("NOM")
                with c3:
                    if is_nom: st.markdown('<div class="st-blink-btn">', unsafe_allow_html=True)
                    if st.button("⚠️ [ AKTIV ] NOM ⚠️" if is_nom else "NOM", key=f"btn_nom_{k}"):
                        store.data[k]["flags"]["NOM"] = not is_nom
                        if store.data[k]["flags"]["NOM"]:
                            store.data[k]["timestamp"] = time.time()
                        st.rerun()
                    if is_nom: st.markdown('</div>', unsafe_allow_html=True)
                
                # BUTTON 4: GERICHTET (Grau - bleibt stabil ohne Blinken)
                is_done = flags.get("Gerichtet")
                with c4:
                    if st.button("[ ERLEDIGT ] GERICHTET" if is_done else "GERICHTET", key=f"btn_done_{k}"):
                        if not is_done:
                            store.data[k]["flags"]["Zum Richten"] = False
                            store.data[k]["flags"]["Gerichtet"] = True
                        else:
                            store.data[k]["flags"]["Gerichtet"] = False
                        st.rerun()
                                
                # --- ENDE DES GRAUEN RECHTECKS ---
                # Erst nachdem die Buttons gerendert wurden, schließen wir das umschließende HTML-Kasten-Div.
                st.markdown("</div>", unsafe_allow_html=True)

# JUDGE VOTING
elif st.session_state.view == "Judge_Voting":
    display_header_with_logo("🗳️ Richter Abstimmung/Judges Votes")
    df_full = load_labels()
    if df_full is not None:
        url_day = st.query_params.get("day", "1")
        day_idx = 1 if url_day == "2" else 0
        tag = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"], index=day_idx, key="judge_day_selector").upper()
        r_col = f"RICHTER {tag}"
        all_judges = sorted([r for r in df_full[r_col].unique() if str(r) != "nan"])
        
        c1, c2 = st.columns(2)
        
                # PRÜFUNG: Wurde ein Richter in der URL mitgegeben? (Ignorieren, wenn Admin am Werk ist)
        url_judge_name = st.session_state.get("url_judge", "--")
        
        if url_judge_name in all_judges and st.session_state.user_role != "Admin":
            # Fixierung NUR für echte Richter-Direktlinks
            active_j = url_judge_name
            c1.markdown(f"<div style='padding-top:25px;'><b>Eingeloggt als Richter:</b> <span style='color:#1a4a9e; font-size:18px;'>{active_j}</span></div>", unsafe_allow_html=True)
        else:
            # Admins (oder wenn kein Richter in URL steht) sehen immer die volle Auswahlbox!
            active_j = c1.selectbox("Identität/Identity:", ["--"] + all_judges)

        active_cat = c2.selectbox("Kategorie/Category:", sorted(df_full['KATEGORIE'].unique()))
        
        # ... ab hier läuft dein originaler Code für das Voting unverändert weiter ...

        if active_j != "--":
            if "votes" not in store.data: store.data["votes"] = {}
            bis_defs = [("Adult Male", [1,3,5,7,9], "M"), ("Adult Female", [1,3,5,7,9], "W"), ("Neuter Male", [2,4,6,8,10], "M"), ("Neuter Female", [2,4,6,8,10], "W"), ("Junior 8-12 Male", [11], "M"), ("Junior 8-12 Female", [11], "W"), ("Kitten 4-8 Male", [12], "M"), ("Kitten 4-8 Female", [12], "W")]
            for label, klassen, geschl in bis_defs:
                with st.expander(f"Wahl für/Choice for {label}"):
                    pool = df_full[(df_full['SELECTION'].astype(str).str.upper() == 'X') & (df_full['KATEGORIE'] == active_cat) & (df_full['KLASSE_INTERNAL'].isin(klassen)) & (df_full['GESCHLECHT'].astype(str).str.upper() == geschl)]
                    if not pool.empty:
                        opts = {f"#{r['KAT_STR']} - {get_full_label(r)}": r['KAT_STR'] for _, r in pool.iterrows()}
                        v_key = f"v_{active_cat}_{label}_{active_j}"
                        curr = store.data["votes"].get(v_key, "Keine Wahl")
                        sel = st.radio("Favorit:", ["Keine Wahl/Not chosen yet"] + list(opts.keys()), index=(list(opts.values()).index(curr)+1) if curr in opts.values() else 0, key=f"r_{v_key}")
                        store.data["votes"][v_key] = opts[sel] if sel != "Keine Wahl/Not chosen yet" else "Keine Wahl/Not chosen yet"




# --- NEUER MENÜPUNKT: QR CODES ---
elif st.session_state.view == "QR_Codes":
    display_header_with_logo("📱 QR-Code Login Zentrale")
    st.write("Lass die Richter und Mitarbeiter diesen QR-Code scannen, um sich sofort ohne Passwort einzuloggen.")
    
    df_full = load_labels()
    
    # Basis-URL deiner App
    base_url = "https://burgdorf-2026-ykralltanrq8aabhwrarmf.streamlit.app/"
    
    # Registerkarten für die Übersichtlichkeit
    tab1, tab2, tab3 = st.tabs(["🤵 Stewards & Admins", "👨‍⚖️ Richter (Tag 1)", "👨‍⚖️ Richter (Tag 2)"])
    
    # Hilfsfunktion zum Zeichnen der QR-Codes
    def generate_qr_image(url_to_encode):
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(url_to_encode)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

        # ---------------- TAB 1: STEWARDS & ADMINS ----------------
    with tab1:
        st.subheader("Allgemeine Logins")
        col_adm, _ = st.columns(2)
        with col_adm:
            st.warning("⚙️ ADMIN MAIN HOME")
            adm_url = f"{base_url}?view=admin&auth=true&role=Admin"
            st.image(generate_qr_image(adm_url), width=230)
            st.caption(f"[Link kopieren]({adm_url})")
            
        st.divider()
        
        if df_full is not None:
            # --- SEKTION: TAG 1 ---
            st.markdown("### 📝 Steward-Links für TAG 1 (Samstag)")
            st.write("Diese QR-Codes filtern fest auf die Richter von Tag 1:")
            
            if 'RICHTER TAG 1' in df_full.columns:
                judges_t1 = sorted([r for r in df_full['RICHTER TAG 1'].unique() if str(r) != "nan"])
                if judges_t1:
                    s_cols_t1 = st.columns(3)
                    for idx, judge in enumerate(judges_t1):
                        with s_cols_t1[idx % 3]:
                            st.info(f"Steward für: {judge}")
                            stew_url_t1 = f"{base_url}?view=steward&auth=true&role=Steward&judge={judge.replace(' ', '+')}&day=1"
                            st.image(generate_qr_image(stew_url_t1), width=200)
                            st.write("---")
                else:
                    st.write("Keine Richter für Tag 1 gefunden.")
            else:
                st.error("Spalte 'RICHTER TAG 1' fehlt in den Daten!")
                
            st.write("") # Abstandhalter
            st.divider()
            st.write("") # Abstandhalter
            
            # --- SEKTION: TAG 2 ---
            st.markdown("### 📝 Steward-Links für TAG 2 (Sonntag)")
            st.write("Diese QR-Codes filtern fest auf die Richter von Tag 2:")
            
            if 'RICHTER TAG 2' in df_full.columns:
                judges_t2 = sorted([r for r in df_full['RICHTER TAG 2'].unique() if str(r) != "nan"])
                if judges_t2:
                    s_cols_t2 = st.columns(3)
                    for idx, judge in enumerate(judges_t2):
                        with s_cols_t2[idx % 3]:
                            st.info(f"Steward für: {judge}")
                            stew_url_t2 = f"{base_url}?view=steward&auth=true&role=Steward&judge={judge.replace(' ', '+')}&day=2"
                            st.image(generate_qr_image(stew_url_t2), width=200)
                            st.write("---")
                else:
                    st.write("Keine Richter für Tag 2 gefunden.")
            else:
                st.error("Spalte 'RICHTER TAG 2' fehlt in den Daten!")


    # ---------------- TAB 2: RICHTER TAG 1 ----------------
    with tab2:
        st.subheader("Richter-Direkt-Links für TAG 1")
        if df_full is not None:
            # Alle Richter für Tag 1 aus der Excel holen
            judges_t1 = sorted([r for r in df_full['RICHTER TAG 1'].unique() if str(r) != "nan"])
            
            if judges_t1:
                # Erstellt ein Raster (3 Spalten nebeneinander) für die QR-Codes
                j_cols = st.columns(3)
                for idx, judge in enumerate(judges_t1):
                    with j_cols[idx % 3]:
                        st.success(f"Richter: {judge}")
                        # URL sicher zusammenbauen (Leerzeichen durch + ersetzen)
                        j_url = f"{base_url}?view=richter&auth=true&role=Richter&judge={judge.replace(' ', '+')}&day=1"
                        st.image(generate_qr_image(j_url), width=200)
                        st.write("---")
            else:
                st.write("Keine Richter für Tag 1 gefunden.")

    # ---------------- TAB 3: RICHTER TAG 2 ----------------
    with tab3:
        st.subheader("Richter-Direkt-Links für TAG 2")
        if df_full is not None:
            # Alle Richter für Tag 2 aus der Excel holen
            judges_t2 = sorted([r for r in df_full['RICHTER TAG 2'].unique() if str(r) != "nan"])
            
            if judges_t2:
                j_cols = st.columns(3)
                for idx, judge in enumerate(judges_t2):
                    with j_cols[idx % 3]:
                        st.success(f"Richter: {judge}")
                        j_url = f"{base_url}?view=richter&auth=true&role=Richter&judge={judge.replace(' ', '+')}&day=2"
                        st.image(generate_qr_image(j_url), width=200)
                        st.write("---")
            else:
                st.write("Keine Richter für Tag 2 gefunden.")

# ADMIN PANEL
elif st.session_state.view == "Admin_Panel":
    display_header_with_logo("⚙️ Admin-Konsole")
    if st.button("ALLE DATEN ZURÜCKSETZEN"):
        store.data = {}
        store.active_overlay = None
        st.success("Speicher geleert!")
