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
        border: 2px solid #1a4a9e; padding: 10px; border-radius: 15px; 
        background-color: #f8f9fa; margin-bottom: 10px; 
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        min-height: auto; 
    }
    .judge-col h3 { 
        font-size: 16px !important; color: white; background-color: #1a4a9e; 
        padding: 8px; border-radius: 10px; text-align: center; margin-bottom: 15px;
    }
    .cat-card, .placeholder-box { 
        padding: 10px; border: 2px solid #1a4a9e; text-align: center; 
        background-color: #ffffff; border-radius: 18px; 
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 10px;
        min-height: 110px;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
    }
    /* Gewinner-Styling */
    .cat-winner { 
        background-color: #d32f2f !important; 
        border-color: #b71c1c !important;
        color: white !important;
    }
    .cat-winner .cat-number, .cat-winner .cat-details { color: white !important; }

    .placeholder-box { border: 2px dashed #d1d1d1; background-color: #fcfcfc; color: #bbbbbb; box-shadow: none; }
    .cat-number { font-size: 32px !important; font-weight: 900 !important; color: #1a4a9e; line-height: 1.0; margin: 0; }
    .cat-details { font-size: 12px; color: #333; font-weight: bold; margin-top: 4px; }
    
    .tag-container { margin-top: 8px; display: flex; justify-content: center; flex-wrap: wrap; gap: 4px; }
    .tag { font-weight: bold; padding: 3px 8px; border-radius: 5px; font-size: 10px; }
    .tag-aufruf { background-color: #007bff; color: white; }
    @keyframes blinker { 50% { opacity: 0.3; } }
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
    st.title("🏆 BIS Steuerung & Gewinner-Kür")
    df_full = load_labels()
    if df_full is not None:
        sel_cat = st.selectbox("Kategorie verwalten:", sorted(df_full['KATEGORIE'].unique()))
        bis_defs = ["Adult Male", "Adult Female", "Neuter Male", "Neuter Female", "Junior (11) Male", "Junior (11) Female", "Kitten (12) Male", "Kitten (12) Female"]
        
        st.subheader("1. Sichtbarkeit & Gewinner")
        for label in bis_defs:
            with st.expander(f"Klasse: {label}"):
                c1, c2 = st.columns([1, 2])
                key_reveal = f"reveal_{sel_cat}_{label}"
                key_winner = f"winner_{sel_cat}_{label}"
                
                # Sichtbarkeit
                store.data[key_reveal] = c1.checkbox("Anzeigen", value=store.data.get(key_reveal, False), key=f"cb_{key_reveal}")
                
                # Gewinner Auswahl aus allen nominierten Katzen dieser Klasse
                klassen_ids = {"Adult Male": ([1,3,5,7,9], "M"), "Adult Female": ([1,3,5,7,9], "W"), "Neuter Male": ([2,4,6,8,10], "M"), "Neuter Female": ([2,4,6,8,10], "W"), "Junior (11) Male": ([11], "M"), "Junior (11) Female": ([11], "W"), "Kitten (12) Male": ([12], "M"), "Kitten (12) Female": ([12], "W")}
                kl, gs = klassen_ids[label]
                pool = df_full[(df_full['SELECTION'].astype(str).str.upper() == 'X') & (df_full['KATEGORIE'] == sel_cat) & (df_full['KLASSE_INTERNAL'].isin(kl)) & (df_full['GESCHLECHT'].astype(str).str.upper() == gs)]
                
                cat_options = ["-- Kein Gewinner --"] + sorted(pool['KAT_STR'].tolist())
                current_winner = store.data.get(key_winner, "-- Kein Gewinner --")
                winner_idx = cat_options.index(current_winner) if current_winner in cat_options else 0
                
                store.data[key_winner] = c2.selectbox("🏆 GEWINNER:", cat_options, index=winner_idx, key=f"sel_{key_winner}")

        st.divider()
        st.subheader("2. Detaillierte Wahlergebnisse (Stimmen der Richter)")
        if "votes" in store.data:
            for label in bis_defs:
                prefix = f"v_{sel_cat}_{label}_"
                votes_in_class = {k.replace(prefix, ""): v for k, v in store.data["votes"].items() if k.startswith(prefix) and v != "Keine Wahl"}
                if votes_in_class:
                    summary = {}
                    for judge, kat_nr in votes_in_class.items():
                        if kat_nr not in summary: summary[kat_nr] = []
                        summary[kat_nr].append(judge)
                    
                    st.write(f"**Stimmen in {label}:**")
                    res_list = [{"Katze": f"#{k}", "Stimmen": len(v), "Richter": ", ".join(v)} for k, v in summary.items()]
                    st.table(pd.DataFrame(res_list).sort_values("Stimmen", ascending=False))
        else: st.info("Noch keine Voting-Daten vorhanden.")
    if st.button("⬅️ Zurück zum Menü"): set_view("Home")

elif st.session_state.view == "BIS_Public":
    st.title("🏆 Best in Show - Public Screen")
    df_full = load_labels()
    if df_full is not None:
        tag_input = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"])
        tag = tag_input.upper(); sel_cat = st.selectbox("Kategorie wählen:", sorted(df_full['KATEGORIE'].unique()))
        bis_defs = [("Adult Male", [1,3,5,7,9], "M"), ("Adult Female", [1,3,5,7,9], "W"), ("Neuter Male", [2,4,6,8,10], "M"), ("Neuter Female", [2,4,6,8,10], "W"), ("Junior (11) Male", [11], "M"), ("Junior (11) Female", [11], "W"), ("Kitten (12) Male", [12], "M"), ("Kitten (12) Female", [12], "W")]
        r_col = f"RICHTER {tag}"
        judges = sorted([r for r in df_full[df_full[tag].astype(str).str.upper() == 'X'][r_col].unique() if str(r) != "nan"])
        
        for label, klassen, geschl in bis_defs:
            if store.data.get(f"reveal_{sel_cat}_{label}", False):
                st.subheader(label)
                winner_nr = store.data.get(f"winner_{sel_cat}_{label}", "-- Kein Gewinner --")
                cols = st.columns(len(judges) if judges else 1)
                for i, j in enumerate(judges):
                    with cols[i]:
                        st.markdown(f"<div style='text-align:center; font-weight:bold; font-size:12px; margin-bottom:5px;'>{j}</div>", unsafe_allow_html=True)
                        match = df_full[(df_full['SELECTION'].astype(str).str.upper() == 'X') & (df_full[r_col] == j) & (df_full['KATEGORIE'] == sel_cat) & (df_full['KLASSE_INTERNAL'].isin(klassen)) & (df_full['GESCHLECHT'].astype(str).str.upper() == geschl)]
                        if not match.empty:
                            row = match.iloc[0]
                            is_winner = row['KAT_STR'] == winner_nr
                            win_class = "cat-winner" if is_winner else ""
                            st.markdown(f"<div class='cat-card {win_class}'><div class='cat-number'>{row['KAT_STR']}</div><div class='cat-details'>{get_full_label(row)}</div></div>", unsafe_allow_html=True)
                        else: st.markdown("<div class='placeholder-box'>–</div>", unsafe_allow_html=True)
    if st.button("⬅️ Zurück zum Menü"): set_view("Home")

# ... (Dashboard, Steward_Panel, Voting, Logins wie zuvor)
elif st.session_state.view == "Dashboard":
    st.title("📢 Live-Aufruf & Status")
    tag_input = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"])
    tag = tag_input.upper(); df_full = load_labels()
    if df_full is not None:
        r_col = f"RICHTER {tag}"; df_tag = df_full[df_full[tag].astype(str).str.upper() == 'X'].copy()
        judges = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
        cols = st.columns(len(judges) if judges else 1)
        for i, j in enumerate(judges):
            with cols[i]:
                st.markdown(f"<div class='judge-col'><h3>{j}</h3>", unsafe_allow_html=True)
                for k, v in store.data.items():
                    if "|" in k:
                        kat_nr, r_name = k.split("|")
                        if r_name == j and any(v.values()):
                            m = df_tag[df_tag['KAT_STR'] == kat_nr]
                            if not m.empty:
                                row = m.iloc[0]; tags_html = "".join([f"<span class='tag tag-{t.lower()}'>{t}</span>" for t, active in v.items() if active])
                                st.markdown(f"<div class='cat-card'><div class='cat-number'>{kat_nr}</div><div class='cat-details'>{get_full_label(row)}</div><div class='tag-container'>{tags_html}</div></div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
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
                if k not in store.data: store.data[k] = {"Aufruf": False, "BIV": False, "NOM": False}
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                c1.write(f"**#{nr}** {get_full_label(row)}")
                store.data[k]["Aufruf"] = c2.checkbox("Ruf", value=store.data[k]["Aufruf"], key=f"auf{k}")
                store.data[k]["BIV"] = c3.checkbox("BIV", value=store.data[k]["BIV"], key=f"biv{k}")
                store.data[k]["NOM"] = c4.checkbox("NOM", value=store.data[k]["NOM"], key=f"nom{k}")
    if st.button("⬅️ Zurück zum Menü"): set_view("Home")

elif st.session_state.view == "Judge_Voting":
    st.title("🗳️ Richter Abstimmung")
    df_full = load_labels()
    if df_full is not None:
        tag_input = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"])
        r_col = f"RICHTER {tag_input.upper()}"; all_judges = sorted([r for r in df_full[r_col].unique() if str(r) != "nan"])
        c1, c2 = st.columns(2)
        with c1: active_j = st.selectbox("Identität:", ["--"] + all_judges)
        with c2: active_cat = st.selectbox("Kategorie:", sorted(df_full['KATEGORIE'].unique()))
        if active_j != "--":
            if "votes" not in store.data: store.data["votes"] = {}
            bis_defs = [("Adult Male", [1,3,5,7,9], "M"), ("Adult Female", [1,3,5,7,9], "W"), ("Neuter Male", [2,4,6,8,10], "M"), ("Neuter Female", [2,4,6,8,10], "W"), ("Junior (11) Male", [11], "M"), ("Junior (11) Female", [11], "W"), ("Kitten (12) Male", [12], "M"), ("Kitten (12) Female", [12], "W")]
            for label, klassen, geschl in bis_defs:
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
                    else: st.info("Keine Nominierten.")
    if st.button("⬅️ Zurück zum Menü"): set_view("Home")

elif st.session_state.view == "Steward_Login":
    st.title("🔒 Steward Login"); pwd = st.text_input("Passwort", type="password")
    if st.button("Anmelden") and pwd == "steward2026": set_view("Steward_Panel")
    if st.button("⬅️ Zurück zum Menü"): set_view("Home")

elif st.session_state.view == "Admin_Login":
    st.title("⚙️ Admin Login"); pwd = st.text_input("Passwort", type="password")
    if st.button("Anmelden") and pwd == "admin2026": set_view("Admin_Panel")
    if st.button("⬅️ Zurück zum Menü"): set_view("Home")

elif st.session_state.view == "Admin_Panel":
    st.title("👨‍⚖️ Admin-Konsole")
    if st.button("ALLE DATEN ZURÜCKSETZEN"): store.data = {}; st.success("Speicher geleert!")
    if st.button("⬅️ Zurück zum Menü"): set_view("Home")
