import streamlit as st
import pandas as pd
import re
import time

# --- 1. SETUP & STYLING ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

st.markdown("""
    <style>
    @keyframes blinker { 50% { opacity: 0.1; } }
    
    .stButton button { 
        width: 100%; height: 50px; font-weight: bold !important; border-radius: 12px !important;
        border: 2px solid #1a4a9e !important;
    }
    
    .judge-header-box {
        background-color: #1a4a9e; color: white; padding: 8px; border-radius: 10px;
        text-align: center; font-size: 15px !important; font-weight: bold;
        height: 60px; display: flex; align-items: center; justify-content: center;
    }
    
    .class-label-box {
        background-color: #e9ecef; color: #1a4a9e; border-radius: 10px;
        text-align: center; font-size: 14px !important; font-weight: 800;
        border: 2px solid #1a4a9e; display: flex; align-items: center; justify-content: center;
        height: 85px; width: 100%;
    }
    
    .cat-card, .placeholder-box { 
        padding: 5px; border: 2px solid #1a4a9e; text-align: center; 
        background-color: #ffffff; border-radius: 14px; min-height: 85px;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
    }
    
    .placeholder-box { border: 1px solid #d1d1d1; background-color: #f2f2f2; color: #999; }
    .winner-card { border: 3px solid #ff4d4d !important; background-color: #ffcccc !important; }
    
    .cat-number { font-size: 28px !important; font-weight: 900 !important; color: #1a4a9e; line-height: 1.0; }
    .cat-details { font-size: 13px !important; color: #333; font-weight: bold; line-height: 1.1; }
    
    /* Stimmen-Balken */
    .vote-bar-container {
        width: 80%; height: 6px; background-color: rgba(0,0,0,0.1); 
        border-radius: 3px; margin-top: 4px; overflow: hidden;
    }
    .vote-bar-fill { height: 100%; background-color: #ff4d4d; }

    /* Celebration Overlay */
    .winner-overlay {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: white; z-index: 9999;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        text-align: center;
    }
    
    .tag-biv { background-color: #28a745; color: white; animation: blinker 1.5s linear infinite; padding: 2px 5px; border-radius: 4px; font-size: 10px;}
    .tag-nom { background-color: #ffc107; color: black; animation: blinker 1s linear infinite; padding: 2px 5px; border-radius: 4px; font-size: 10px;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. GLOBALER SPEICHER ---
@st.cache_resource
def get_store(): return {"data": {}, "votes": {}}
store = get_store()

if "view" not in st.session_state: st.session_state.view = "Home"

# --- 3. HILFSFUNKTIONEN ---
def load_labels():
    try:
        df = pd.read_excel("LABELS.xlsx", engine='openpyxl')
        df.columns = [str(c).strip().upper() for c in df.columns]
        df['KLASSE_INTERNAL'] = df['AUSSTELLUNGSKLASSE'] if 'AUSSTELLUNGSKLASSE' in df.columns else df.get('KLASSE', '')
        df['KAT_STR'] = df['KATALOG-NR'].astype(str).str.replace('.0', '', regex=False)
        return df
    except: return None

def get_full_label(row):
    return f"{row.get('RASSE_KURZ','')} {row.get('FARBGRUPPE','')} ({row.get('FARBE','')})".strip()

# --- 4. VIEWS ---

if st.session_state.view == "Home":
    st.title("🐾 KECB Burgdorf 2026")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📢 LIVE-DASHBOARD"): st.session_state.view = "Dashboard"; st.rerun()
        if st.button("🏆 BEST IN SHOW (PUBLIC)"): st.session_state.view = "BIS_Public"; st.rerun()
    with c2:
        if st.button("📝 STEWARD-PULT"): st.session_state.view = "Steward_Login"; st.rerun()
        if st.button("👨‍⚖️ BIS ADMIN CONTROL"): st.session_state.view = "BIS_Admin_Control"; st.rerun()

elif st.session_state.view == "BIS_Admin_Control":
    st.title("👨‍⚖️ BIS Control Center")
    df = load_labels()
    if df is not None:
        sel_cat = st.selectbox("Kategorie:", sorted(df['KATEGORIE'].unique()))
        bis_defs = [("Adult Male", [1,3,5,7,9], "M"), ("Adult Female", [1,3,5,7,9], "W"), ("Neuter Male", [2,4,6,8,10], "M"), ("Neuter Female", [2,4,6,8,10], "W"), ("Junior 8-12 Male", [11], "M"), ("Junior 8-12 Female", [11], "W"), ("Kitten 4-8 Male", [12], "M"), ("Kitten 4-8 Female", [12], "W")]
        
        for label, klassen, geschl in bis_defs:
            with st.expander(f"KLASSE: {label}", expanded=True):
                c_ctrl, c_votes = st.columns([1, 1])
                key_reveal = f"reveal_{sel_cat}_{label}"
                key_winner_reveal = f"winner_reveal_{sel_cat}_{label}"
                
                with c_ctrl:
                    store["data"][key_reveal] = st.checkbox("Noms anzeigen", value=store["data"].get(key_reveal, False), key=f"cb_{key_reveal}")
                    store["data"][key_winner_reveal] = st.checkbox("Winner anzeigen", value=store["data"].get(key_winner_reveal, False), key=f"cbw_{key_winner_reveal}")
                    
                    # Stimmen auswerten für den Slide-Button
                    prefix = f"v_{sel_cat}_{label}_"
                    current_votes = [v for k, v in store["votes"].items() if k.startswith(prefix) and v != "Keine Wahl"]
                    if current_votes:
                        top_cat = pd.Series(current_votes).index.tolist()[0]
                        if st.button(f"✨ #{top_cat} ZELEBRIEREN (SLIDE)", key=f"btn_{label}"):
                            store["data"]["active_slide"] = top_cat
                            store["data"]["slide_start"] = time.time()
                            st.success(f"Slide für #{top_cat} aktiviert!")

    if st.button("⬅️ Zurück"): st.session_state.view = "Home"; st.rerun()

elif st.session_state.view == "BIS_Public":
    # TIMER LOGIK
    if "active_slide" in store["data"] and store["data"]["active_slide"]:
        elapsed = time.time() - store["data"].get("slide_start", 0)
        if elapsed > 15: # 15 Sekunden Timer
            store["data"]["active_slide"] = None
            st.rerun()
        
        # CELEBRATION OVERLAY (Wie auf deinem Foto)
        df_all = load_labels()
        winner_data = df_all[df_all['KAT_STR'] == str(store["data"]["active_slide"])].iloc[0]
        st.markdown(f"""
            <div class="winner-overlay">
                <div style="font-size: 50px; font-weight: bold; color: #333;">{winner_data['KAT_STR']}. {get_full_label(winner_data)}</div>
                <div style="font-size: 70px; font-weight: 900; color: #1a4a9e; margin: 30px 0; text-transform: uppercase;">{winner_data.get('NAME_DER_KATZE', 'WORLD WINNER')}</div>
                <div style="font-size: 40px; font-style: italic; color: #666;">{winner_data.get('BESITZER', 'Aussteller')}</div>
                <div style="margin-top: 50px;">
                     <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Logo_FIFE.svg/1200px-Logo_FIFE.svg.png" width="120">
                     <div style="font-size: 35px; font-weight: bold; color: #1a4a9e; margin-top: 20px;">KECB BURGDORF 2026</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(1)
        st.rerun() # Refresh für den Timer

    else:
        # NORMALES GRID
        st.title("🏆 Best in Show")
        df_full = load_labels()
        if df_full is not None:
            sel_cat = st.selectbox("Kategorie wählen:", sorted(df_full['KATEGORIE'].unique()))
            bis_defs = [("Adult Male", [1,3,5,7,9], "M"), ("Adult Female", [1,3,5,7,9], "W"), ("Neuter Male", [2,4,6,8,10], "M"), ("Neuter Female", [2,4,6,8,10], "W"), ("Junior 8-12", [11], "M"), ("Kitten 4-8", [12], "M")]
            
            tag = "TAG 1" # Beispielhaft
            r_col = f"RICHTER {tag}"
            judges = sorted([r for r in df_full[df_full[tag].astype(str).str.upper() == 'X'][r_col].unique() if str(r) != "nan"])
            
            cols = st.columns([1.2] + [1]*len(judges) + [1.2])
            cols[0].write("")
            for i, j in enumerate(judges): cols[i+1].markdown(f"<div class='judge-header-box'>{j}</div>", unsafe_allow_html=True)
            cols[-1].markdown(f"<div class='judge-header-box' style='background-color:#b21f2d;'>BEST IN SHOW</div>", unsafe_allow_html=True)
            
            for label, klassen, geschl in bis_defs:
                row_cols = st.columns([1.2] + [1]*len(judges) + [1.2])
                row_cols[0].markdown(f"<div class='class-label-box'>{label}</div>", unsafe_allow_html=True)
                
                # Noms
                reveal = store["data"].get(f"reveal_{sel_cat}_{label}", False)
                for i, j in enumerate(judges):
                    with row_cols[i+1]:
                        if reveal:
                            m = df_full[(df_full['SELECTION'] == 'X') & (df_full[r_col] == j) & (df_full['KATEGORIE'] == sel_cat) & (df_full['KLASSE_INTERNAL'].isin(klassen))]
                            if not m.empty:
                                st.markdown(f"<div class='cat-card'><div class='cat-number'>{m.iloc[0]['KAT_STR']}</div></div>", unsafe_allow_html=True)
                            else: st.markdown("<div class='placeholder-box'>–</div>", unsafe_allow_html=True)
                        else: st.markdown("<div class='placeholder-box'>🔒</div>", unsafe_allow_html=True)
                
                # BIS Winner mit Balken
                with row_cols[-1]:
                    if store["data"].get(f"winner_reveal_{sel_cat}_{label}", False):
                        prefix = f"v_{sel_cat}_{label}_"
                        v_list = [v for k, v in store["votes"].items() if k.startswith(prefix) and v != "Keine Wahl"]
                        if v_list:
                            counts = pd.Series(v_list).value_counts()
                            win_nr = counts.index[0]
                            perc = (counts.iloc[0] / len(judges)) * 100
                            st.markdown(f"""
                                <div class='cat-card winner-card'>
                                    <div class='cat-number'>{win_nr}</div>
                                    <div class='vote-bar-container'><div class='vote-bar-fill' style='width:{perc}%'></div></div>
                                </div>
                            """, unsafe_allow_html=True)
                        else: st.markdown("<div class='placeholder-box'>Wahl...</div>", unsafe_allow_html=True)
                    else: st.markdown("<div class='placeholder-box'>🔒</div>", unsafe_allow_html=True)

    if st.button("⬅️ Zurück"): st.session_state.view = "Home"; st.rerun()

# --- Restliche Views (Steward, Login etc.) wie vorher ---
elif st.session_state.view == "Steward_Login":
    pwd = st.text_input("Passwort", type="password")
    if st.button("Login"):
        if pwd == "steward2026": st.session_state.view = "Home"; st.rerun() # Platzhalter
