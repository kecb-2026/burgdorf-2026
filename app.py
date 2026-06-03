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
import json
import os
from io import BytesIO
# --- IMPORTS FÜR DIE PDF-GENERIERUNG ---
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

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

    def save_backup(self):
        """Sichert den aktuellen Speicherzustand in einer JSON-Datei auf dem Server"""
        try:
            with open("store_backup.json", "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            pass  # Verhindert, dass ein Fehler beim Schreiben die App blockiert

    def load_backup(self):
        """Lädt die Daten aus dem Backup, falls der Server neu gestartet wurde"""
        if os.path.exists("store_backup.json"):
            try:
                with open("store_backup.json", "r", encoding="utf-8") as f:
                    backup_data = json.load(f)
                    if backup_data:
                        self.data = backup_data
            except Exception as e:
                st.error(f"Fehler beim Laden des Notfall-Backups: {e}")

@st.cache_resource
def get_store():
    store_instance = GlobalStore()
    # Beim allerersten Start der App prüfen, ob ein Backup bereitliegt
    store_instance.load_backup()
    return store_instance

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
        elif v_param == "nominated": st.session_state.view = "Nominated_Cats"



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
        df = pd.read_excel("2026.xlsx", engine='openpyxl', header=0)
        df.columns = [str(c).strip().upper() for c in df.columns]
        df = df.fillna("-")
        df['KLASSE_INTERNAL'] = df['AUSSTELLUNGSKLASSE'] if 'AUSSTELLUNGSKLASSE' in df.columns else df.get('KLASSE', '')
        if 'KATALOG-NR' in df.columns:
            df['KAT_STR'] = df['KATALOG-NR'].astype(str).str.replace('.0', '', regex=False)

        # --- NEU: ABSOLUT RISIKO-FREIE WEICHE FÜR TAG 1 & TAG 2 ---
        # Wir prüfen, welcher Tag im globalen Sidebar-Radio-Button gewählt ist
        # Falls der Selector auf "Tag 2" steht, nehmen wir SELECTION 2, sonst SELECTION 1
        day_selector = st.session_state.get("judge_day_selector", "Tag 1")
        
        if "2" in str(day_selector):
            df['SELECTION'] = df['SELECTION 2'] if 'SELECTION 2' in df.columns else df.get('SELECTION', '-')
        else:
            df['SELECTION'] = df['SELECTION 1'] if 'SELECTION 1' in df.columns else df.get('SELECTION', '-')
        # -----------------------------------------------------------
		
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
    "Admin": ["Home", "Dashboard", "BIS_Public", "Judge_Voting", "Steward_Panel", "BIS_Admin_Control", "QR_Codes", "Nominated_Cats", "Judge_List", "Nomination_Labels", "Admin_Panel"]
}

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
    
available_views = access_map.get(st.session_state.user_role, ["Dashboard"])
st.sidebar.image(LOGO_URL, width=150)

# HIER WURDE format_func HINZUGEFÜGT: Tauscht bei der Anzeige die Unterstriche gegen Leerzeichen
st.session_state.view = st.sidebar.radio(
    "Menü:", 
    available_views, 
    index=available_views.index(st.session_state.view) if st.session_state.view in available_views else 0,
    format_func=lambda x: x.replace("_", " ")
)
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
             # NEU: Button für die nominierten Katzen
        if st.button("🐈 NOMINIERTE KATZEN LISTE"):
            st.query_params.update({"view": "nominated", "auth": "true", "role": "Admin"})
            set_view("Nominated_Cats")
            st.rerun()
            # NEU: Button für die Richter Liste
        if st.button("🐈 RICHTER LISTE"):
            st.query_params.update({"view": "judge-list", "auth": "true", "role": "Admin"})
            set_view("Judge_List")
            st.rerun()
        if st.button("🖨️ NOMINATION LABELS DRUCK"):
            st.query_params.update({"view": "nom-labels", "auth": "true", "role": "Admin"})
            set_view("Nomination_Labels")
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
st.divider()
st.subheader("⚙️ System-Einstellungen (Admin-Steuerung)")

# 1. Richter-Fixierung
if "steward_lock" not in st.session_state:
    st.session_state.steward_lock = True
st.session_state.steward_lock = st.toggle(
    "Richter-Auswahl für Stewards sperren (Lockdown)", 
    value=st.session_state.steward_lock
)

# Initialisiere den sicheren Speicher, falls er beim allerersten Start noch leer ist
if "admin_selected_day" not in st.session_state:
    st.session_state.admin_selected_day = "Tag 1"

# Funktion, die den Wert sofort beim Klicken bombensicher wegschreibt
def save_admin_day():
    st.session_state.admin_selected_day = st.session_state.admin_radio_widget

st.subheader("⚙️ Globaler Event-Status")
st.radio(
    "Aktiven Tag für die gesamte Ausstellung festlegen:", 
    ["Tag 1", "Tag 2"], 
    key="admin_radio_widget",
    index=0 if st.session_state.admin_selected_day == "Tag 1" else 1,
    on_change=save_admin_day  # Das hier sichert den Tag ab!
)





