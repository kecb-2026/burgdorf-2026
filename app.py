import streamlit as st
import pandas as pd
import re
import time  # Neu für den Timer

# --- 1. SETUP & STYLING ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

st.markdown("""
    <style>
    /* ... Dein bestehendes CSS ... */
    @keyframes blinker { 50% { opacity: 0.1; } }
    .stButton button { width: 100%; height: 50px; font-size: 13px !important; font-weight: bold !important; border-radius: 12px !important; margin-bottom: 5px; border: 2px solid #1a4a9e !important; }
    .judge-header-box { background-color: #1a4a9e; color: white; padding: 8px; border-radius: 10px; text-align: center; font-size: 15px !important; font-weight: bold; margin-bottom: 10px; border: 2px solid #0d2a5e; height: 60px; display: flex; align-items: center; justify-content: center; }
    .class-label-box { background-color: #e9ecef; color: #1a4a9e; padding: 5px; border-radius: 10px; text-align: center; font-size: 14px !important; font-weight: 800; border: 2px solid #1a4a9e; display: flex; align-items: center; justify-content: center; height: 80px; width: 100%; line-height: 1.1; }
    .cat-card, .placeholder-box { padding: 5px; border: 2px solid #1a4a9e; text-align: center; background-color: #ffffff; border-radius: 14px; margin-bottom: 5px; min-height: 80px; display: flex; flex-direction: column; justify-content: center; align-items: center; }
    .placeholder-box { border: 1px solid #d1d1d1; background-color: #f2f2f2 !important; color: #999999; }
    .winner-card { border: 3px solid #ff4d4d !important; background-color: #ffcccc !important; color: #b21f2d !important; }
    .cat-number { font-size: 28px !important; font-weight: 900 !important; color: #1a4a9e; line-height: 1.0; }
    .cat-details { font-size: 14px !important; color: #333; font-weight: bold; margin-top: 2px; line-height: 1.1; }
    
    /* NEU: Gewinner Slide Overlay */
    .winner-overlay {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: white; z-index: 9999;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        text-align: center; font-family: sans-serif;
    }
    .win-num-text { font-size: 80px; font-weight: 900; color: #1a4a9e; }
    .win-name-text { font-size: 50px; font-weight: bold; margin: 20px 0; color: #333; text-transform: uppercase; }
    .win-owner-text { font-size: 35px; font-style: italic; color: #666; }
    </style>
    """, unsafe_allow_html=True)

# ... (GlobalStore, load_labels, roman_to_numeric, get_full_label bleiben UNVERÄNDERT) ...
class GlobalStore:
    def __init__(self):
        self.data = {} 

@st.cache_resource
def get_store():
    return GlobalStore()

store = get_store()

if "view" not in st.session_state:
    st.session_state.view = "Home"

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

# HOME (UNVERÄNDERT)
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

# DASHBOARD, STEWARD, VOTING etc. bleiben UNVERÄNDERT...
# (Ich kürze hier ab, damit der Fokus auf den Änderungen liegt)

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
                    
                    # NEU: Button zum Starten des Celebration Slides
                    if store.data[key_winner_reveal]:
                        # Ermittlung der Nummer für den Slide (manuell oder automatisch)
                        slide_nr = None
                        if store.data[key_override] != "Automatisch (Stimmen)":
                            slide_nr = store.data[key_override]
                        else:
                            prefix = f"v_{sel_cat}_{label}_"
                            votes = [v for k, v in store.data.get("votes", {}).items() if k.startswith(prefix) and v != "Keine Wahl"]
                            if votes:
                                counts = pd.Series(votes).value_counts()
                                if len(counts) > 0: slide_nr = counts.index[0]
                        
                        if slide_nr and st.button(f"✨ Slide für #{slide_nr} zeigen", key=f"btn_slide_{sel_cat}_{label}"):
                            store.data["active_celebration"] = slide_nr
                            store.data["celebration_start"] = time.time()
                
                # Stimmen-Details bleiben UNVERÄNDERT...
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
                    else:
                        st.info("Keine Stimmen abgegeben.")
    if st.button("⬅️ Zurück"): set_view("Home")

