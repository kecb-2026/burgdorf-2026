import streamlit as st
import pandas as pd
import re

# --- 1. SETUP & STYLING ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

st.markdown("""
    <style>
    /* Startbildschirm Buttons */
    .stButton button { 
        width: 100%; 
        height: 120px; 
        font-size: 26px !important; 
        font-weight: bold !important; 
        border-radius: 15px !important;
        margin-bottom: 20px;
        border: 2px solid #1a4a9e !important;
    }
    
    /* Dashboard & Cards */
    .judge-col { border: 3px solid #1a4a9e; padding: 15px; border-radius: 20px; background-color: #ffffff; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .judge-col h3 { font-size: 32px !important; color: white; background-color: #1a4a9e; padding: 10px; border-radius: 10px; text-align: center; }
    
    .cat-card { 
        padding: 20px; 
        border: 1px solid #e0e0e0; 
        margin-bottom: 25px; 
        text-align: center; 
        background-color: #ffffff; 
        border-radius: 20px; 
        box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
    }
    .cat-number { font-size: 110px !important; font-weight: 900 !important; color: #1a4a9e; line-height: 0.8; margin: 10px 0; }
    .cat-label { font-size: 26px; color: #333; font-weight: bold; margin: 5px 0 15px 0; }
    
    /* Tags & Steward Farben */
    .tag-container { margin-top: 10px; display: flex; justify-content: center; flex-wrap: wrap; gap: 10px; }
    .tag { font-weight: bold; padding: 10px 20px; border-radius: 10px; font-size: 22px; display: inline-block; }
    
    .tag-aufruf { background-color: #007bff; color: white; }
    @keyframes blinker { 50% { opacity: 0.2; } }
    .tag-biv { background-color: #28a745; color: white; animation: blinker 1.5s linear infinite; }
    .tag-nom { background-color: #ffc107; color: black; animation: blinker 1s linear infinite; }

    /* Best in Show Grid */
    .bis-table { width: 100%; border-collapse: collapse; margin-bottom: 30px; table-layout: fixed; background: white; }
    .bis-table th, .bis-table td { border: 2px solid #1a4a9e; padding: 5px; text-align: center; vertical-align: middle; min-height: 100px; }
    .bis-table th { background-color: #1a4a9e; color: white; font-size: 18px; }
    .class-header { background-color: #f0f0f0 !important; font-weight: bold; text-align: left !important; width: 180px; color: #1a4a9e; }
    .bis-nr { font-size: 48px !important; font-weight: 900 !important; color: #000; margin: 0; line-height: 1; }
    .bis-label { font-size: 13px; font-weight: bold; color: #333; margin-top: 2px; }
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

# --- 4. HILFSFUNKTIONEN ---
def roman_to_numeric(text):
    roman_map = {'IX': '9', 'VIII': '8', 'VII': '7', 'VI': '6', 'IV': '4', 'V': '5', 'III': '3', 'II': '2', 'I': '1'}
    if pd.isna(text) or text == "": return ""
    res = str(text).upper()
    for rom, num in roman_map.items():
        res = re.sub(rf'\b{rom}\b', num, res)
    return res

@st.cache_data(ttl=30)
def load_labels():
    try:
        df = pd.read_excel("LABELS.xlsm", engine='openpyxl', header=1)
        df.columns = df.columns.astype(str).str.strip()
        df['KAT_STR'] = df['Katalog-Nr'].astype(str).str.replace('.0', '', regex=False)
        return df
    except: return None

def get_full_label(row):
    r = row.get('Rasse_Kurz', row.get('Rasse', ''))
    g = roman_to_numeric(row.get('Farbgruppe', ''))
    e = row.get('Farbe', '')
    label = f"{r} {g}".strip()
    if pd.notna(e) and e != "": label += f" ({e})"
    return label

def set_view(name):
    st.session_state.view = name
    st.rerun()

# --- 7. VIEWS ---

if st.session_state.view == "Home":
    st.title("🐾 KECB Burgdorf 2026")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📢 LIVE-DASHBOARD"): set_view("Dashboard")
        if st.button("🏆 BEST IN SHOW GRID"): set_view("BIS_Grid")
    with col2:
        if st.button("📝 STEWARD-PULT"): set_view("Steward_Login")
        if st.button("👨‍⚖️ RICHTER / ⚙️ ADMIN"): set_view("Admin_Login")

elif st.session_state.view == "Steward_Login":
    st.title("🔒 Steward Login")
    pwd = st.text_input("Passwort", type="password")
    if st.button("Anmelden") and pwd == "steward2026": set_view("Steward_Panel")
    if st.button("Abbrechen"): set_view("Home")

elif st.session_state.view == "Admin_Login":
    st.title("⚙️ Admin / Richter Login")
    pwd = st.text_input("Passwort", type="password")
    if st.button("Anmelden") and pwd == "admin2026": set_view("Admin_Panel")
    if st.button("Abbrechen"): set_view("Home")

else:
    st.sidebar.title("KECB 2026")
    tag = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"])
    df_full = load_labels()
    r_col = f"Richter {tag}"
    df_tag = df_full[df_full[tag].astype(str).str.upper() == 'X'].copy() if df_full is not None else None

    if st.sidebar.button("🏠 Logout"): set_view("Home")

    if st.session_state.view == "Dashboard":
        st.title(f"Live-Aufruf ({tag})")
        if df_tag is not None:
            judges = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
            cols = st.columns(len(judges))
            for i, j in enumerate(judges):
                with cols[i]:
                    st.markdown(f"<div class='judge-col'><h3>{j}</h3>", unsafe_allow_html=True)
                    for k, v in store.data.items():
                        nr, r_n = k.split("|")
                        if r_n == j and any(v.values()):
                            m = df_tag[df_tag['KAT_STR'] == nr]
                            if not m.empty:
                                row = m.iloc[0]
                                card_html = f"""<div class='cat-card'>
                                    <div style='font-size:20px; font-weight:bold;'>Kategorie {row['Kategorie']}</div>
                                    <div class='cat-number'>{nr}</div>
                                    <div class='cat-label'>{get_full_label(row)}</div>
                                    <div class='tag-container'>"""
                                if v.get("Aufruf"): card_html += "<span class='tag tag-aufruf'>AUFRUF</span>"
                                if v.get("BIV"): card_html += "<span class='tag tag-biv'>BIV</span>"
                                if v.get("NOM"): card_html += "<span class='tag tag-nom'>NOM</span>"
                                st.markdown(card_html + "</div></div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.view == "Steward_Panel":
        st.title("Steward-Steuerung")
        all_j = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
        mein_richter = st.selectbox("Richter wählen:", ["--"] + all_j)
        if mein_richter != "--":
            df_j = df_tag[df_tag[r_col] == mein_richter].sort_values(['Katalog-Nr'])
            for _, row in df_j.iterrows():
                nr = row['KAT_STR']; k = f"{nr}|{mein_richter}"
                if k not in store.data: store.data[k] = {"Aufruf": False, "BIV": False, "NOM": False}
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                c1.write(f"**#{nr}** (Kat {row['Kategorie']}) - {get_full_label(row)}")
                store.data[k]["Aufruf"] = c2.checkbox("Ruf", value=store.data[k]["Aufruf"], key=f"a{k}")
                store.data[k]["BIV"] = c3.checkbox("BIV", value=store.data[k]["BIV"], key=f"b{k}")
                store.data[k]["NOM"] = c4.checkbox("NOM", value=store.data[k]["NOM"], key=f"n{k}")