# BIS ADMIN CONTROL
# BIS ADMIN CONTROL
elif st.session_state.view == "BIS_Admin_Control":
    display_header_with_logo("👑 BIS Admin Control")
    df_full = load_labels()
    
    if df_full is not None:
        # --- HIER DIE NEUE RADIO-BOX FÜR DIE TAGE EINFÜGEN ---
        admin_tag = st.radio("Ausstellungstag verwalten:", ["Tag 1", "Tag 2"], horizontal=True, key="admin_day_selector").upper()
        
        # Spaltenname dynamisch bestimmen (SELECTION 1 oder SELECTION 2)
        sel_col = f"SELECTION {admin_tag.replace('TAG ', '')}"
        
        # Wir überschreiben temporär im geladenen Dataframe die 'SELECTION' Spalte,
        # damit alle nachfolgenden Filter im originalen Code (pool = df_full[df_full['SELECTION']...]) unverändert weiterlaufen!
        if sel_col in df_full.columns:
            df_full['SELECTION'] = df_full[sel_col]
        # -----------------------------------------------------

    if df_full is not None:
        # Auch die Kategorie-Auswahl braucht einen tagesabhängigen Key
        sel_cat = st.selectbox("Kategorie verwalten:", sorted(df_full['KATEGORIE'].unique()), key=f"admin_sel_cat_{admin_tag}")
        bis_defs = [("Adult Male", [1,3,5,7,9], "M"), ("Adult Female", [1,3,5,7,9], "W"), ("Neuter Male", [2,4,6,8,10], "M"), ("Neuter Female", [2,4,6,8,10], "W"), ("Junior 8-12 Male", [11], "M"), ("Junior 8-12 Female", [11], "W"), ("Kitten 4-8 Male", [12], "M"), ("Kitten 4-8 Female", [12], "W")]
        
        for label, klassen, geschl in bis_defs:
            # Der Expander-Key wird tagesabhängig, damit der Auf-/Zuklapp-Status nicht vermischt wird
            with st.expander(f"KLASSE: {label} ({admin_tag})", expanded=True):
                c_ctrl, c_votes = st.columns([1, 1.2])
                
                # Der v_prefix enthält jetzt den Tag, damit die Stimmen von Tag 1 und Tag 2 getrennt gesucht werden
                v_prefix = f"v_{admin_tag}_{sel_cat}_{label}_"
                
                with c_ctrl:
                    st.markdown("**Steuerung**")
                    
                    # Die Datenschlüssel im store.data erhalten den Tag, damit Werte getrennt gespeichert werden
                    key_reveal = f"reveal_{admin_tag}_{sel_cat}_{label}"
                    key_winner_reveal = f"winner_reveal_{admin_tag}_{sel_cat}_{label}"
                    key_override = f"override_{admin_tag}_{sel_cat}_{label}"
                    
                    # Die Widget-Keys (key=...) erhalten ebenfalls das admin_tag, was Streamlit zum sauberen Reset zwingt
                    store.data[key_reveal] = st.checkbox("Nominationen anzeigen", value=store.data.get(key_reveal, False), key=f"cb1_{key_reveal}")
                    store.data[key_winner_reveal] = st.checkbox("BIS Gewinner anzeigen", value=store.data.get(key_winner_reveal, False), key=f"cb2_{key_winner_reveal}")
                    
                    pool = df_full[(df_full['SELECTION'].astype(str).str.upper() == 'X') & (df_full['KATEGORIE'] == sel_cat) & (df_full['KLASSE_INTERNAL'].isin(klassen)) & (df_full['GESCHLECHT'].astype(str).str.upper() == geschl)]
                    options = ["Automatisch (Stimmen)"] + sorted(pool['KAT_STR'].unique().tolist())
                    
                    store.data[key_override] = st.selectbox(f"Gewinner festlegen:", options, index=options.index(store.data.get(key_override, "Automatisch (Stimmen)")) if store.data.get(key_override) in options else 0, key=f"sb_{key_override}")
                    
                    final_nr = None
                    if store.data[key_override] != "Automatisch (Stimmen)": 
                        final_nr = store.data[key_override]
                    elif "votes" in store.data:
                        vts = [v for k, v in store.data["votes"].items() if k.startswith(v_prefix) and v != "Keine Wahl"]
                        if vts: 
                            final_nr = pd.Series(vts).value_counts().index[0]
                            
                    if final_nr and st.button(f"🏆 OVERLAY ZEIGEN (#{final_nr})", key=f"btn_ov_{admin_tag}_{sel_cat}_{label}"):
                        w_match = df_full[df_full['KAT_STR'] == str(final_nr)]
                        if not w_match.empty:
                            store.active_overlay = w_match.iloc[0].to_dict()
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
                            for nr, count in summary.items(): 
                                st.write(f"Katze #{nr}: {count} Stimme(n)")
                                
    if st.button("⬅️ Zurück zum Hauptmenü", key="back_from_bisadmin"):
        set_view("Home")

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

        # --- DYNAMISCHE SPALTEN-WEICHE FÜR DIE 2 TAGE ---
        sel_col = f"SELECTION {tag.replace('TAG ', '')}"
        if sel_col in df_full.columns:
            df_full['SELECTION'] = df_full[sel_col]
        # ------------------------------------------------

        bis_defs = [
            ("Adult Male", [1,3,5,7,9], "M"), ("Adult Female", [1,3,5,7,9], "W"), 
            ("Neuter Male", [2,4,6,8,10], "M"), ("Neuter Female", [2,4,6,8,10], "W"), 
            ("Junior 8-12 Male", [11], "M"), ("Junior 8-12 Female", [11], "W"), 
            ("Kitten 4-8 Male", [12], "M"), ("Kitten 4-8 Female", [12], "W")
        ]
        
        r_col = f"RICHTER {tag}"
        judges = sorted([r for r in df_full[df_full[tag].astype(str).str.upper() == 'X'][r_col].unique() if str(r) != "nan"])

        # --- PRÜFEN, OB ES IN DIESER KATEGORIE ÜBERHAUPT NOMINIERTE KATZEN GIBT ---
        cats_in_this_cat = df_full[
            (df_full['SELECTION'].astype(str).str.upper() == 'X') & 
            (df_full['KATEGORIE'] == sel_cat)
        ]

        # Wenn keine einzige Katze ein 'X' in dieser Kategorie hat, Tabelle ausblenden
        if cats_in_this_cat.empty:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.info(f"ℹ️ In der Kategorie {sel_cat} sind für {tag} aktuell keine Katzen für die Best in Show nominiert.")
            
            # Verhindert, dass das restliche Layout/Footer nach oben springt
            st.markdown("<div style='min-height: 400px;'></div>", unsafe_allow_html=True)

        # --- CSS-LOGIK FÜR GRÜNE RICHTER IM HEADER ---
        style_rules = ""
        for label, klassen, geschl in bis_defs:
            if not store.data.get(f"winner_reveal_{tag}_{sel_cat}_{label}", False):
                prefix = f"v_{tag}_{sel_cat}_{label}_"
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
            
            show_noms = store.data.get(f"reveal_{tag}_{sel_cat}_{label}", False)
            winner_revealed = store.data.get(f"winner_reveal_{tag}_{sel_cat}_{label}", False)
            
            for i, j in enumerate(judges):
                with r_cols[i+1]:
                    if show_noms:
                        m = df_full[(df_full['SELECTION'].astype(str).str.upper() == 'X') & (df_full[r_col] == j) & (df_full['KATEGORIE'] == sel_cat) & (df_full['KLASSE_INTERNAL'].isin(klassen)) & (df_full['GESCHLECHT'].astype(str).str.upper() == geschl)]
                        if not m.empty:
                            kat_nr = m.iloc[0]['KAT_STR']
                            circles_html = ""
                            if winner_revealed:
                                prefix = f"v_{tag}_{sel_cat}_{label}_"
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
                    prefix = f"v_{tag}_{sel_cat}_{label}_"
                    winner_nr = store.data.get(f"override_{tag}_{sel_cat}_{label}", "Automatisch (Stimmen)")
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


    # Holt den Tag direkt aus dem vom Admin gesteuerten Key
    menu_day = st.session_state.get("judge_day_selector", "Tag 1")
    tag = "TAG 2" if "2" in str(menu_day) else "TAG 1"
	
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
        url_day = st.query_params.get("day", None)
        
        # Standardmäßig wird der Tag vom Admin-Schalter genommen
        admin_day = st.session_state.get("judge_day_selector", "Tag 1")
        calculated_tag = "TAG 2" if "2" in str(admin_day) else "TAG 1"
        
        # Falls in der URL explizit ein Tag steht, überschreibt dieser den Admin-Tag
        if url_day == "1":
            calculated_tag = "TAG 1"
        elif url_day == "2":
            calculated_tag = "TAG 2"
        
        # 3. Wenn ein Richtername übergeben wurde, die bestehende Logik prüfen:
        if url_judge_name != "--":
            # Wenn der Richter nicht in Tag 1, aber in Tag 2 existiert -> Zuweisung auf Tag 2 erzwingen
            j_t1 = [r for r in df_full['RICHTER TAG 1'].unique() if str(r) != "nan"] if 'RICHTER TAG 1' in df_full.columns else []
            j_t2 = [r for r in df_full['RICHTER TAG 2'].unique() if str(r) != "nan"] if 'RICHTER TAG 2' in df_full.columns else []
            
            if url_judge_name in j_t2 and url_judge_name not in j_t1:
                calculated_tag = "TAG 2"
        
        # Finale Zuweisung an die Variable tag (immer in Großbuchstaben für die Spaltennamen)
        tag = calculated_tag.upper()
        
        # Optionale visuelle Rückmeldung in der Sidebar statt einem Eingabefeld
        st.sidebar.info(f"📅 Aktiver Ausstellungstag: {tag}")
        

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
                
                   # Zieht eine saubere Linie und schafft 30px Platz zur nächsten Karte
                st.markdown('<hr style="border: none; border-top: 2px solid #000; margin-top: 0px; margin-bottom: 30px;">', unsafe_allow_html=True)

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
                        # TAG wird hier in den Schlüssel eingebaut, damit Tag 1 und Tag 2 getrennt gespeichert und resettet werden
                        v_key = f"v_{tag}_{active_cat}_{label}_{active_j}"
                        curr = store.data["votes"].get(v_key, "Keine Wahl")
                        sel = st.radio("Favorit:", ["Keine Wahl/Not chosen yet"] + list(opts.keys()), index=(list(opts.values()).index(curr)+1) if curr in opts.values() else 0, key=f"r_{v_key}")
                        store.data["votes"][v_key] = opts[sel] if sel != "Keine Wahl/Not chosen yet" else "Keine Wahl/Not chosen yet"