elif st.session_state.view == "BIS_Public":
    # NEU: Timer & Slide Logik VOR dem Grid-Rendering
    if "active_celebration" in store.data and store.data["active_celebration"]:
        elapsed = time.time() - store.data.get("celebration_start", 0)
        if elapsed < 15: # 15 Sekunden Timer
            df_full = load_labels()
            winner_nr = store.data["active_celebration"]
            m_win = df_full[df_full['KAT_STR'] == str(winner_nr)].iloc[0]
            
            st.markdown(f"""
                <div class="winner-overlay">
                    <div class="win-num-text">#{winner_nr}</div>
                    <div style="font-size: 30px; color: #1a4a9e; font-weight: bold;">{get_full_label(m_win)}</div>
                    <div class="win-name-text">{m_win.get('NAME_DER_KATZE', '')}</div>
                    <div class="win-owner-text">{m_win.get('BESITZER', '')}</div>
                    <div style="margin-top: 50px;">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Logo_FIFE.svg/1200px-Logo_FIFE.svg.png" width="100">
                        <p style="font-weight: bold; color: #1a4a9e;">BEST IN SHOW 2026</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            time.sleep(1)
            st.rerun()
        else:
            store.data["active_celebration"] = None
            st.rerun()

    # RESTLICHE BIS_Public Logik (Grid) bleibt UNVERÄNDERT...
    st.title("🏆 Best in Show")
    df_full = load_labels()
    if df_full is not None:
        tag_input = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"])
        tag = tag_input.upper(); sel_cat = st.selectbox("Kategorie wählen:", sorted(df_full['KATEGORIE'].unique()))
        # ... (restliches Grid Rendering wie im Original)
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
            # Nominationen
            show_noms = store.data.get(f"reveal_{sel_cat}_{label}", False)
            for i, j in enumerate(judges):
                with row_cols[i+1]:
                    if show_noms:
                        match = df_full[(df_full['SELECTION'].astype(str).str.upper() == 'X') & (df_full[r_col] == j) & (df_full['KATEGORIE'] == sel_cat) & (df_full['KLASSE_INTERNAL'].isin(klassen)) & (df_full['GESCHLECHT'].astype(str).str.upper() == geschl)]
                        if not match.empty: st.markdown(f"<div class='cat-card'><div class='cat-number'>{match.iloc[0]['KAT_STR']}</div><div class='cat-details'>{get_full_label(match.iloc[0])}</div></div>", unsafe_allow_html=True)
                        else: st.markdown("<div class='placeholder-box'>–</div>", unsafe_allow_html=True)
                    else: st.markdown("<div class='placeholder-box'>🔒</div>", unsafe_allow_html=True)
            # Gewinner
            with row_cols[-1]:
                if store.data.get(f"winner_reveal_{sel_cat}_{label}", False):
                    manual_winner = store.data.get(f"override_{sel_cat}_{label}", "Automatisch (Stimmen)")
                    winner_nr = None
                    if manual_winner != "Automatisch (Stimmen)": winner_nr = manual_winner
                    elif "votes" in store.data:
                        prefix = f"v_{sel_cat}_{label}_"
                        votes = [v for k, v in store.data["votes"].items() if k.startswith(prefix) and v != "Keine Wahl"]
                        if votes:
                            counts = pd.Series(votes).value_counts()
                            if len(counts) > 0 and (len(counts) == 1 or counts.iloc[0] > counts.iloc[1]): winner_nr = counts.index[0]
                    if winner_nr:
                        m_winner = df_full[df_full['KAT_STR'] == str(winner_nr)]
                        if not m_winner.empty: st.markdown(f"<div class='cat-card winner-card'><div class='cat-number'>{winner_nr}</div><div class='cat-details'>🏆 BIS<br>{get_full_label(m_winner.iloc[0])}</div></div>", unsafe_allow_html=True)
                    else: st.markdown("<div class='placeholder-box'>Wahl läuft...</div>", unsafe_allow_html=True)
                else: st.markdown("<div class='placeholder-box'>🔒</div>", unsafe_allow_html=True)

    if st.button("⬅️ Zurück"): set_view("Home")

# ... (Steward_Panel, Judge_Voting, Admin_Panel bleiben UNVERÄNDERT) ...
