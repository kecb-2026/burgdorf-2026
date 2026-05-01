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
    .judge-header-box {
        background-color: #1a4a9e; color: white; padding: 12px; border-radius: 12px;
        text-align: center; font-size: 16px !important; font-weight: bold;
        margin-bottom: 15px; border: 2px solid #0d2a5e; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    .class-label-box {
        background-color: #e9ecef; color: #1a4a9e; padding: 10px; border-radius: 12px;
        text-align: center; font-size: 16px !important; font-weight: 800;
        border: 2px solid #1a4a9e; display: flex; align-items: center; justify-content: center;
        height: 105px; width: 100%;
    }
    .cat-card, .placeholder-box { 
        padding: 10px; border: 2px solid #1a4a9e; text-align: center; 
        background-color: #ffffff; border-radius: 18px; 
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1); margin-bottom: 10px;
        min-height: 105px; display: flex; flex-direction: column;
        justify-content: center; align-items: center;
    }
    .placeholder-box {
        border: 2px dashed #d1d1d1; background-color: #fcfcfc; color: #bbbbbb; box-shadow: none;
    }
    .winner-card {
        border: 4px solid #b21f2d !important; background-color: #dc3545 !important; color: white !important;
    }
    .winner-card .cat-number, .winner-card .cat-details { color: white !important; }
    .cat-number { font-size: 32px !important; font-weight: 900 !important; color: #1a4a9e; line-height: 1.0; margin: 0; }
    .cat-details { font-size: 12px; color: #333; font-weight: bold; margin-top: 4px; }
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

@st.cache_data(ttl=10)
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
    st.session_state.view = name
    st.rerun()

# Definitionen für BIS-Klassen
BIS_DEFS = [
    ("Adult Male", [1,3,5,7,9], "M"), ("Adult Female", [1,3,5,7,9], "W"), 
    ("Neuter Male", [2,4,6,8,10], "M"), ("Neuter Female", [2,4,6,8,10], "W"), 
    ("Junior 8-12 Male", [11], "M"), ("Junior 8-12 Female", [11], "W"), 
    ("Kitten 4-8 Male", [12], "M"), ("Kitten 4-8 Female", [12], "W")
]

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

elif st.session_state.view == "BIS_Admin_Control":
    st.title("🏆 BIS Steuerung & Manuelle Wahl")
    df_full = load_labels()
    if df_full is not None:
        sel_cat = st.selectbox("Kategorie verwalten:", sorted(df_full['KATEGORIE'].unique()))
        
        st.subheader("Sichtbarkeit, Stimmen & Manueller Eingriff")
        for label, klassen, geschl in BIS_DEFS:
            with st.expander(f"Klasse: {label}"):
                c1, c2, c3, c4 = st.columns([1, 1, 1.5, 2])
                
                # Stimmen zählen für die Anzeige im Admin
                prefix = f"v_{sel_cat}_{label}_"
                class_votes = [v for k, v in store.data.get("votes", {}).items() if k.startswith(prefix) and v != "Keine Wahl"]
                vote_summary = pd.Series(class_votes).value_counts().to_dict() if class_votes else {}
                vote_str = " | ".join([f"#{k}: {v} St." for k, v in vote_summary.items()]) if vote_summary else "Keine Stimmen"
                
                # 1. & 2. Sichtbarkeit
                key_reveal = f"reveal_{sel_cat}_{label}"
                key_winner_reveal = f"winner_reveal_{sel_cat}_{label}"
                store.data[key_reveal] = c1.checkbox("Einblenden", value=store.data.get(key_reveal, False), key=f"vis_{key_reveal}")
                store.data[key_winner_reveal] = c2.checkbox("🏆 Gewinner", value=store.data.get(key_winner_reveal, False), key=f"win_{key_winner_reveal}")
                
                # 3. Stimmen Anzeige
                c3.info(f"🗳️ {vote_str}")
                
                # 4. Manueller Override (Gefiltert auf Katzen dieser Klasse)
                pool = df_full[(df_full['SELECTION'].astype(str).str.upper() == 'X') & (df_full['KATEGORIE'] == sel_cat) & (df_full['KLASSE_INTERNAL'].isin(klassen)) & (df_full['GESCHLECHT'].astype(str).str.upper() == geschl)]
                options = ["Automatisch (Stimmen)"] + sorted(pool['KAT_STR'].unique().tolist())
                
                key_override = f"override_{sel_cat}_{label}"
                current_override = store.data.get(key_override, "Automatisch (Stimmen)")
                idx = options.index(current_override) if current_override in options else 0
                store.data[key_override] = c4.selectbox("Wähle Gewinner (Override):", options, index=idx, key=f"sb_{key_override}")
        
    if st.button("⬅️ Zurück zum Menü"): set_view("Home")

elif st.session_state.view == "BIS_Public":
    st.title("🏆 Best in Show - Public Screen")
    df_full = load_labels()
    if df_full is not None:
        tag_input = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"])
        tag = tag_input.upper()
        sel_cat = st.selectbox("Kategorie wählen:", sorted(df_full['KATEGORIE'].unique()))
        
        r_col = f"RICHTER {tag}"
        judges = sorted([r for r in df_full[df_full[tag].astype(str).str.upper() == 'X'][r_col].unique() if str(r) != "nan"])
        
        h_cols = st.columns([1.5] + [1] * len(judges) + [1.2])
        h_cols[0].write("")
        for i, j in enumerate(judges):
            h_cols[i+1].markdown(f"<div class='judge-header-box'>{j}</div>", unsafe_allow_html=True)
        h_cols[-1].markdown(f"<div class='judge-header-box' style='background-color:#dc3545;'>WINNER</div>", unsafe_allow_html=True)

        for label, klassen, geschl in BIS_DEFS:
            if store.data.get(f"reveal_{sel_cat}_{label}", False):
                row_cols = st.columns([1.5] + [1] * len(judges) + [1.2])
                row_cols[0].markdown(f"<div class='class-label-box'>{label}</div>", unsafe_allow_html=True)
                
                for i, j in enumerate(judges):
                    with row_cols[i+1]:
                        match = df_full[(df_full['SELECTION'].astype(str).str.upper() == 'X') & (df_full[r_col] == j) & (df_full['KATEGORIE'] == sel_cat) & (df_full['KLASSE_INTERNAL'].isin(klassen)) & (df_full['GESCHLECHT'].astype(str).str.upper() == geschl)]
                        if not match.empty:
                            row = match.iloc[0]
                            st.markdown(f"<div class='cat-card'><div class='cat-number'>{row['KAT_STR']}</div><div class='cat-details'>{get_full_label(row)}</div></div>", unsafe_allow_html=True)
                        else: st.markdown("<div class='placeholder-box'>–</div>", unsafe_allow_html=True)
                
                with row_cols[-1]:
                    if store.data.get(f"winner_reveal_{sel_cat}_{label}", False):
                        manual_winner = store.data.get(f"override_{sel_cat}_{label}", "Automatisch (Stimmen)")
                        winner_nr = None
                        
                        if manual_winner != "Automatisch (Stimmen)":
                            winner_nr = manual_winner
                        elif "votes" in store.data:
                            prefix = f"v_{sel_cat}_{label}_"
                            votes = [v for k, v in store.data["votes"].items() if k.startswith(prefix) and v != "Keine Wahl"]
                            if votes:
                                counts = pd.Series(votes).value_counts()
                                if len(counts) > 0 and (len(counts) == 1 or counts.iloc[0] > counts.iloc[1]):
                                    winner_nr = counts.index[0]
                                else:
                                    st.markdown("<div class='placeholder-box' style='border: 2px solid #dc3545; color: #dc3545;'><b>TIE</b><br>Manual Pick</div>", unsafe_allow_html=True)
                        
                        if winner_nr:
                            m_winner = df_full[df_full['KAT_STR'] == str(winner_nr)]
                            if not m_winner.empty:
                                w_row = m_winner.iloc[0]
                                st.markdown(f"<div class='cat-card winner-card'><div class='cat-number'>{winner_nr}</div><div class='cat-details'><b>🏆 WINNER</b><br>{get_full_label(w_row)}</div></div>", unsafe_allow_html=True)
                    else: st.markdown("<div class='placeholder-box' style='background-color:#eee;'>🔒</div>", unsafe_allow_html=True)
                st.divider()
    if st.button("⬅️ Zurück zum Menü"): set_view("Home")

# Rest des Codes bleibt gleich (Dashboard, Steward, Voting, Admin_Login) ...
elif st.session_state.view == "Dashboard":
    st.title("📢 Live-Aufruf & Status")
    tag_input = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"])
    tag = tag_input.upper()
    df_full = load_labels()
    if df_full is not None:
        r_col = f"RICHTER {tag}"
        df_tag = df_full[df_full[tag].astype(str).str.upper() == 'X'].copy()
        judges = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
        cols = st.columns(len(judges) if judges else 1)
        for i, j in enumerate(judges):
            with cols[i]:
                st.markdown(f"<div class='judge-header-box'>{j}</div>", unsafe_allow_html=True)
                for k, v in store.data.items():
                    if "|" in k:
                        kat_nr, r_name = k.split("|")
                        if r_name == j and any(v.values()):
                            m = df_tag[df_tag['KAT_STR'] == kat_nr]
                            if not m.empty:
                                row = m.iloc[0]
                                st.markdown(f"<div class='cat-card'><div class='cat-number'>{kat_nr}</div><div class='cat-details'>{get_full_label(row)}</div></div>", unsafe_allow_html=True)
    if st.button("⬅️ Zurück zum Menü"): set_view("Home")

elif st.session_state.view == "Judge_Voting":
    st.title("🗳️ Richter Abstimmung")
    df_full = load_labels()
    if df_full is not None:
        tag_input = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"])
        r_col = f"RICHTER {tag_input.upper()}"
        all_judges = sorted([r for r in df_full[r_col].unique() if str(r) != "nan"])
        c1, c2 = st.columns(2)
        with c1: active_j = st.selectbox("Identität:", ["--"] + all_judges)
        with c2: active_cat = st.selectbox("Kategorie:", sorted(df_full['KATEGORIE'].unique()))
        if active_j != "--":
            if "votes" not in store.data: store.data["votes"] = {}
            for label, klassen, geschl in BIS_DEFS:
                with st.expander(f"Wahl für {label}"):
                    pool = df_full[(df_full['SELECTION'].astype(str).str.upper() == 'X') & (df_full['KATEGORIE'] == active_cat) & (df_full['KLASSE_INTERNAL'].isin(klassen)) & (df_full['GESCHLECHT'].astype(str).str.upper() == geschl)]
                    if not pool.empty:
                        opts = {f"#{r['KAT_STR']} - {get_full_label(r)}": r['KAT_STR'] for _, r in pool.iterrows()}
                        v_key = f"v_{active_cat}_{label}_{active_j}"
                        curr = store.data["votes"].get(v_key, "Keine Wahl")
                        idx = 0
                        if curr in opts.values(): idx = list(opts.values()).index(curr) + 1
                        sel = st.radio("Favorit:", ["Keine Wahl"] + list(opts.keys()), index=idx, key=f"r_{v_key}")
                        store.data["votes"][v_key] = opts[sel] if sel != "Keine Wahl" else "Keine Wahl"
    if st.button("⬅️ Zurück zum Menü"): set_view("Home")

elif st.session_state.view == "Steward_Login":
    st.title("🔒 Steward Login")
    pwd = st.text_input("Passwort", type="password")
    if st.button("Anmelden") and pwd == "steward2026": set_view("Steward_Panel")
    if st.button("⬅️ Zurück zum Menü"): set_view("Home")

elif st.session_state.view == "Steward_Panel":
    st.title("📝 Steward-Pult")
    tag_input = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"])
    df_full = load_labels()
    if df_full is not None:
        tag = tag_input.upper(); r_col = f"RICHTER {tag}"
        all_j = sorted([r for r in df_full[df_full[tag].astype(str).str.upper() == 'X'][r_col].unique() if str(r) != "nan"])
        mein_richter = st.selectbox("Richter wählen:", ["--"] + all_j)
        if mein_richter != "--":
            df_j = df_full[(df_full[tag].astype(str).str.upper() == 'X') & (df_full[r_col] == mein_richter)].sort_values('KATALOG-NR')
            for _, row in df_j.iterrows():
                nr = row['KAT_STR']; k = f"{nr}|{mein_richter}"
                if k not in store.data: store.data[k] = {"Zum Richten": False, "BIV": False, "NOM": False}
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                c1.write(f"**#{nr}** {get_full_label(row)}")
                store.data[k]["Zum Richten"] = c2.checkbox("Ruf", value=store.data[k]["Zum Richten"], key=f"auf{k}")
                store.data[k]["BIV"] = c3.checkbox("BIV", value=store.data[k]["BIV"], key=f"biv{k}")
                store.data[k]["NOM"] = c4.checkbox("NOM", value=store.data[k]["NOM"], key=f"nom{k}")
    if st.button("⬅️ Zurück zum Menü"): set_view("Home")

elif st.session_state.view == "Admin_Login":
    st.title("⚙️ Admin Login")
    pwd = st.text_input("Passwort", type="password")
    if st.button("Anmelden") and pwd == "admin2026": set_view("Admin_Panel")
    if st.button("⬅️ Zurück zum Menü"): set_view("Home")

elif st.session_state.view == "Admin_Panel":
    st.title("👨‍⚖️ Admin-Konsole")
    if st.button("ALLE DATEN ZURÜCKSETZEN"):
        store.data = {}
        st.success("Speicher geleert!")
    if st.button("⬅️ Zurück zum Menü"): set_view("Home")
