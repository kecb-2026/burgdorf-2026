import streamlit as st
import pandas as pd
import re

# --- 1. SETUP & STYLING ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

st.markdown("""
    <style>
    /* Dashboard Grid Style */
    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 20px;
        padding: 20px;
    }

    /* Die weißen Karten aus image_4.png */
    .cat-card-dash {
        background-color: white;
        border-radius: 25px;
        padding: 30px 15px;
        text-align: center;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 180px;
    }

    .cat-number-dash {
        font-size: 56px !important;
        font-weight: 900 !important;
        color: #1a4a9e;
        margin-bottom: 15px;
        line-height: 1;
    }

    /* Status Badges */
    .tag-container-dash {
        display: flex;
        flex-direction: column;
        gap: 6px;
        width: 80%;
    }

    .tag-dash {
        font-weight: bold;
        padding: 5px 10px;
        border-radius: 8px;
        font-size: 14px;
        color: white;
        text-align: center;
    }

    .tag-aufruf { background-color: #007bff; }
    .tag-biv { background-color: #28a745; }
    .tag-nom { background-color: #ffc107; color: black; }

    /* Buttons & Standard-Elemente */
    .stButton button { 
        width: 100%; height: 60px; font-weight: bold !important; border-radius: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GLOBALER SPEICHER ---
class GlobalStore:
    def __init__(self):
        self.data = {} 

@st.cache_resource
def get_store():
    return GlobalStore()

store = get_store()

if "view" not in st.session_state:
    st.session_state.view = "Home"

# --- 3. HILFSFUNKTIONEN ---
def roman_to_numeric(text):
    roman_map = {'IX': '9', 'VIII': '8', 'VII': '7', 'VI': '6', 'IV': '4', 'V': '5', 'III': '3', 'II': '2', 'I': '1'}
    if pd.isna(text) or text == "": return ""
    res = str(text).upper()
    for rom, num in roman_map.items(): res = re.sub(rf'\b{rom}\b', num, res)
    return res

@st.cache_data(ttl=5)
def load_labels():
    try:
        df = pd.read_excel("LABELS.xlsx", engine='openpyxl')
        df.columns = [str(c).strip().upper() for c in df.columns]
        if 'KATALOG-NR' in df.columns:
            df['KAT_STR'] = df['KATALOG-NR'].astype(str).replace(r'\.0$', '', regex=True)
        return df
    except: return None

def set_view(name):
    st.session_state.view = name
    st.rerun()

# --- 4. VIEWS ---

if st.session_state.view == "Home":
    st.title("🐾 KECB Burgdorf 2026")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📢 LIVE-DASHBOARD"): set_view("Dashboard")
        if st.button("🏆 BEST IN SHOW (PUBLIC)"): set_view("BIS_Public")
    with c2:
        if st.button("📝 STEWARD-PULT"): set_view("Steward_Login")
        if st.button("👨‍⚖️ BIS ADMIN / CONTROL"): set_view("BIS_Admin_Control")

elif st.session_state.view == "Dashboard":
    st.title("📢 Live-Aufruf & Status")
    
    # Aggregierte Daten für das Grid sammeln
    active_cats = {}
    for key, states in store.data.items():
        if "|" in key:
            kat_nr, _ = key.split("|")
            if any(states.values()):
                if kat_nr not in active_cats:
                    active_cats[kat_nr] = {"Aufruf": False, "BIV": False, "NOM": False}
                for s_key in ["Aufruf", "BIV", "NOM"]:
                    if states.get(s_key): active_cats[kat_nr][s_key] = True

    if active_cats:
        sorted_nrs = sorted(active_cats.keys(), key=lambda x: int(x) if x.isdigit() else 999)
        html_grid = "<div class='dashboard-grid'>"
        for nr in sorted_nrs:
            s = active_cats[nr]
            tags = ""
            if s["Aufruf"]: tags += "<span class='tag-dash tag-aufruf'>Aufruf</span>"
            if s["BIV"]: tags += "<span class='tag-dash tag-biv'>BIV</span>"
            if s["NOM"]: tags += "<span class='tag-dash tag-nom'>NOM</span>"
            
            html_grid += f"""
            <div class='cat-card-dash'>
                <div class='cat-number-dash'>{nr}</div>
                <div class='tag-container-dash'>{tags}</div>
            </div>"""
        html_grid += "</div>"
        st.markdown(html_grid, unsafe_allow_html=True)
    
    if st.button("⬅️ Zurück"): set_view("Home")

elif st.session_state.view == "Steward_Panel":
    st.title("📝 Steward-Pult")
    df = load_labels()
    if df is not None:
        tag = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"]).upper()
        r_col = f"RICHTER {tag}"
        judges = sorted([r for r in df[df[tag] == 'X'][r_col].unique() if str(r) != "nan"])
        mein_richter = st.selectbox("Richter wählen:", ["--"] + judges)
        
        if mein_richter != "--":
            df_j = df[(df[tag] == 'X') & (df[r_col] == mein_richter)].sort_values('KATALOG-NR')
            for _, row in df_j.iterrows():
                nr = row['KAT_STR']; k = f"{nr}|{mein_richter}"
                if k not in store.data: store.data[k] = {"Aufruf": False, "BIV": False, "NOM": False}
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                c1.write(f"**#{nr}**")
                store.data[k]["Aufruf"] = c2.checkbox("Ruf", value=store.data[k]["Aufruf"], key=f"a{k}")
                store.data[k]["BIV"] = c3.checkbox("BIV", value=store.data[k]["BIV"], key=f"b{k}")
                store.data[k]["NOM"] = c4.checkbox("NOM", value=store.data[k]["NOM"], key=f"n{k}")
    if st.button("⬅️ Zurück"): set_view("Home")

elif st.session_state.view == "Steward_Login":
    st.title("🔒 Login"); pwd = st.text_input("Passwort", type="password")
    if st.button("Anmelden") and pwd == "steward2026": set_view("Steward_Panel")
    if st.button("⬅️ Zurück"): set_view("Home")

# (Andere Views wie BIS_Admin_Control oder BIS_Public hier einfügen falls nötig)