# --- NEUER MENÜPUNKT: QR CODES ---
elif st.session_state.view == "QR_Codes":
    display_header_with_logo("📱 QR-Code Login Zentrale")
    st.write("Lass die Richter und Mitarbeiter diesen QR-Code scannen, um sich sofort ohne Passwort einzuloggen.")
    
    df_full = load_labels()
    
    # Basis-URL deiner App
    base_url = "https://kecb2026.streamlit.app/"
    
    # 1. Hilfsfunktion zum Zeichnen der QR-Codes für die Streamlit-UI
    def generate_qr_image(url_to_encode):
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(url_to_encode)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    # 2. PDF-Generierungsfunktion (Getrennter Admin-Block & Emoji-frei)
    def generate_pdf_download(df):
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer, 
            pagesize=letter,
            rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
        )
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=20, leading=24, spaceAfter=15, textColor=colors.HexColor("#1A365D"), alignment=1)
        section_style = ParagraphStyle('DocSection', parent=styles['Heading2'], fontSize=12, leading=15, spaceBefore=15, spaceAfter=6, textColor=colors.HexColor("#2B6CB0"))
        label_style = ParagraphStyle('DocLabel', parent=styles['Normal'], fontSize=9, leading=12, alignment=1, textColor=colors.HexColor("#2D3748"))
        
        story = []
        story.append(Paragraph("QR-Code Login Zentrale - Burgdorf 2026", title_style))
        story.append(Spacer(1, 10))
        
        # --- FIX: ADMIN DIREKT ZEICHNEN (Nicht im 3er-Raster der Richter!) ---
        story.append(Paragraph("1. Allgemeine Logins und Admins", section_style))
        adm_url = f"{base_url}?view=admin&auth=true&role=Admin"
        
        qr = qrcode.QRCode(version=1, box_size=4, border=1)
        qr.add_data(adm_url)
        qr.make(fit=True)
        img_pil = qr.make_image(fill_color="black", back_color="white")
        img_buf = BytesIO()
        img_pil.save(img_buf, format="PNG")
        img_buf.seek(0)
        
        # Platziert den Admin zentriert als Einzelelement
        admin_table = Table([[Paragraph("<b>ADMIN MAIN HOME</b>", label_style)], [Image(img_buf, width=90, height=90)]], colWidths=[180])
        admin_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
        story.append(admin_table)
        story.append(Spacer(1, 15))
        
        # --- AB HIER NUR NOCH DIE LISTEN FÜR STUFENWEISE RASTER SAMMELN ---
        all_qr_items = []
        
        # --- Daten sammeln: Tag 1 ---
        if df is not None and 'RICHTER TAG 1' in df.columns:
            judges_t1 = sorted([r for r in df['RICHTER TAG 1'].unique() if str(r) != "nan"])
            for judge in judges_t1:
                # Stewards Tag 1
                stew_url = f"{base_url}?view=steward&auth=true&role=Steward&judge={judge.replace(' ', '+')}&day=1"
                all_qr_items.append((f"Steward fuer: {judge}", stew_url, "2. Steward-Links fuer TAG 1 (Samstag)"))
                
                # Richter Direkt Tag 1
                j_url = f"{base_url}?view=richter&auth=true&role=Richter&judge={judge.replace(' ', '+')}&day=1"
                all_qr_items.append((f"Richter: {judge} (Tag 1)", j_url, "3. Richter-Direkt-Links fuer TAG 1 (Samstag)"))
                
        # --- Daten sammeln: Tag 2 ---
        if df is not None and 'RICHTER TAG 2' in df.columns:
            judges_t2 = sorted([r for r in df['RICHTER TAG 2'].unique() if str(r) != "nan"])
            for judge in judges_t2:
                # Stewards Tag 2
                stew_url = f"{base_url}?view=steward&auth=true&role=Steward&judge={judge.replace(' ', '+')}&day=2"
                all_qr_items.append((f"Steward fuer: {judge}", stew_url, "4. Steward-Links fuer TAG 2 (Sonntag)"))
                
                # Richter Direkt Tag 2
                j_url = f"{base_url}?view=richter&auth=true&role=Richter&judge={judge.replace(' ', '+')}&day=2"
                all_qr_items.append((f"Richter: {judge} (Tag 2)", j_url, "5. Richter-Direkt-Links fuer TAG 2 (Sonntag)"))
        
        # --- Grid im PDF generieren ---
        unique_sections = list(dict.fromkeys([item[2] for item in all_qr_items]))
        for current_section in unique_sections:
            story.append(Paragraph(current_section, section_style))
            story.append(Spacer(1, 4))
            
            section_items = [item for item in all_qr_items if item[2] == current_section]
            cells = []
            
            for label, url, _ in section_items:
                qr = qrcode.QRCode(version=1, box_size=4, border=1)
                qr.add_data(url)
                qr.make(fit=True)
                img_pil = qr.make_image(fill_color="black", back_color="white")
                
                img_buf = BytesIO()
                img_pil.save(img_buf, format="PNG")
                img_buf.seek(0)
                
                rl_img = Image(img_buf, width=90, height=90)
                
                cell_content = [
                    Paragraph(f"<b>{label}</b>", label_style),
                    Spacer(1, 3),
                    rl_img,
                    Spacer(1, 10)
                ]
                cells.append(cell_content)
            
            grid_data = []
            row = []
            for i, cell in enumerate(cells):
                row.append(cell)
                if (i + 1) % 3 == 0 or (i + 1) == len(cells):
                    while len(row) < 3:
                        row.append(Paragraph("", label_style)) # Saubere leere Zelle
                    grid_data.append(row)
                    row = []
            
            if grid_data:
                table_grid = Table(grid_data, colWidths=[180, 180, 180])
                table_grid.setStyle(TableStyle([
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ]))
                story.append(table_grid)
                story.append(Spacer(1, 5))

        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()

    # ---------------- DYNAMIC DOWNLOAD BUTTON ----------------
    st.write("### 🖨️ Druckansicht & Export")
    try:
        pdf_data = generate_pdf_download(df_full)
        st.download_button(
            label="📄 ALLE QR-Codes (Admins, Stewards & Richter) als PDF herunterladen",
            data=pdf_data,
            file_name="Alle_QR_Codes_Burgdorf_2026.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Fehler bei der PDF-Erstellung: {e}")
    
    st.divider()

    # Registerkarten für die Übersichtlichkeit (Web-Ansicht)
    tab1, tab2, tab3 = st.tabs(["🤵 Stewards & Admins", "👨‍⚖️ Richter (Tag 1)", "👨‍⚖️ Richter (Tag 2)"])
    
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
                
            st.write("") 
            st.divider()
            st.write("") 
            
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
            if 'RICHTER TAG 1' in df_full.columns:
                judges_t1 = sorted([r for r in df_full['RICHTER TAG 1'].unique() if str(r) != "nan"])
                if judges_t1:
                    j_cols = st.columns(3)
                    for idx, judge in enumerate(judges_t1):
                        with j_cols[idx % 3]:
                            st.success(f"Richter: {judge}")
                            j_url = f"{base_url}?view=richter&auth=true&role=Richter&judge={judge.replace(' ', '+')}&day=1"
                            st.image(generate_qr_image(j_url), width=200)
                            st.write("---")
                else:
                    st.write("Keine Richter für Tag 1 gefunden.")
            else:
                st.error("Spalte 'RICHTER TAG 1' fehlt in den Daten!")

    # ---------------- TAB 3: RICHTER TAG 2 ----------------
    with tab3:
        st.subheader("Richter-Direkt-Links für TAG 2")
        if df_full is not None:
            if 'RICHTER TAG 2' in df_full.columns:
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
            else:
                st.error("Spalte 'RICHTER TAG 2' fehlt in den Daten!")
                
    # --- ZURÜCK NAVI ---
    if st.button("⬅️ Zurück zum Hauptmenü", key="back_from_qrcode"):
        set_view("Home")
                
                
