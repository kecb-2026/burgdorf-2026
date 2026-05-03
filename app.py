import streamlit as st
import pandas as pd
import re
import time
from streamlit_autorefresh import st_autorefresh

# --- 1. SETUP & STYLING ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

# Zentrale Logo URL
LOGO_URL = "logo.GIF"

st.markdown("""
    <style>
    @keyframes blinker { 50% { opacity: 0.1; } }
    
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


    /* Die spezifischen Boxen nutzen nun alle den Flex-Container */
    .class-label-box { background-color: #e9ecef; border: 2px solid #1a4a9e; color: #1a4a9e; font-weight: 800; }
    .cat-card { background-color: #ffffff; border: 2px solid #1a4a9e; }
    .placeholder-box { background-color: #f8f9fa !important; border: 1px solid #d1d1d1; color: #cccccc; }
    .winner-card { background-color: #ffcccc !important; border: 3px solid #ff4d4d !important; }



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
        animation: fadeIn 0.5s ease-out;
        padding: 40px;
    }
    
        /* Initialen Kreise */
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
        background-color: #1a4a9e;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
        font-weight: bold;
        cursor: help; /* Zeigt an, dass man drüberfahren kann */
    }

    
    .overlay-backdrop {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: rgba(0,0,0,0.7);
        z-index: 9999998;
    }

    /* TITEL ANPASSUNGEN */
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
    
    /* NEU: Klasse für die Hauptüberschriften neben dem Logo */
    .header-text {
        text-transform: uppercase !important;
        font-size: 26px !important;
        font-weight: bold;
        color: #1a4a9e;
        margin: 0 !important;
    }

    @keyframes fadeIn { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }

    .stButton button { width: 100%; height: 50px; font-size: 13px !important; font-weight: bold !important; border-radius: 12px !important; margin-bottom: 5px; border: 2px solid #1a4a9e !important; }
    
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
        height: 80px; width: 100%; line-height: 1.1; 
    }

    .cat-card, .placeholder-box { padding: 5px; border: 2px solid #1a4a9e; text-align: center; background-color: #ffffff; border-radius: 14px; margin-bottom: 5px; min-height: 80px; display: flex; height:120px; flex-direction: column; justify-content: center; align-items: center; }
    .placeholder-box { border: 1px solid #d1d1d1; background-color: #f2f2f2 !important; color: #999999; }
    .winner-card { border: 3px solid #ff4d4d !important; background-color: #ffcccc !important; color: #b21f2d !important; }
    .cat-number { font-size: 28px !important; font-weight: 900 !important; color: #1a4a9e; line-height: 1.0; }
    .cat-details { font-size: 14px !important; color: #333; font-weight: bold; margin-top: 2px; line-height: 1.1; }
    
    .tag-container { margin-top: 4px; display: flex; justify-content: center; flex-wrap: wrap; gap: 3px; }
    .tag { font-weight: bold; padding: 4px 8px; border-radius: 6px; font-size: 11px; text-transform: uppercase; color: white; }
    .tag-zumrichten { background-color: #007bff; }
    .tag-biv { background-color: #28a745; animation: blinker 1.5s linear infinite; }
    .tag-nom { background-color: #ffc107; color: black; animation: blinker 1s linear infinite; }
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

# --- 3. SESSION STATE & URL PARAMETER ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = "Public"
if "view" not in st.session_state:
    st.session_state.view = "Dashboard"

q_params = st.query_params
if "view" in q_params:
    v_param = q_params["view"].lower()
    if v_param == "katzenaufruf": st.session_state.view = "Dashboard"
    elif v_param == "bis": st.session_state.view = "BIS_Public"
    elif v_param in ["admin", "steward", "richter", "bis-admin"]:
        st.session_state.view = "Login"
        st.session_state.target_role = v_param

def logout():
    st.session_state.authenticated = False
    st.session_state.user_role = "Public"
    st.session_state.view = "Dashboard"
    st.rerun()

# --- 4. HILFSFUNKTIONEN ---

def display_header_with_logo(text):
    """Zeigt die Überschrift links und das Logo rechtsbündig an"""
    col_text, col_logo = st.columns([5, 1]) 
    with col_text:
        st.markdown(f"<p class='header-text'>{text}</p>", unsafe_allow_html=True)
    with col_logo:
        st.markdown("<div style='display: flex; justify-content: flex-end;'>", unsafe_allow_html=True)
        st.image(LOGO_URL, width=65)
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
                <img src="https://kecb.ch/wp-content/uploads/2020/01/Logo-Link-weiss-279x300-1.gif" width="100">
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
    g = roman_to_numeric(row.get('FARBGRUPPE', ''))
    e = row.get('FARBE', '')
    return f"{r} {g} ({e})".strip()

def set_view(name):
    store.active_overlay = None   # <-- WICHTIG
    st.session_state.view = name
    st.rerun()

# --- 5. NAVIGATION & ZUGRIFF ---
access_map = {
    "Public": ["Dashboard", "BIS_Public", "Login"],
    "Richter": ["Judge_Voting", "Dashboard", "BIS_Public"],
    "Steward": ["Steward_Panel", "Dashboard", "BIS_Public"],
    "Admin": ["Home", "Dashboard", "BIS_Public", "Judge_Voting", "Steward_Panel", "BIS_Admin_Control", "Admin_Panel"]
}

available_views = access_map.get(st.session_state.user_role, ["Dashboard"])
st.sidebar.image(LOGO_URL, width=100)

st.session_state.view = st.sidebar.radio("Menü:", available_views, 
    index=available_views.index(st.session_state.view) if st.session_state.view in available_views else 0)

if st.session_state.authenticated:
    if st.sidebar.button("Abmelden"): logout()
elif st.session_state.view != "Login":
    if st.sidebar.button("🔒 Interner Login"): set_view("Login")

# --- 6. VIEWS ---

# LOGIN VIEW
if st.session_state.view == "Login":
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.image(LOGO_URL, width=120)
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
            set_view("Home")
        elif role_input == "Steward" and password == "steward2026":
            st.session_state.user_role, st.session_state.authenticated = "Steward", True
            set_view("Steward_Panel")
        elif role_input == "Richter" and password == "judge2026":
            st.session_state.user_role, st.session_state.authenticated = "Richter", True
            set_view("Judge_Voting")
        else:
            st.error("Passwort ungültig.")
    
    if st.button("Abbrechen"): set_view("Dashboard")
    st.markdown("</div>", unsafe_allow_html=True)

    
    
# HOME (ADMIN NUR)
elif st.session_state.view == "Home":
    display_header_with_logo("🐾 KECB Burgdorf 2026")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📢 LIVE-DASHBOARD"): set_view("Dashboard")
        if st.button("🏆 BEST IN SHOW (PUBLIC)"): set_view("BIS_Public")
        if st.button("🗳️ RICHTER-VOTING"): set_view("Judge_Voting")
    with col2:
        if st.button("📝 STEWARD-PULT"): set_view("Steward_Panel")
        if st.button("👨‍⚖️ BIS ADMIN / CONTROL"): set_view("BIS_Admin_Control")
        if st.button("⚙️ ADMIN-KONSOLE (RESET)"): set_view("Admin_Panel")

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
                    if final_nr and st.button(f"🏆 PUBLIC OVERLAY STARTEN (#{final_nr})", key=f"btn_ov_{sel_cat}_{label}"):
                        w_match = df_full[df_full['KAT_STR'] == str(final_nr)]
                        if not w_match.empty:
                            store.active_overlay = w_match.iloc[0].to_dict()
                            store.overlay_start_time = time.time()
                            st.success(f"Overlay für #{final_nr} aktiviert!")

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
elif st.session_state.view == "BIS_Public":
    if hasattr(store, 'active_overlay') and store.active_overlay:
        if time.time() - store.overlay_start_time < 20:
            st.markdown(render_overlay_html(store.active_overlay), unsafe_allow_html=True)
            time.sleep(1); st.rerun() 
        else: store.active_overlay = None; st.rerun()

    def get_initials(name):
        """Erzeugt Initialen aus Vor- und Nachnamen (z.B. Martti Peltonen -> MP)"""
        parts = str(name).split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return str(name)[:2].upper()

    display_header_with_logo("🏆 Best in Show")
    df_full = load_labels()
    if df_full is not None:
        tag = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"]).upper()
        sel_cat = st.selectbox("Kategorie:", sorted(df_full['KATEGORIE'].unique()))
        
        bis_defs = [
            ("Adult Male", [1,3,5,7,9], "M"), ("Adult Female", [1,3,5,7,9], "W"), 
            ("Neuter Male", [2,4,6,8,10], "M"), ("Neuter Female", [2,4,6,8,10], "W"), 
            ("Junior 8-12 Male", [11], "M"), ("Junior 8-12 Female", [11], "W"), 
            ("Kitten 4-8 Male", [12], "M"), ("Kitten 4-8 Female", [12], "W")
        ]
        
        r_col = f"RICHTER {tag}"
        judges = sorted([r for r in df_full[df_full[tag].astype(str).str.upper() == 'X'][r_col].unique() if str(r) != "nan"])
        
        # Header
        cols = st.columns([0.8] + [1.2]*len(judges) + [0.8])
        for i, j in enumerate(judges): 
            cols[i+1].markdown(f"<div class='judge-header-box'>{j}</div>", unsafe_allow_html=True)
        cols[-1].markdown("<div class='judge-header-box' style='background-color:#b21f2d;'>BIS</div>", unsafe_allow_html=True)
        
        for label, klassen, geschl in bis_defs:
            r_cols = st.columns([0.8] + [1.2]*len(judges) + [0.8])
            r_cols[0].markdown(f"<div class='class-label-box'>{label}</div>", unsafe_allow_html=True)
            
            show_noms = store.data.get(f"reveal_{sel_cat}_{label}", False)
            winner_revealed = store.data.get(f"winner_reveal_{sel_cat}_{label}", False)
            
            for i, j in enumerate(judges):
                with r_cols[i+1]:
                    if show_noms:
                        m = df_full[
                            (df_full['SELECTION'].astype(str).str.upper() == 'X') & 
                            (df_full[r_col] == j) & 
                            (df_full['KATEGORIE'] == sel_cat) & 
                            (df_full['KLASSE_INTERNAL'].isin(klassen)) & 
                            (df_full['GESCHLECHT'].astype(str).str.upper() == geschl)
                        ]
                        
                        if not m.empty:
                            kat_nr = m.iloc[0]['KAT_STR']
                            circles_html = ""
                            
                            if winner_revealed:
                                prefix = f"v_{sel_cat}_{label}_"
                                all_votes = store.data.get("votes", {})
                                voters = [
                                    v_key.replace(prefix, "") 
                                    for v_key, v_val in all_votes.items() 
                                    if v_key.startswith(prefix) and str(v_val) == str(kat_nr)
                                ]
                                
                                if voters:
                                    circles = "".join([f"<div class='judge-circle' title='{v}'>{get_initials(v)}</div>" for v in voters])
                                    circles_html = f"<div class='judge-initials-container'>{circles}</div>"

                            st.markdown(f"""
                                <div class='cat-card'>
                                    <div class='cat-number'>{kat_nr}</div>
                                    <div class='cat-details'>{get_full_label(m.iloc[0])}</div>
                                    {circles_html}
                                </div>
                            """, unsafe_allow_html=True)
                        else: 
                            st.markdown("<div class='placeholder-box'>–</div>", unsafe_allow_html=True)
                    else: 
                        st.markdown("<div class='placeholder-box'>🔒</div>", unsafe_allow_html=True)
            
            # BIS GEWINNER SPALTE
            with r_cols[-1]:
                if winner_revealed:
                    prefix = f"v_{sel_cat}_{label}_"
                    winner_nr = store.data.get(f"override_{sel_cat}_{label}", "Automatisch (Stimmen)")
                    
                    if winner_nr == "Automatisch (Stimmen)" and "votes" in store.data:
                        vts = [v for k, v in store.data["votes"].items() if k.startswith(prefix) and v != "Keine Wahl"]
                        if vts: 
                            winner_nr = pd.Series(vts).value_counts().index[0]
                    
                    if winner_nr and winner_nr != "Automatisch (Stimmen)":
                        m_w = df_full[df_full['KAT_STR'] == str(winner_nr)]
                        if not m_w.empty: 
                            st.markdown(f"""
                                <div class='cat-card winner-card'>
                                    <div class='cat-number'>{winner_nr}</div>
                                    <div class='cat-details'>{get_full_label(m_w.iloc[0])}</div>
                                </div>
                            """, unsafe_allow_html=True)
                else: 
                    st.markdown("<div class='placeholder-box'>🔒</div>", unsafe_allow_html=True)
    st_autorefresh(interval=3000, key="bis_refresh_global")
    #time.sleep(3)
    #st.rerun()




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
                    for k, v in store.data.items():
                        if "|" in k and k.split("|")[1] == j and any(v.values()):
                            m = df_tag[df_tag['KAT_STR'] == k.split("|")[0]]
                            if not m.empty:
                                tags = "".join([f"<span class='tag tag-{t.lower().replace(' ', '')}'>{t}</span> " for t, val in v.items() if val])
                                st.markdown(f"<div class='cat-card'><div class='cat-number'>{k.split('|')[0]}</div><div class='cat-details'>{get_full_label(m.iloc[0])}</div><div class='tag-container'>{tags}</div></div>", unsafe_allow_html=True)
    #time.sleep(3); st.rerun()
    st_autorefresh(interval=3000, key="dash_refresh")

# STEWARD PANEL
elif st.session_state.view == "Steward_Panel":
    display_header_with_logo("📝 Steward-Pult")
    tag = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"]).upper()
    df_full = load_labels()
    if df_full is not None:
        r_col = f"RICHTER {tag}"
        all_j = sorted([r for r in df_full[df_full[tag].astype(str).str.upper() == 'X'][r_col].unique() if str(r) != "nan"])
        mein_richter = st.selectbox("Richter wählen:", ["--"] + all_j)
        if mein_richter != "--":
            df_j = df_full[(df_full[tag].astype(str).str.upper() == 'X') & (df_full[r_col] == mein_richter)].sort_values('KATALOG-NR')
            for _, row in df_j.iterrows():
                nr = row['KAT_STR']; k = f"{nr}|{mein_richter}"
                if k not in store.data: store.data[k] = {"Zum Richten": False, "BIV": False, "NOM": False}
                c1, c2, c3, c4 = st.columns([3, 1.2, 1, 1])
                c1.write(f"**#{nr}** {get_full_label(row)}")
                store.data[k]["Zum Richten"] = c2.checkbox("Zum Richten", value=store.data[k]["Zum Richten"], key=f"auf{k}")
                store.data[k]["BIV"] = c3.checkbox("BIV", value=store.data[k]["BIV"], key=f"biv{k}")
                store.data[k]["NOM"] = c4.checkbox("NOM", value=store.data[k]["NOM"], key=f"nom{k}")

# JUDGE VOTING
elif st.session_state.view == "Judge_Voting":
    display_header_with_logo("🗳️ Richter Abstimmung/Judges Votes")
    df_full = load_labels()
    if df_full is not None:
        tag = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"]).upper()
        r_col = f"RICHTER {tag}"; all_judges = sorted([r for r in df_full[r_col].unique() if str(r) != "nan"])
        c1, c2 = st.columns(2)
        active_j = c1.selectbox("Identität/Identity:", ["--"] + all_judges)
        active_cat = c2.selectbox("Kategorie/Category:", sorted(df_full['KATEGORIE'].unique()))
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

# ADMIN PANEL
elif st.session_state.view == "Admin_Panel":
    display_header_with_logo("⚙️ Admin-Konsole")
    if st.button("ALLE DATEN ZURÜCKSETZEN"):
        store.data = {}
        store.active_overlay = None
        st.success("Speicher geleert!")