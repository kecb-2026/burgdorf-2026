import streamlit as st
import pandas as pd
import re
import time

# --- 1. SETUP & STYLING ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

st.markdown("""
    <style>
    /* Animation für blinkende Tags */
    @keyframes blinker { 50% { opacity: 0.1; } }
    
    /* Vollflächiges Gewinner-Overlay */
    .winner-overlay {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: white;
        z-index: 9999999;
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        text-align: center;
        animation: fadeIn 0.8s ease-in-out;
    }
    .ov-header {
        font-size: 55px !important; font-weight: 500; color: #333;
        border-bottom: 2px solid #ccc; width: 80%;
        padding-bottom: 25px; margin-bottom: 50px;
    }
    .ov-cat-name {
        font-size: 90px !important; font-weight: 900;
        text-transform: uppercase; color: #000;
        margin-bottom: 30px; line-height: 1.1;
    }
    .ov-owner {
        font-size: 45px !important; font-style: italic; color: #444;
    }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

    /* Buttons & Standard-Styles */
    .stButton button { width: 100%; height: 50px; font-size: 13px !important; font-weight: bold !important; border-radius: 12px !important; margin-bottom: 5px; border: 2px solid #1a4a9e !important; }
    .judge-header-box { background-color: #1a4a9e; color: white; padding: 8px; border-radius: 10px; text-align: center; font-size: 15px !important; font-weight: bold; margin-bottom: 10px; border: 2px solid #0d2a5e; height: 60px; display: flex; align-items: center; justify-content: center; }
    .class-label-box { background-color: #e9ecef; color: #1a4a9e; padding: 5px; border-radius: 10px; text-align: center; font-size: 14px !important; font-weight: 800; border: 2px solid #1a4a9e; display: flex; align-items: center; justify-content: center; height: 80px; width: 100%; line-height: 1.1; }
    .cat-card, .placeholder-box { padding: 5px; border: 2px solid #1a4a9e; text-align: center; background-color: #ffffff; border-radius: 14px; margin-bottom: 5px; min-height: 80px; display: flex; flex-direction: column; justify-content: center; align-items: center; }
    .placeholder-box { border: 1px solid #d1d1d1; background-color: #f2f2f2 !important; color: #999999; }
    .winner-card { border: 3px solid #ff4d4d !important; background-color: #ffcccc !important; color: #b21f2d !important; }
    .cat-number { font-size: 28px !important; font-weight: 900 !important; color: #1a4a9e; line-height: 1.0; }
    .cat-details { font-size: 14px !important; color: #333; font-weight: bold; margin-top: 2px; line-height: 1.1; }
    .tag-container { margin-top: 4px; display: flex; justify-content: center; flex-wrap: wrap; gap: 3px; }
    .tag { font-weight: bold; padding: 2px 6px; border-radius: 4px; font-size: 10px; text-transform: uppercase; }
    .tag-biv { background-color: #28a745; color: white; animation: blinker 1.5s linear infinite; }
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

if "view" not in st.session_state:
    st.session_state.view = "Home"

# --- 3. HILFSFUNKTIONEN ---
def render_overlay_html(row):
    kat_nr = str(row.get('KATALOG-NR', '')).replace('.0', '')
    rasse = row.get('RASSE', '')
    farbe = row.get('FARBE', '')
    name_gross = str(row.get('NAME', '')).upper()
    besitzer = f"{row.get('BESITZER VORNAME', '')} {row.get('BESITZER NACHNAME', '')}"
    
    return f"""
        <div class="winner-overlay">
            <div class="ov-header">{kat_nr}. {rasse} {farbe}</div>
            <div class="ov-cat-name">{name_gross}</div>
            <div class="ov-owner">{besitzer}</div>
            <div style="margin-top: 80px;">
                <img src="https://upload.wikimedia.org/wikipedia/de/thumb/f/f4/FIFe_logo.svg/500px-FIFe_logo.svg.png" width="130">
                <div style="font-weight: bold; font-size: 28px; color: #1a4a9e; margin-top: 15px;">KECB BURGDORF 2026</div>
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
    st.session_state.view = name
    st.rerun()

# --- 4. VIEWS ---

# HOME
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

# BIS ADMIN CONTROL
elif st.session_state.view == "BIS_Admin_Control":
    st.title("👨‍⚖️ BIS Control Center")
    df_full = load_labels()
    if df_full is not None:
        sel_cat = st.selectbox("Kategorie verwalten:", sorted(df_full['KATEGORIE'].unique()))
        bis_defs = [("Adult Male", [1,3,5,7,9], "M"), ("Adult Female", [1,3,5,7,9], "W"), ("Neuter Male", [2,4,6,8,10], "M"), ("Neuter Female", [2,4,6,8,10], "W"), ("Junior 8-12 Male", [11], "M"), ("Junior 8-12 Female", [11], "W"), ("Kitten 4-8 Male", [12], "M"), ("Kitten 4-8 Female", [12], "W")]
        
        for label, klassen, geschl in bis_defs:
            with st.expander(f"KLASSE: {label}", expanded=True):
                c_ctrl, c_votes = st.columns([1, 1.2])
                with c_ctrl:
                    st.markdown("**Steuerung**")
                    key_reveal = f"reveal_{sel_cat}_{label}"; key_winner_reveal = f"winner_reveal_{sel_cat}_{label}"; key_override = f"override_{sel_cat}_{label}"
                    store.data[key_reveal] = st.checkbox("Nominationen anzeigen", value=store.data.get(key_reveal, False), key=f"cb1_{key_reveal}")
                    store.data[key_winner_reveal] = st.checkbox("BIS Gewinner anzeigen", value=store.data.get(key_winner_reveal, False), key=f"cb2_{key_winner_reveal}")
                    
                    pool = df_full[(df_full['SELECTION'].astype(str).str.upper() == 'X') & (df_full['KATEGORIE'] == sel_cat) & (df_full['KLASSE_INTERNAL'].isin(klassen)) & (df_full['GESCHLECHT'].astype(str).str.upper() == geschl)]
                    options = ["Automatisch (Stimmen)"] + sorted(pool['KAT_STR'].unique().tolist())
                    current_override = store.data.get(key_override, "Automatisch (Stimmen)")
                    idx = options.index(current_override) if current_override in options else 0
                    store.data[key_override] = st.selectbox(f"Gewinner festlegen:", options, index=idx, key=f"sb_{key_override}")
                    
                    manual_winner = store.data.get(key_override, "Automatisch (Stimmen)")
                    final_nr = None
                    if manual_winner != "Automatisch (Stimmen)":
                        final_nr = manual_winner
                    elif "votes" in store.data:
                        v_prefix = f"v_{sel_cat}_{label}_"
                        votes = [v for k, v in store.data["votes"].items() if k.startswith(v_prefix) and v != "Keine Wahl"]
                        if votes:
                            final_nr = pd.Series(votes).value_counts().index[0]
                    
                    if final_nr:
                        w_match = df_full[df_full['KAT_STR'] == str(final_nr)]
                        if not w_match.empty:
                            if st.button(f"🏆 PUBLIC OVERLAY STARTEN (#{final_nr})", key=f"btn_ov_{sel_cat}_{label}"):
                                store.active_overlay = w_match.iloc[0].to_dict()
                                store.overlay_start_time = time.time()
                                st.success(f"Overlay für #{final_nr} wird auf dem Monitor angezeigt!")
                
                with c_votes:
                    st.markdown("**Stimmen-Details**")
                    prefix = f"v_{sel_cat}_{label}_"
                    votes_in_class = {k.replace(prefix, ""): v for k, v in store.data.get("votes", {}).items() if k.startswith(prefix) and v != "Keine Wahl"}
                    if votes_in_class:
                        summary = {}
                        for judge, kat_nr in votes_in_class.items():
                            if kat_nr not in summary: summary[kat_nr] = []
                            summary[kat_nr].append(judge)
                        results_table = [{"Kat": f"#{k}", "Stimmen": len(j), "Richter": ", ".join(j)} for k, j in summary.items()]
                        st.table(pd.DataFrame(results_table).sort_values("Stimmen", ascending=False))
    if st.button("⬅️ Zurück"): set_view("Home")

# BIS PUBLIC VIEW
elif st.session_state.view == "BIS_Public":
    # --- OVERLAY LOGIK (NUR HIER AKTIV) ---
    if hasattr(store, 'active_overlay') and store.active_overlay is not None:
        elapsed = time.time() - store.overlay_start_time
        if elapsed < 30:
            st.markdown(render_overlay_html(store.active_overlay), unsafe_allow_html=True)
            time.sleep(2)
            st.rerun() 
        else:
            store.active_overlay = None 
            st.rerun()

    st.title("🏆 Best in Show")
    df_full = load_labels()
    if df_full is not None:
        tag_input = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"])
        tag = tag_input.upper(); sel_cat = st.selectbox("Kategorie wählen:", sorted(df_full['KATEGORIE'].unique()))
        bis_defs = [("Adult Male", [1,3,5,7,9], "M"), ("Adult Female", [1,3,5,7,9], "W"), ("Neuter Male", [2,4,6,8,10], "M"), ("Neuter Female", [2,4,6,8,10], "W"), ("Junior 8-12 Male", [11], "M"), ("Junior 8-12 Female", [11], "W"), ("Kitten 4-8 Male", [12], "M"), ("Kitten 4-8 Female", [12], "W")]
        r_col = f"RICHTER {tag}"; judges = sorted([r for r in df_full[df_full[tag].astype(str).str.upper() == 'X'][r_col].unique() if str(r) != "nan"])
        
        col_ratios = [1.2] + [1] * len(judges) + [1.2]
        h_cols = st.columns(col_ratios)
        h_cols[0].write("") 
        for i, j in enumerate(judges): 
            h_cols[i+1].markdown(f"<div class='judge-header-box'>{j}</div>", unsafe_allow_html=True)
        h_cols[-1].markdown(f"<div class='judge-header-box' style='background-color:#b21f2d;'>BEST IN SHOW</div>", unsafe_allow_html=True)
        
        for label, klassen, geschl in bis_defs:
            row_cols = st.columns(col_ratios)
            row_cols[0].markdown(f"<div class='class-label-box'>{label}</div>", unsafe_allow_html=True)
            show_noms = store.data.get(f"reveal_{sel_cat}_{label}", False)
            for i, j in enumerate(judges):
                with row_cols[i+1]:
                    if show_noms:
                        match = df_full[(df_full['SELECTION'].astype(str).str.upper() == 'X') & (df_full[r_col] == j) & (df_full['KATEGORIE'] == sel_cat) & (df_full['KLASSE_INTERNAL'].isin(klassen)) & (df_full['GESCHLECHT'].astype(str).str.upper() == geschl)]
                        if not match.empty: 
                            st.markdown(f"<div class='cat-card'><div class='cat-number'>{match.iloc[0]['KAT_STR']}</div><div class='cat-details'>{get_full_label(match.iloc[0])}</div></div>", unsafe_allow_html=True)
                        else: 
                            st.markdown("<div class='placeholder-box'>–</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='placeholder-box'>🔒</div>", unsafe_allow_html=True)
            
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
                            if len(counts) > 0 and (len(counts) == 1 or counts.iloc[0] > counts.iloc[1]): winner_nr = counts.index[0]
                    if winner_nr:
                        m_winner = df_full[df_full['KAT_STR'] == str(winner_nr)]
                        if not m_winner.empty: 
                            st.markdown(f"<div class='cat-card winner-card'><div class='cat-number'>{winner_nr}</div><div class='cat-details'>🏆 BIS<br>{get_full_label(m_winner.iloc[0])}</div></div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='placeholder-box'>Wahl läuft...</div>", unsafe_allow_html=True)
                else: 
                    st.markdown("<div class='placeholder-box'>🔒</div>", unsafe_allow_html=True)
    if st.button("⬅️ Zurück"): set_view("Home")
    time.sleep(3)
    st.rerun()

# LIVE DASHBOARD
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
                                tags_html = "".join([f"<span class='tag tag-{t.replace(' ', '').lower()}'>{t.upper()}</span>" for t, active in v.items() if active])
                                st.markdown(f"<div class='cat-card'><div class='cat-number'>{kat_nr}</div><div class='cat-details'>{get_full_label(row)}</div><div class='tag-container'>{tags_html}</div></div>", unsafe_allow_html=True)
    if st.button("⬅️ Zurück"): set_view("Home")

# STEWARD PANEL
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
                c1, c2, c3, c4 = st.columns([3, 1.2, 1, 1])
                c1.write(f"**#{nr}** {get_full_label(row)}")
                store.data[k]["Zum Richten"] = c2.checkbox("Zum Richten", value=store.data[k]["Zum Richten"], key=f"auf{k}")
                store.data[k]["BIV"] = c3.checkbox("BIV", value=store.data[k]["BIV"], key=f"biv{k}")
                store.data[k]["NOM"] = c4.checkbox("NOM", value=store.data[k]["NOM"], key=f"nom{k}")
    if st.button("⬅️ Zurück"): set_view("Home")

# JUDGE VOTING
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
            bis_defs = [("Adult Male", [1,3,5,7,9], "M"), ("Adult Female", [1,3,5,7,9], "W"), ("Neuter Male", [2,4,6,8,10], "M"), ("Neuter Female", [2,4,6,8,10], "W"), ("Junior 8-12 Male", [11], "M"), ("Junior 8-12 Female", [11], "W"), ("Kitten 4-8 Male", [12], "M"), ("Kitten 4-8 Female", [12], "W")]
            for label, klassen, geschl in bis_defs:
                with st.expander(f"Wahl für {label}"):
                    pool = df_full[(df_full['SELECTION'].astype(str).str.upper() == 'X') & (df_full['KATEGORIE'] == active_cat) & (df_full['KLASSE_INTERNAL'].isin(klassen)) & (df_full['GESCHLECHT'].astype(str).str.upper() == geschl)]
                    if not pool.empty:
                        opts = {f"#{r['KAT_STR']} - {get_full_label(r)}": r['KAT_STR'] for _, r in pool.iterrows()}
                        v_key = f"v_{active_cat}_{label}_{active_j}"
                        curr = store.data["votes"].get(v_key, "Keine Wahl")
                        idx = (list(opts.values()).index(curr) + 1) if curr in opts.values() else 0
                        sel = st.radio("Favorit:", ["Keine Wahl"] + list(opts.keys()), index=idx, key=f"r_{v_key}")
                        store.data["votes"][v_key] = opts[sel] if sel != "Keine Wahl" else "Keine Wahl"
    if st.button("⬅️ Zurück"): set_view("Home")

# LOGINS
elif st.session_state.view == "Steward_Login":
    pwd = st.text_input("Passwort (Steward)", type="password")
    if st.button("Anmelden") and pwd == "steward2026": set_view("Steward_Panel")
    if st.button("⬅️ Zurück"): set_view("Home")

elif st.session_state.view == "Admin_Login":
    pwd = st.text_input("Passwort (Admin)", type="password")
    if st.button("Anmelden") and pwd == "admin2026": set_view("Admin_Panel")
    if st.button("⬅️ Zurück"): set_view("Home")

elif st.session_state.view == "Admin_Panel":
    st.title("⚙️ Admin-Konsole")
    if st.button("ALLE DATEN ZURÜCKSETZEN"):
        store.data = {}
        store.active_overlay = None
        st.success("Speicher geleert!")
    if st.button("⬅️ Zurück"): set_view("Home")