# --- NEUER MENÜPUNKT: NOMINIERTE KATZEN (VOLLE FILTER- & SORTIERFUNKTION) ---
elif st.session_state.view == "Nominated_Cats":
    display_header_with_logo("🏅 Nominierte Katzen (Admin-Zentrale)")

    def get_show_class(row):
        kl = str(row.get('KLASSE_INTERNAL', row.get('AUSSTELLUNGSKLASSE', row.get('KLASSE', '')))).replace('.0', '')
        geschlecht = str(row.get('GESCHLECHT', '')).upper()
        if kl in ['1','3','5','7','9']: return f"Adult {geschlecht}"
        if kl in ['2','4','6','8','10']: return f"Neuter {geschlecht}"
        if kl == '11': return f"Junior 8-12 {geschlecht}"
        if kl == '12': return f"Kitten 4-8 {geschlecht}"
        return "Unbekannt"    
    
    df_full = load_labels()
        
    if df_full is not None:
        df_nominierte = df_full[df_full['SELECTION'].astype(str).str.upper() == 'X'].copy()
        if not df_nominierte.empty:
            nominated_data = []

            
            for _, row in df_nominierte.iterrows():
                kat_nr = row.get('KAT_STR', str(row.get('KATALOG-NR', ''))).replace('.0', '')
                
                richter_t1 = row.get('RICHTER TAG 1', row.get('RICHTER 1', ''))
                richter_t2 = row.get('RICHTER TAG 2', row.get('RICHTER 2', ''))
                
                is_tag1 = str(row.get('TAG 1', '')).upper() == 'X'
                is_tag2 = str(row.get('TAG 2', '')).upper() == 'X'
                
                richter_name = "-"
                ausstellungstag = "-"
                if is_tag1 and pd.notna(richter_t1) and str(richter_t1) != "nan":
                    richter_name = richter_t1
                    ausstellungstag = "Tag 1 (Sa)"
                elif is_tag2 and pd.notna(richter_t2) and str(richter_t2) != "nan":
                    richter_name = richter_t2
                    ausstellungstag = "Tag 2 (So)"
                else:
                    if pd.notna(richter_t1) and str(richter_t1) != "nan": richter_name = richter_t1; ausstellungstag = "Tag 1"
                    elif pd.notna(richter_t2) and str(richter_t2) != "nan": richter_name = richter_t2; ausstellungstag = "Tag 2"

                klasse = row.get('KLASSE_INTERNAL', row.get('AUSSTELLUNGSKLASSE', row.get('KLASSE', '-')))
                
                fg_cols = [c for c in row.index if "FARBGRUPPE" in c or "FARB-GRUPPE" in c]
                farbgruppe = row[fg_cols[0]] if fg_cols else row.get('FARBGRUPPE', '-')
                
                geb_cols = [c for c in row.index if "GEB" in c or "GEBURT" in c]
                geb_datum = row[geb_cols[0]] if geb_cols else row.get('GEB_DATUM', '-')
                if isinstance(geb_datum, pd.Timestamp): 
                    geb_datum = geb_datum.strftime('%d.%m.%Y')
                
                nominated_data.append({
                    "Katalog-Nr.": kat_nr,
                    "Rasse": row.get('RASSE', '-'),
                    "Farbcode": row.get('FARBE', '-'),
                    "Geburtsdatum": geb_datum,
                    "Geschlecht": row.get('GESCHLECHT', '-'),
                    "Kategorie": row.get('KATEGORIE', '-'),
                    "Klasse": klasse,
					"Show-Klasse": get_show_class(row),
                    "Richter": richter_name,
                    "Tag": ausstellungstag
                })
            
            df_nom_display = pd.DataFrame(nominated_data)

            # --- ADMIN-KONTROLLZENTRUM (Version 1 Stil: Eigene Expander) ---
            st.markdown("### 🛡️ Admin-Kontrollzentrum")
            df_valid = df_nom_display[df_nom_display['Richter'] != "-"].copy()

            # 1. Dubletten
            dups = df_nom_display[df_nom_display.duplicated(subset=['Katalog-Nr.', 'Tag'], keep=False)]
            if not dups.empty:
                st.error(f"❌ {len(dups['Katalog-Nr.'].unique())} Katze(n) sind mehrfach nominiert!")
                with st.expander("Details: Doppelte Katalog-Nummern"):
                    st.dataframe(dups[['Tag', 'Katalog-Nr.', 'Richter']], hide_index=True)
            else:
                st.success("✅ Katalog-Nummern sind eindeutig.")

            # 2. Richter-Limit
            richter_load = df_valid.groupby(['Tag', 'Richter', 'Kategorie']).size().reset_index(name='Anzahl')
            overloaded = richter_load[richter_load['Anzahl'] > 8]
            if not overloaded.empty:
                st.warning(f"⚠️ {len(overloaded)} Richter-Kategorie-Kombination(en) über Limit (8)!")
                with st.expander("Details: Richter-Auslastung"):
                    st.dataframe(overloaded, hide_index=True)
            else:
                st.success("✅ Richter-Kapazität eingehalten.")

            # 3. Klassen-Exklusivität
            violation_groups = df_valid.groupby(['Tag', 'Richter', 'Kategorie', 'Show-Klasse']).filter(lambda x: len(x) > 1)
            if not violation_groups.empty:
                st.error(f"❌ {len(violation_groups['Richter'].unique())} Richter hat Klassen-Verstöße!")
                with st.expander("Details: Klassen-Verstöße"):
                    st.dataframe(violation_groups[['Tag', 'Richter', 'Kategorie', 'Show-Klasse', 'Katalog-Nr.']], hide_index=True)
            else:
                st.success("✅ Klassen-Regel eingehalten.")

            st.divider()



            
            # --- SEKTION: FILTER & SORTIERUNG (RASTER-LAYOUT) ---
            st.markdown("### 🔍 Filter & Sortierung")
            
            # Erste Filterzeile (Richter & Kategorie)
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                richter_optionen = ["Alle Richter"] + sorted([r for r in df_nom_display['Richter'].unique() if r != "-"])
                wahl_richter = st.selectbox("Nach Richter filtern:", richter_optionen)
            with c_f2:
                kat_optionen = ["Alle Kategorien"] + sorted([str(k) for k in df_nom_display['Kategorie'].unique() if k != "-"])
                wahl_kategorie = st.selectbox("Nach Kategorie filtern:", kat_optionen)
                
            # Zweite Filterzeile (Klasse & Geschlecht)
            c_f3, c_f4 = st.columns(2)
            with c_f3:
                # Wir definieren die feste Reihenfolge für die Show-Klassen
                reihenfolge = ["Kitten 4-8 M", "Kitten 4-8 W", "Junior 8-12 M", "Junior 8-12 W", "Neuter M", "Neuter W", "Adult M", "Adult W"]
                vorhandene_sk = [sk for sk in reihenfolge if sk in df_nom_display['Show-Klasse'].unique()]
                
                show_klasse_optionen = ["Alle Show-Klassen"] + vorhandene_sk
                wahl_show_klasse = st.selectbox("Nach Show-Klasse filtern:", show_klasse_optionen)
            with c_f4:
                geschlecht_optionen = ["Alle Geschlechter"] + sorted([str(g) for g in df_nom_display['Geschlecht'].unique() if g != "-"])
                wahl_geschlecht = st.selectbox("Nach Geschlecht filtern:", geschlecht_optionen)
            
            # Sortierzeile (Volle Breite darunten)
            c_s, _ = st.columns([1, 1])
            with c_s:
                sort_options = {
                    "Katalog-Nr.": "Katalog-Nr.",
                    "Rasse": "Rasse",
                    "Kategorie": "Kategorie",
                    "Klasse": "Klasse",
                    "Geschlecht": "Geschlecht",
                    "Richter": "Richter"
                }
                wahl_sortierung = st.selectbox("Primär sortieren nach:", list(sort_options.keys()))
            
            # --- FILTER LOGIK ANWENDEN ---
            if wahl_richter != "Alle Richter":
                df_nom_display = df_nom_display[df_nom_display['Richter'] == wahl_richter]
                
            if wahl_kategorie != "Alle Kategorien":
                df_nom_display = df_nom_display[df_nom_display['Kategorie'].astype(str) == wahl_kategorie]
                
            if wahl_show_klasse != "Alle Show-Klassen":
                df_nom_display = df_nom_display[df_nom_display['Show-Klasse'].astype(str) == wahl_klasse]
                
            if wahl_geschlecht != "Alle Geschlechter":
                df_nom_display = df_nom_display[df_nom_display['Geschlecht'] == wahl_geschlecht]
                
            # --- SORTIER LOGIK ANWENDEN ---
            if wahl_sortierung == "Katalog-Nr.":
                df_nom_display = df_nom_display.sort_values(by="Katalog-Nr.", key=lambda x: pd.to_numeric(x, errors='coerce'))
            else:
                df_nom_display = df_nom_display.sort_values(by=sort_options[wahl_sortierung])
            # -------------------------------------

            # Ergebnismeldung anpassen
            st.success(f"Gefunden: {len(df_nom_display)} nominierte Katze(n) mit den gewählten Filtern.")
            
            # Registerkarten zur Anzeige
            tab_alle, tab_t1, tab_t2 = st.tabs(["Alle anzeigen", "Tag 1 (Samstag)", "Tag 2 (Sonntag)"])
            
            with tab_alle:
                if not df_nom_display.empty:
                    st.dataframe(df_nom_display, use_container_width=True, hide_index=True)
                else:
                    st.info("Keine Einträge für diese Filterkombination.")
            
            with tab_t1:
                df_t1 = df_nom_display[df_nom_display['Tag'].str.contains('Tag 1')]
                if not df_t1.empty:
                    st.dataframe(df_t1, use_container_width=True, hide_index=True)
                else:
                    st.info("Keine passenden Nominationen für Tag 1 vorhanden.")
                    
            with tab_t2:
                df_t2 = df_nom_display[df_nom_display['Tag'].str.contains('Tag 2')]
                if not df_t2.empty:
                    st.dataframe(df_t2, use_container_width=True, hide_index=True)
                else:
                    st.info("Keine passenden Nominationen für Tag 2 vorhanden.")

            # CSV Download (berücksichtigt alle aktiven Filter und Sortierungen!)
            if not df_nom_display.empty:
                csv = df_nom_display.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 Gefilterte Liste als CSV herunterladen",
                    data=csv,
                    file_name="nominierte_katzen_gefiltert.csv",
                    mime="text/csv",
                )
        else:
            st.info("In der Excel-Datei (Spalte 'SELECTION') sind aktuell keine Katzen mit 'X' nominiert.")
            
    if st.button("⬅️ Zurück zum Hauptmenü", key="back_from_nom"):
        set_view("Home")
        
            
