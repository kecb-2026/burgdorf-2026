import streamlit as st
import pandas as pd
import re

# --- 1. SETUP & STYLING ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

st.markdown("""
    <style>
    /* Allgemeine Schrifteinstellungen für bessere Lesbarkeit */
    html, body, [class*="st-"] { color: #000000 !important; font-family: 'Arial', sans-serif; }

    /* Home Buttons */
    .stButton button { width: 100%; height: 100px; font-size: 24px !important; font-weight: bold !important; border-radius: 15px !important; margin-bottom: 20px; border: 3px solid #1a4a9e !important; background-color: #ffffff !important; color: #1a4a9e !important; }
    
    /* Dashboard & Cards */
    .judge-col { border: 3px solid #1a4a9e; padding: 15px; border-radius: 20px; background-color: #ffffff; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .judge-col h3 { font-size: 32px !important; color: white; background-color: #1a4a9e; padding: 10px; border-radius: 10px; text-align: center; }
    .cat-card { padding: 20px; border: 2px solid #ddd; margin-bottom: 25px; text-align: center; background-color: #ffffff; border-radius: 20px; }
    .cat-number { font-size: 110px !important; font-weight: 900 !important; color: #1a4a9e; line-height: 0.8; margin: 10px 0; }
    .cat-label { font-size: 26px; color: #000; font-weight: bold; }
    
    /* Tags im Dashboard */
    .tag-container { margin-top: 10px; display: flex; justify-content: center; flex-wrap: wrap; gap: 10px; }
    .tag { font-weight: bold; padding: 10px 20px; border-radius: 10px; font-size: 22px; display: inline-block; color: white; }
    .tag-aufruf { background-color: #007bff; }
    .tag-biv { background-color: #28a745; }
    .tag-nom { background-color: #ffc107; color: black !important; }

    /* --- STEWARD MODUL HIGH CONTRAST --- */
    .steward-section-header { background-color: #0d2a5e; color: white !important; padding: 15px; border-radius: 10px; margin: 20px 0 10px 0; font-size: 24px; font-weight: bold; text-align: center; }
    
    .steward-card { 
        background-color: #ffffff; 
        border: 2px solid #000000; 
        padding: 15px; 
        border-radius: 12px; 
        margin-bottom: 12px;
        color: #000000 !important;
    }
    .steward-card-alt { background-color: #f0f2f6; } /* Zebra-Look */
    
    .steward-nr { font-size: 35px !important; font-weight: 900 !important; color: #1a4a9e !important; }
    .steward-info-text { font-size: 18px !important; color: #000000 !important; font-weight: 600; }
    
    /* Spaltenüberschriften im Steward-Pult */
    .steward-label-header { font-weight: bold; color: #000; text-align: center; font-size: 16px; text-transform: uppercase; margin-bottom: 5px; }
    
    /* Best in Show Grid */
    .bis-table { width: 100%; border-collapse: collapse; background: white; color: black; }
    .bis-table th, .bis-table td { border: 2px solid #000; padding: 10px; text-align: center; }
    .bis-table th { background-color: #1a4a9e; color: white; }
    .bis-nr { font-size: 48px !important; font-weight: 900 !important; color: #000; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GLOBALER SPEICHER ---
class GlobalStore:
    def __init__(self): self.data = {} 
@st.cache_resource
def get_store(): return GlobalStore()
store = get_store()

if "view" not in st.session_state: st.session_state.view = "Home"

# --- 3. HELPER ---
def roman_to_numeric(text):
    roman_map = {'IX': '9', 'VIII': '8', 'VII': '7', 'VI': '6', 'IV': '4', 'V': '5', 'III': '3', 'II': '2', 'I': '1'}
    if pd.isna(text) or text == "": return ""
    res = str(text).upper()
    for rom, num in roman_map.items(): res = re.sub(rf'\b{rom}\b', num, res)
    return res

@st.cache_data(ttl=10)
def load_labels():
    try:
        df = pd.read_excel("LABELS.xlsm", engine='openpyxl', header=1)
        df.columns = df.columns.astype(str).str.strip()
        df['KAT_STR'] = df['Katalog-Nr'].astype(str).str.replace('.0', '', regex=False)
        return df
    except: return None

def get_full_label(row):
    r, g, e = row.get('Rasse_Kurz', ''), row.get('Farbgruppe', ''), row.get('Farbe', '')
    label = f"{r} {roman_to_numeric(g)}".strip()
    if pd.notna(e) and e != "": label += f" ({e})"
    return label

# --- 4. VIEWS ---

if st.session_state.view == "Home":
    st.title("🐾 KECB Burgdorf 2026")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📢 LIVE-DASHBOARD"): st.session_state.view = "Dashboard"; st.rerun()
        if st.button("🏆 BIS GRID"): st.session_state.view = "BIS_Grid"; st.rerun()
    with c2:
        if st.button("📝 STEWARD-PULT"): st.session_state.view = "Steward_Login"; st.rerun()
        if st.button("⚙️ ADMIN / RICHTER"): st.session_state.view = "Admin_Login"; st.rerun()

elif "Login" in st.session_state.view:
    st.title("🔒 Login")
    pwd = st.text_input("Passwort", type="password")
    if st.button("Anmelden"):
        if "Steward" in st.session_state.view and pwd == "steward2026": st.session_state.view = "Steward_Panel"; st.rerun()
        elif "Admin" in st.session_state.view and pwd == "admin2026": st.session_state.view = "Admin_Panel"; st.rerun()
        else: st.error("Falsch!")
    if st.button("Zurück"): st.session_state.view = "Home"; st.rerun()

else:
    df_full = load_labels()
    tag = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"])
    r_col = f"Richter {tag}"
    df_tag = df_full[df_full[tag].astype(str).str.upper() == 'X'].copy() if df_full is not None else None
    if st.sidebar.button("🏠 Logout"): st.session_state.view = "Home"; st.rerun()

    if st.session_state.view == "Dashboard":
        cat_filter = st.sidebar.multiselect("Kategorien:", sorted(df_tag['Kategorie'].unique()), default=sorted(df_tag['Kategorie'].unique()))
        st.title(f"Live ({tag})")
        if df_tag is not None:
            judges = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
            cols = st.columns(len(judges))
            for i, j in enumerate(judges):
                with cols[i]:
                    st.markdown(f"<div class='judge-col'><h3>{j}</h3>", unsafe_allow_html=True)
                    for k, v in store.data.items():
                        nr, r_n = k.split("|")
                        if r_n == j and any(v.values()):
                            m = df_tag[(df_tag['KAT_STR'] == nr) & (df_tag['Kategorie'].isin(cat_filter))]
                            if not m.empty:
                                row = m.iloc[0]
                                card = f"<div class='cat-card'><div class='cat-number'>{nr}</div><div class='cat-label'>{get_full_label(row)}</div><div class='tag-container'>"
                                if v.get("Aufruf"): card += "<span class='tag tag-aufruf'>AUFRUF</span>"
                                if v.get("BIV"): card += "<span class='tag tag-biv'>BIV</span>"
                                if v.get("NOM"): card += "<span class='tag tag-nom'>NOM</span>"
                                st.markdown(card + "</div></div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.view == "Steward_Panel":
        st.title("Steward Steuerung")
        all_j = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
        mein_richter = st.selectbox("Richter:", ["--"] + all_j)
        
        if mein_richter != "--":
            # Headerzeile für die Spalten
            h1, h2, h3, h4 = st.columns([2, 1, 1, 1])
            h1.markdown("<div class='steward-label-header'>Katze</div>", unsafe_allow_html=True)
            h2.markdown("<div class='steward-label-header'>RUF</div>", unsafe_allow_html=True)
            h3.markdown("<div class='steward-label-header'>BIV</div>", unsafe_allow_html=True)
            h4.markdown("<div class='steward-label-header'>NOM</div>", unsafe_allow_html=True)
            
            df_j = df_tag[df_tag[r_col] == mein_richter].sort_values(['Kategorie', 'Katalog-Nr'])
            
            current_cat = None
            for idx, (_, row) in enumerate(df_j.iterrows()):
                # Kategorie-Trenner
                if row['Kategorie'] != current_cat:
                    current_cat = row['Kategorie']
                    st.markdown(f"<div class='steward-section-header'>Kategorie {current_cat}</div>", unsafe_allow_html=True)
                
                nr = row['KAT_STR']
                k = f"{nr}|{mein_richter}"
                if k not in store.data: store.data[k] = {"Aufruf": False, "BIV": False, "NOM": False}
                
                # Zebra-Look Klasse
                bg_class = "steward-card-alt" if idx % 2 == 0 else ""
                
                st.markdown(f"<div class='steward-card {bg_class}'>", unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                
                c1.markdown(f"<span class='steward-nr'>#{nr}</span><br><span class='steward-info-text'>{get_full_label(row)}</span>", unsafe_allow_html=True)
                store.data[k]["Aufruf"] = c2.checkbox("R", value=store.data[k]["Aufruf"], key=f"a{k}", label_visibility="collapsed")
                store.data[k]["BIV"] = c3.checkbox("B", value=store.data[k]["BIV"], key=f"b{k}", label_visibility="collapsed")
                store.data[k]["NOM"] = c4.checkbox("N", value=store.data[k]["NOM"], key=f"n{k}", label_visibility="collapsed")
                st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.view == "BIS_Grid":
        st.title("Best in Show")
        # Logik analog zum vorherigen Grid, aber mit Kategorie-Trennern aus Excel
        for cat in sorted(df_tag['Kategorie'].unique()):
            st.markdown(f"<div class='steward-section-header'>Kategorie {cat}</div>", unsafe_allow_html=True)
            # ... (Rest des Grid-Codes wie zuvor)
