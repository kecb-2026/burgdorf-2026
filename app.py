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
        padding: 10px; border: 2px solid #1a4a9e; text-align: center; 
        background-color: #ffffff; border-radius: 18px; 
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        min-height: 110px; display: flex; flex-direction: column; justify-content: center;
        margin-bottom: 10px;
    }
    .cat-number { font-size: 34px !important; font-weight: 900 !important; color: #1a4a9e; line-height: 1.0; margin: 0; }
    .cat-details { font-size: 13px; color: #333; font-weight: bold; margin-top: 4px; line-height: 1.2; }
    
    .placeholder-box {
        min-height: 110px; border: 2px dashed #d1d1d1; border-radius: 18px; 
        background-color: rgba(255,255,255,0.3);
        display: flex; align-items: center; justify-content: center;
        color: #bbbbbb; font-size: 11px; font-weight: bold; margin-bottom: 10px;
    }

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
        if st.button("🗳️ RICHTER-VOTING"): set_view("Judge_Voting")
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

elif st.session_state.view == "Judge_Voting":
    st.title("🗳️ Richter Abstimmung")
    df_full = load_labels()
    if df_full is not None:
        tag_input = st.sidebar.radio("Tag für Voting:", ["Tag 1", "Tag 2"])
        r_col = f"RICHTER {tag_input.upper()}"
        all_judges = sorted([r for r in df_full[r_col].unique() if str(r) != "nan"])
        
        c1, c2 = st.columns(2)
        with c1: active_j = st.selectbox("Ihre Identität:", ["--"] + all_judges)
        with c2: active_cat = st.selectbox("Kategorie:", sorted(df_full['KATEGORIE'].unique()))
        
        if active_j != "--":
            if "votes" not in store.data: store.data["votes"] = {}
            bis_defs = [
                ("Adult Male", [1, 3, 5, 7, 9], "M"), ("Adult Female", [1, 3, 5, 7, 9], "W"),
                ("Neuter Male", [2, 4, 6, 8, 10], "M"), ("Neuter Female", [2, 4, 6, 8, 10], "W"),
                ("Junior (11) Male", [11], "M"), ("Junior (11) Female", [11], "W"),
                ("Kitten (12) Male", [12], "M"), ("Kitten (12) Female", [12], "W")
            ]
            for label, klassen, geschlecht in bis_defs:
                with st.expander(f"Wahl: {label}", expanded=True):
                    pool = df_full[(df_full['SELECTION'].astype(str).str.upper() == 'X') & 
                                   (df_full['KATEGORIE'] == active_cat) &
                                   (df_full['KLASSE_INTERNAL'].isin(klassen)) &
                                   (df_full['GESCHLECHT'].astype(str).str.upper() == geschlecht)]
                    if not pool.empty:
                        opts = {f"#{r['KAT_STR']} - {get_full_label(r)}": r['KAT_STR'] for _, r in pool.iterrows()}
                        v_key = f"v_{active_cat}_{label}_{active_j}"
                        curr = store.data["votes"].get(v_key, "Keine Wahl")
                        sel = st.radio("Favorit:", ["Keine Wahl"] + list(opts.keys()), 
                                       index=0 if curr == "Keine Wahl" else list(opts.values()).index(curr) + 1, key=f"r_{v_key}")
                        store.data["votes"][v_key] = opts[sel] if sel != "Keine Wahl" else "Keine Wahl"
                    else: st.info("Keine Nominierten.")
    if st.button("⬅️ Menü"): set_view("Home")

elif st.session_state.view == "Dashboard":
    st.title("Live-Aufruf")
    # ... (bestehender Dashboard-Code)

elif st.session_state.view == "BIS_Admin_Control":
    st.title("🏆 BIS Steuerung & Auszählung")
    df_full = load_labels()
    if df_full is not None:
        sel_cat = st.selectbox("Kategorie verwalten:", sorted(df_full['KATEGORIE'].unique()))
        
        st.subheader("1. Sichtbarkeit (Public Screen)")
        bis_defs = [("Adult Male", [1, 3, 5, 7, 9], "M"), ("Adult Female", [1, 3, 5, 7, 9], "W"),
                    ("Neuter Male", [2, 4, 6, 8, 10], "M"), ("Neuter Female", [2, 4, 6, 8, 10], "W"),
                    ("Junior (11) Male", [11], "M"), ("Junior (11) Female", [11], "W"),
                    ("Kitten (12) Male", [12], "M"), ("Kitten (12) Female", [12], "W")]
        
        cols = st.columns(4)
        for idx, (label, _, _) in enumerate(bis_defs):
            key = f"reveal_{sel_cat}_{label}"
            if key not in store.data: store.data[key] = False
            store.data[key] = cols[idx % 4].checkbox(label, value=store.data[key], key=f"cb_{key}")

        st.divider()
        st.subheader("2. Wahlergebnisse")
        if "votes" in store.data:
            for label, _, _ in bis_defs:
                v_list = [v for k, v in store.data["votes"].items() if k.startswith(f"v_{sel_cat}_{label}_") and v != "Keine Wahl"]
                if v_list:
                    st.write(f"**Ergebnis {label}:**")
                    counts = pd.Series(v_list).value_counts()
                    st.dataframe(counts.rename("Stimmen"), use_container_width=True)
                else: st.caption(f"Keine Stimmen für {label}")
    if st.button("⬅️ Menü"): set_view("Home")

elif st.session_state.view == "BIS_Public":
    # ... (bestehender BIS_Public Code)
    st.title("🏆 Best in Show")
    # (Rest wie zuvor)
    if st.button("⬅️ Menü"): set_view("Home")