# --- NEUER MENÜPUNKT: JUDGE LIST ---
elif st.session_state.view == "Judge_List" or st.session_state.view == "Judge List":
    display_header_with_logo("📊 Judge Book")
    st.write("Sieh sofort, welche Katzen in den jeweiligen Klassen direkt gegeneinander antreten.")
    
    df_full = load_labels()
    
    if df_full is not None:
        # 1. Filter-Ebene: Tag & Richter
        tag = st.sidebar.radio("Tag auswählen:", ["Tag 1", "Tag 2"], key="jl_tag_selector").upper()
        r_col = f"RICHTER {tag}"
        
        # Alle Richter holen, die an diesem Tag aktiv sind
        all_j = sorted([r for r in df_full[df_full[tag].astype(str).str.upper() == 'X'][r_col].unique() if str(r) != "nan"])
        
        c1, c2 = st.columns(2)
        mein_richter = c1.selectbox("Richter filtern:", ["--"] + all_j, key="jl_judge")
        
        if mein_richter != "--":
            # Kategorien für diesen Richter ermitteln
            df_richter_alle = df_full[(df_full[tag].astype(str).str.upper() == 'X') & (df_full[r_col] == mein_richter)]
            verfuegbare_kategorien = sorted(list(set([str(cat).replace('.0', '') for cat in df_richter_alle['KATEGORIE'].unique() if pd.notna(cat)])))
            meine_kategorie = c2.selectbox("Kategorie filtern:", verfuegbare_kategorien, key="jl_cat")
            
            # Daten filtern und sortieren nach Katalog-Nr
            df_filtered = df_richter_alle[df_richter_alle['KATEGORIE'].astype(str).str.replace('.0', '') == meine_kategorie].sort_values('KATALOG-NR')
            
            st.divider()
            
            # --- NEU: ANZAHL DER KATZEN ANZEIGEN ---
            anzahl_katzen = len(df_filtered)
            st.markdown(f"**Gemeldete Katzen in dieser Auswahl:** {anzahl_katzen}")
            # ---------------------------------------
            
            # Vorbereitung der Tabellendaten
            table_rows = []
            
            for _, row in df_filtered.iterrows():
                nr = row['KAT_STR']
                ems = row.get('RASSE_KURZ', row.get('RASSE', '')) + " " + row.get('FARBE', '')
                sex = row.get('GESCHLECHT', 'N/A')
                klasse = str(row.get('KLASSE_INTERNAL', row.get('AUSSTELLUNGSKLASSE', row.get('KLASSE', 'N/A')))).replace('.0', '')
                
                # Geburtsdatum formatieren
                geb_cols = [c for c in row.index if "GEB" in c or "GEBURT" in c]
                geb_datum = row[geb_cols[0]] if geb_cols else row.get('GEB_DATUM', 'N/A')
                if isinstance(geb_datum, pd.Timestamp): 
                    geb_datum = geb_datum.strftime('%d.%m.%Y')
                elif pd.isna(geb_datum) or str(geb_datum).strip().lower() == "nan": 
                    geb_datum = "–"
                
                # 8-Spalten Logik initialisieren
                x_cols = {"Ad ♂": "", "Ad ♀": "", "K ♂": "", "K ♀": "", "11 ♂": "", "11 ♀": "", "12 ♂": "", "12 ♀": ""}
                
                                # Automatische Zuordnung basierend auf Klasse und Geschlecht (Sex)
                try:
                    kl_num = int(klasse)
                    
                    # KORREKTUR: Erkennt nun "1,0" sowie "m" und "M" zuverlässig als Kater
                    sex_clean = str(sex).strip().lower()
                    is_male = (sex_clean == "1,0" or sex_clean == "m")
                    
                    if kl_num in [1, 3, 5, 7, 9]:
                        x_cols["Ad ♂" if is_male else "Ad ♀"] = "X"
                    elif kl_num in [2, 4, 6, 8, 10]:
                        x_cols["K ♂" if is_male else "K ♀"] = "X"
                    elif kl_num == 11:
                        x_cols["11 ♂" if is_male else "11 ♀"] = "X"
                    elif kl_num == 12:
                        x_cols["12 ♂" if is_male else "12 ♀"] = "X"
                except ValueError:
                    pass # Für den Fall, dass Klassen-Werte nicht konvertierbar sind
                
                # Zeile zusammensetzen
                row_entry = {
                    "Nr.": nr,
                    "EMS-Code": ems,
                    "Sex": sex,
                    "Kl.": klasse,
                    "Geboren": geb_datum,
                    **x_cols
                }
                table_rows.append(row_entry)
            
            if table_rows:
                df_display = pd.DataFrame(table_rows)
                
                # Darstellung als sortierbare Streamlit-Tabelle
                st.dataframe(
                    df_display, 
                    use_container_width=True, 
                    hide_index=True,
                    height=650,
                    column_config={
                        "Nr.": st.column_config.TextColumn(width="small"),
                        "Sex": st.column_config.TextColumn(width="small"),
                        "Kl.": st.column_config.TextColumn(width="small"),
                        "Ad ♂": st.column_config.TextColumn(alignment="center"),
                        "Ad ♀": st.column_config.TextColumn(alignment="center"),
                        "K ♂": st.column_config.TextColumn(alignment="center"),
                        "K ♀": st.column_config.TextColumn(alignment="center"),
                        "11 ♂": st.column_config.TextColumn(alignment="center"),
                        "11 ♀": st.column_config.TextColumn(alignment="center"),
                        "12 ♂": st.column_config.TextColumn(alignment="center"),
                        "12 ♀": st.column_config.TextColumn(alignment="center"),
                    }
                )
                
                st.caption("💡 Tipp: Klicke auf die Spaltenköpfe (z.B. '12 ♀'), um die Katzen zu sortieren und Konkurrenten direkt im Blick zu haben!")
            else:
                st.info("Keine Katzen für diese Auswahl gemeldet.")
        else:
            st.info("Bitte wähle einen Richter aus der Liste aus, um die Judge List anzuzeigen.")
            
    if st.button("⬅️ Zurück zum Hauptmenü", key="back_from_judgebook"):
        set_view("Home")

