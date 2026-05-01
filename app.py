import streamlit as st
import pandas as pd
import re

# --- 1. SETUP & STYLING ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

st.markdown("""
    <style>
    .stButton button { 
        width: 100%; height: 60px; font-size: 13px !important; 
        font-weight: bold !important; border-radius: 12px !important;
        margin-bottom: 5px; border: 2px solid #1a4a9e !important;
    }
    .judge-col { 
        border: 2px solid #1a4a9e; padding: 5px; border-radius: 15px; 
        background-color: #ffffff; margin-bottom: 8px; 
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        display: flex; flex-direction: column; gap: 5px;
    }
    .judge-col h3 { 
        font-size: 14px !important; color: white; background-color: #1a4a9e; 
        padding: 3px; border-radius: 8px; text-align: center; margin-bottom: 5px;
    }
    .cat-card { 
        padding: 8px; border: 1px solid #e0e0e0; text-align: center; 
        background-color: #ffffff; border-radius: 15px; 
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
        height: auto; min-height: 120px; display: flex; flex-direction: column; justify-content: center; 
    }
    .cat-number { font-size: 32px !important; font-weight: 900 !important; color: #1a4a9e; line-height: 0.9; margin: 2px 0; }
    .cat-details { font-size: 14px; color: #333; font-weight: bold; margin-top: 5px; line-height: 1.2; }
    
    .tag-container { margin-top: 5px; display: flex; justify-content: center; flex-wrap: wrap; gap: 5px; }
    .tag { font-weight: bold; padding: 4px 10px; border-radius: 6px; font-size: 10px; display: inline-block; }
    .tag-aufruf { background-color: #007bff; color: white; }
    @keyframes blinker { 50% { opacity: 0.2; } }
    .tag-biv { background-color: #28a745; color: white; animation: blinker 1.5s linear infinite; }
    .tag-nom { background-color: #ffc107; color: black; animation: blinker 1s linear infinite; }
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
    for rom, num in roman_map.items():
        res = re.sub(rf'\b{rom}\b', num, res)
    return res

@st.cache_data(ttl=30)
def load_labels():
    try:
        df = pd.read_excel("LABELS.xlsx", engine='openpyxl', header=0)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        if 'AUSSTELLUNGSKLASSE' in df.columns:
            df['KLASSE_INTERNAL'] = df['AUSSTELLUNGSKLASSE']
        elif 'KLASSE' in df.columns:
            df['KLASSE_INTERNAL'] = df['KLASSE']
            
        if 'KATALOG-NR' in df.columns:
            df['KAT_STR'] = df['KATALOG-NR'].astype(str).str.replace('.0', '', regex=False)
        return df
    except Exception as e:
        st.error(f"Excel-Fehler: {e}")
        return None

def get_full_label(row):
    r = row.get('RASSE_KURZ', row.get('RASSE', ''))
    g = roman_to_numeric(row.get('FARBGRUPPE', ''))
    e = row.get('FARBE', '')
    label = f"{r} {g}".strip()
    if pd.notna(e) and e != "": label += f" ({e})"
    return label

def set_view(name):
    st.session_state.view = name
    st.rerun()

# --- 4. VIEWS ---

if st.session_state.view == "Home":
    st.title("🐾 KECB Burgdorf 2026")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📢 LIVE-DASHBOARD"): set_view("Dashboard")
        if st.button("🏆 BEST IN SHOW (PUBLIC)"): set_view("BIS_Public")
    with col2:
        if st.button("📝 STEWARD-PULT"): set_view("Steward_Login")
        if st.button("👨‍⚖️ BIS ADMIN / CONTROL"): set_view("BIS_Admin_Control")
        if st.button("⚙️ ADMIN-KONSOLE (RESET)"): set_view("Admin_Login")

elif st.session_state.view == "Steward_Login":
    st.title("🔒 Steward Login")
    pwd = st.text_input("Passwort", type="password")
    if st.button("Anmelden") and pwd == "steward2026": set_view("Steward_Panel")
    if st.button("Zurück"): set_view("Home")

elif st.session_state.view == "Admin_Login":
    st.title("⚙️ Admin Login")
    pwd = st.text_input("Passwort", type="password")
    if st.button("Anmelden") and pwd == "admin2026": set_view("Admin_Panel")
    if st.button("Zurück"): set_view("Home")

elif st.session_state.view == "Admin_Panel":
    st.title("👨‍⚖️ Admin-Konsole")
    with st.expander("🚨 Gefahrenzone: Speicher leeren"):
        if st.button("ALLE DATEN ZURÜCKSETZEN"):
            store.data = {} 
            st.success("Speicher geleert!")
            st.rerun()
    if st.button("⬅️ Zurück zum Menü"): set_view("Home")

else:
    st.sidebar.title("KECB 2026")
    tag_input = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"])
    tag = tag_input.upper()
    if st.sidebar.button("⬅️ Menü"): set_view("Home")
    
    df_full = load_labels()
    r_col = f"RICHTER {tag}"
    
    if df_full is not None and tag in df_full.columns:
        df_tag = df_full[df_full[tag].astype(str).str.upper() == 'X'].copy()
    else:
        df_tag = None

    if st.session_state.view == "Dashboard":
        st.title(f"Live-Aufruf ({tag_input})")
        if df_tag is not None and r_col in df_tag.columns:
            judges = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
            cols = st.columns(max(1, len(judges)))
            for i, j in enumerate(judges):
                with cols[i]:
                    st.markdown(f"<div class='judge-col'><h3>{j}</h3>", unsafe_allow_html=True)
                    for k, v in store.data.items():
                        if "|" in k:
                            nr, r_n = k.split("|")
                            if r_n == j and any(v.values()):
                                m = df_tag[df_tag['KAT_STR'] == nr]
                                if not m.empty:
                                    row = m.iloc[0]
                                    card_html = f"""<div class='cat-card'>
                                        <div style='font-size: 10px; font-weight: bold; color: #ff0000;'>Kat. {row.get('KATEGORIE', '–')}</div>
                                        <div class='cat-number'>{nr}</div>
                                        <div class='cat-details'>{get_full_label(row)}</div>
                                        <div class='tag-container'>"""
                                    if v.get("Aufruf"): card_html += "<span class='tag tag-aufruf'>AUFRUF</span>"
                                    if v.get("BIV"): card_html += "<span class='tag tag-biv'>BIV</span>"
                                    if v.get("NOM"): card_html += "<span class='tag tag-nom'>NOM</span>"
                                    st.markdown(card_html + "</div></div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.view == "Steward_Panel":
        st.title("Steward-Steuerung")
        if df_tag is not None and r_col in df_tag.columns:
            all_j = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
            mein_richter = st.selectbox("Richter wählen:", ["--"] + all_j)
            if mein_richter != "--":
                df_j = df_tag[df_tag[r_col] == mein_richter].sort_values(['KATALOG-NR'])
                for _, row in df_j.iterrows():
                    nr = row['KAT_STR']; k = f"{nr}|{mein_richter}"
                    if k not in store.data: store.data[k] = {"Aufruf": False, "BIV": False, "NOM": False}
                    c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                    c1.write(f"**#{nr}** - {get_full_label(row)}")
                    store.data[k]["Aufruf"] = c2.checkbox("Ruf", value=store.data[k]["Aufruf"], key=f"a{k}")
                    store.data[k]["BIV"] = c3.checkbox("BIV", value=store.data[k]["BIV"], key=f"b{k}")
                    store.data[k]["NOM"] = c4.checkbox("NOM", value=store.data[k]["NOM"], key=f"n{k}")

    elif st.session_state.view == "BIS_Admin_Control":
        st.title("🏆 BIS Steuerung")
        if df_full is not None:
            all_cats = sorted(df_full['KATEGORIE'].unique())
            sel_cat = st.selectbox("Kategorie verwalten:", all_cats, key="admin_cat")
            bis_defs = [
                ("Adult Male", [1, 3, 5, 7, 9], "M"), ("Adult Female", [1, 3, 5, 7, 9], "W"),
                ("Neuter Male", [2, 4, 6, 8, 10], "M"), ("Neuter Female", [2, 4, 6, 8, 10], "W"),
                ("Junior (11) Male", [11], "M"), ("Junior (11) Female", [11], "W"),
                ("Kitten (12) Male", [12], "M"), ("Kitten (12) Female", [12], "W")
            ]
            for label, _, _ in bis_defs:
                key = f"reveal_{sel_cat}_{label}"
                if key not in store.data: store.data[key] = False
                store.data[key] = st.checkbox(f"Sichtbar: {label}", value=store.data[key], key=f"cb_{key}")

    elif st.session_state.view == "BIS_Public":
        if df_full is not None:
            all_cats = sorted(df_full['KATEGORIE'].unique())
            sel_cat = st.selectbox("Kategorie wählen:", all_cats, key="pub_cat")
            st.title(f"🏆 Best in Show - Kategorie {sel_cat}")
            
            required = ['SELECTION', 'KLASSE_INTERNAL', 'GESCHLECHT']
            missing = [c for c in required if c not in df_full.columns]
            
            if not missing:
                # Alle aktiven Richter für diesen TAG ermitteln (damit immer alle Spalten da sind)
                all_active_judges = sorted([r for r in df_full[r_col].unique() if str(r) != "nan"])
                
                df_nom = df_full[(df_full['SELECTION'].astype(str).str.upper() == 'X') & (df_full['KATEGORIE'] == sel_cat)].copy()
                
                h_cols = st.columns([1.5] + [1] * len(all_active_judges))
                h_cols[0].markdown("**Klasse**")
                for i, j in enumerate(all_active_judges):
                    h_cols[i+1].markdown(f"<div style='background-color:#1a4a9e; color:white; padding:5px; border-radius:8px; text-align:center; font-size:10px; font-weight:bold;'>{j}</div>", unsafe_allow_html=True)
                st.divider()

                bis_defs = [
                    ("Adult Male", [1, 3, 5, 7, 9], "M"), ("Adult Female", [1, 3, 5, 7, 9], "W"),
                    ("Neuter Male", [2, 4, 6, 8, 10], "M"), ("Neuter Female", [2, 4, 6, 8, 10], "W"),
                    ("Junior (11) Male", [11], "M"), ("Junior (11) Female", [11], "W"),
                    ("Kitten (12) Male", [12], "M"), ("Kitten (12) Female", [12], "W")
                ]

                for label, klassen, geschlecht in bis_defs:
                    r_cols = st.columns([1.5] + [1] * len(all_active_judges))
                    r_cols[0].markdown(f"<div style='font-size:12px; font-weight:bold; padding-top:15px;'>{label}</div>", unsafe_allow_html=True)
                    
                    is_revealed = store.data.get(f"reveal_{sel_cat}_{label}", False)
                    for i, j in enumerate(all_active_judges):
                        with r_cols[i+1]:
                            if is_revealed:
                                match = df_nom[(df_nom[r_col] == j) & (df_nom['KLASSE_INTERNAL'].isin(klassen)) & (df_nom['GESCHLECHT'].astype(str).str.upper() == geschlecht)]
                                if not match.empty:
                                    for _, row in match.iterrows():
                                        st.markdown(f"""
                                            <div class='cat-card' style='border: 2px solid #1a4a9e;'>
                                                <div class='cat-number'>{row['KAT_STR']}</div>
                                                <div class='cat-details'>{get_full_label(row)}</div>
                                            </div>
                                        """, unsafe_allow_html=True)
                            else:
                                st.markdown("<div style='height:80px; border:1px dashed #ccc; border-radius:10px; margin-bottom:5px; background-color:#f9f9f9;'></div>", unsafe_allow_html=True)
                    st.divider()
            else:
                st.error(f"Fehlende Spalten im Excel: AUSSTELLUNGSKLASSE, SELECTION, GESCHLECHT")