# --- EIGENSTÄNDIGE VIEW: NOMINATION LABELS DRUCK ---
elif st.session_state.view in ["Nomination_Labels", "Nomination Labels"]:
    display_header_with_logo("🖨️ Nomination Labels Druckzentrale")
    st.write("Generiere hier die exakten Druck-Labels (8 Stück pro A4-Seite). Jede Klasse beginnt ein neues Blatt.")
    
    df_full = load_labels()
    
    if df_full is not None:
        # Nur Katzen filtern mit Nominierungs-X
        df_nominierte = df_full[df_full['SELECTION'].astype(str).str.upper() == 'X'].copy()
        
        if not df_nominierte.empty:
            st.info(f"Aktuell sind **{len(df_nominierte)}** Katzen für den Labeldruck bereit.")
            
            # ABSOLUT STABILE IMPORTS
            import reportlab
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.lib import colors
            from io import BytesIO

            def generate_avery_labels(df):
                buffer = BytesIO()
                c = canvas.Canvas(buffer, pagesize=A4)
                
                # Avery J8165 exakte Maße
                mm = 2.83464
                label_width = 99.1 * mm
                label_height = 67.7 * mm
                margin_left = 5.9 * mm
                margin_top = 13.1 * mm
                
                color_map = {
                    "AM": colors.HexColor("#ffff00"),   # Gelb
                    "AW": colors.HexColor("#ff99cc"),   # Rosa
                    "KM": colors.HexColor("#99cc00"),   # Grün
                    "KW": colors.HexColor("#33ccff"),   # Blau
                    "JM": colors.HexColor("#cc99ff"),   # Pastell-Lila
                    "JW": colors.HexColor("#e60073"),   # Kräftiges Beeren-Pink
                    "KiM": colors.HexColor("#ffbf00"),  # Bernstein-Gelb
                    "KiW": colors.HexColor("#ff6600")   # Orange
                }
                
                # --- HILFSFELDER FÜR DIE SORTIERUNG ERZEUGEN ---
                sorted_rows = []
                for idx, row in df.iterrows():
                    # Flexibler Check für die Klasse-Spalte
                    klasse_val = row.get('KLASSE_INTERNAL', row.get('KLASSE', ''))
                    klasse_str = str(klasse_val).replace('.0', '')
                    sex = str(row.get('GESCHLECHT', '')).strip().upper()
                    kat_nr_str = str(row.get('KAT_STR', '')).replace('.0', '')
                    
                    try:
                        kat_nr_sort = int(kat_nr_str)
                    except:
                        kat_nr_sort = 9999
                    
                    badge_key = "AM"
                    badge_label = "Adult M"
                    sort_order = 0
                    
                    try:
                        kl_num = int(klasse_str)
                        is_male = (sex in ["1,0", "M", "MALE"])
                        if kl_num in [1, 3, 5, 7, 9]:
                            badge_key = "AM" if is_male else "AW"
                            badge_label = "Adult M" if is_male else "Adult W"
                            sort_order = 0 if is_male else 1
                        elif kl_num in [2, 4, 6, 8, 10]:
                            badge_key = "KM" if is_male else "KW"
                            badge_label = "Kastrat M" if is_male else "Kastrat W"
                            sort_order = 2 if is_male else 3
                        elif kl_num == 11:
                            badge_key = "JM" if is_male else "JW"
                            badge_label = "8-12 M" if is_male else "8-12 W"
                            sort_order = 4 if is_male else 5
                        elif kl_num == 12:
                            badge_key = "KiM" if is_male else "KiW"
                            badge_label = "4-8 M" if is_male else "4-8 W"
                            sort_order = 6 if is_male else 7
                    except:
                        if "K" in sex or "N" in sex:
                            badge_key = "KM" if "M" in sex else "KW"
                            badge_label = "MN" if "M" in sex else "FN"
                            sort_order = 2 if "M" in sex else 3
                        else:
                            badge_key = "AM"
                            badge_label = f"{klasse_str} {sex}"
                            sort_order = 8
                    
                    row_data = row.to_dict()
                    row_data['_sort_kat'] = str(row.get('KATEGORIE', '9')).replace('.0', '')
                    row_data['_sort_class'] = sort_order
                    row_data['_sort_kat_nr'] = kat_nr_sort
                    row_data['_badge_key'] = badge_key
                    row_data['_badge_label'] = badge_label
                    row_data['_clean_kat_nr'] = kat_nr_str
                    row_data['_clean_klasse'] = klasse_str
                    sorted_rows.append(row_data)
                
                df_sorted = pd.DataFrame(sorted_rows)
                df_sorted = df_sorted.sort_values(by=['_sort_kat', '_sort_class', '_sort_kat_nr']).reset_index(drop=True)
                
                grouped = df_sorted.groupby(['_sort_kat', '_sort_class'])
                
                is_first_page = True
                
                for (kat_name, class_idx), group in grouped:
                    if not is_first_page:
                        c.showPage()
                    is_first_page = False
                    
                    count = 0
                    for _, row in group.iterrows():
                        if count > 0 and count % 8 == 0:
                            c.showPage()
                            
                        page_idx = count % 8
                        col = page_idx % 2
                        row_idx = page_idx // 2
                        
                        x = margin_left + (col * label_width)
                        y = (297 * mm) - margin_top - ((row_idx + 1) * label_height)
                        
                        kat_nr = row['_clean_kat_nr']
                        kategorie = row['_sort_kat']
                        badge_label = row['_badge_label']
                        badge_bg = color_map.get(row['_badge_key'], colors.HexColor("#99cc00"))
                        
                        rasse = str(row.get('RASSE', ''))
                        farbe = str(row.get('FARBE', ''))
                        ems_code = f"{rasse} {farbe}".strip()
                        
                        geb_cols = [col for col in row.index if "GEB" in col or "GEBURT" in col]
                        geb_datum = row[geb_cols[0]] if geb_cols else row.get('GEB_DATUM', '-')
                        if isinstance(geb_datum, pd.Timestamp):
                            geb_datum = geb_datum.strftime('%d.%m.%Y')
                        
                        # --- ZEICHNEN ---
                        c.saveState()
                        
                        # Haardünner Rahmen (Schneide-/Ablösehilfe)
                        c.setStrokeColor(colors.HexColor("#e5e5e5"))
                        c.setLineWidth(0.2)
                        c.rect(x, y, label_width, label_height)
                        
                        # Oben Links: Kategorie
                        c.setFont("Helvetica", 14)
                        c.setFillColor(colors.black)
                        c.drawString(x + 6*mm, y + label_height - 10*mm, kategorie)
                        
                        # Oben Rechts: Farbiger Badge
                        badge_w = 22 * mm
                        badge_h = 6 * mm
                        bx = x + label_width - badge_w - 6*mm
                        by = y + label_height - 11*mm
                        
                        c.setFillColor(badge_bg)
                        c.rect(bx, by, badge_w, badge_h, fill=1, stroke=0)
                        
                        c.setFillColor(colors.black)
                        c.setFont("Helvetica-Bold", 11)
                        c.drawCentredString(bx + (badge_w / 2), by + 1.8*mm, badge_label)
                        
                        # Mitte: Große Katalognummer
                        c.setFont("Helvetica", 46)
                        c.drawCentredString(x + (label_width / 2), y + (label_height / 2) - 4*mm, kat_nr)
                        
                        # Unten Links: Rasse / EMS
                        c.setFont("Helvetica", 12)
                        c.drawString(x + 6*mm, y + 10*mm, ems_code)
                        
                        # Unten Rechts: Geburtsdatum
                        c.setFont("Helvetica", 12)
                        c.drawRightString(x + label_width - 6*mm, y + 10*mm, str(geb_datum))
                        
                        c.restoreState()
                        count += 1
                
                c.save()
                buffer.seek(0)
                return buffer.getvalue()

            # PDF Download Button
            pdf_labels = generate_avery_labels(df_nominierte)
            st.download_button(
                label="📥 Avery Zweckform PDF generieren & herunterladen",
                data=pdf_labels,
                file_name="KECB_Nomination_Labels_Sorted.pdf",
                mime="application/pdf"
            )
            
            # SAFE VORSCHAU: Holt nur die Spalten, die garantiert existieren
            st.write("### Vorschau der enthaltenen Katzen:")
            verfuegbare_spalten = [col for col in ['KAT_STR', 'KATEGORIE', 'KLASSE_INTERNAL', 'GESCHLECHT', 'RASSE', 'FARBE'] if col in df_nominierte.columns]
            
            # Schöne Namen für die Anzeige definieren
            schoene_namen = {
                "KAT_STR": "Kat.-Nr.",
                "KATEGORIE": "Kategorie",
                "KLASSE_INTERNAL": "Klasse",
                "GESCHLECHT": "Geschlecht",
                "RASSE": "Rasse",
                "FARBE": "Farbe"
            }
            
            # Nur die Konfigurationen übergeben, deren Spalten auch wirklich da sind
            aktuelle_config = {col: schoene_namen[col] for col in verfuegbare_spalten if col in schoene_namen}
            st.dataframe(df_nominierte[verfuegbare_spalten], column_config=aktuelle_config, use_container_width=True, hide_index=True)
            
        if st.button("⬅️ Zurück zum Hauptmenü", key="back_from_labels"):
            set_view("Home")



# ADMIN PANEL
elif st.session_state.view == "Admin_Panel":
    display_header_with_logo("⚙️ Admin-Konsole")
    if st.button("ALLE DATEN ZURÜCKSETZEN"):
        store.data = {}
        store.active_overlay = None
        st.success("Speicher geleert!")
        
    if st.button("⬅️ Zurück zum Hauptmenü", key="back_from_admin"):
        set_view("Home")
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
