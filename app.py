import streamlit as st
import pandas as pd
import re
import time

# --- 1. SETUP & STYLING ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

st.markdown("""
    <style>
    @keyframes blinker { 50% { opacity: 0.1; } }
    .stButton button { width: 100%; height: 50px; font-weight: bold !important; border-radius: 12px !important; border: 2px solid #1a4a9e !important; }
    .judge-header-box { background-color: #1a4a9e; color: white; padding: 8px; border-radius: 10px; text-align: center; font-size: 15px !important; font-weight: bold; height: 60px; display: flex; align-items: center; justify-content: center; }
    .class-label-box { background-color: #e9ecef; color: #1a4a9e; border-radius: 10px; text-align: center; font-size: 14px !important; font-weight: 800; border: 2px solid #1a4a9e; display: flex; align-items: center; justify-content: center; height: 85px; width: 100%; line-height: 1.1; }
    .cat-card, .placeholder-box { padding: 5px; border: 2px solid #1a4a9e; text-align: center; background-color: #ffffff; border-radius: 14px; min-height: 85px; display: flex; flex-direction: column; justify-content: center; align-items: center; margin-bottom: 5px; }
    .placeholder-box { border: 1px solid #d1d1d1; background-color: #f2f2f2; color: #999; }
    .winner-card { border: 3px solid #ff4d4d !important; background-color: #ffcccc !important; }
    .cat-number { font-size: 28px !important; font-weight: 900 !important; color: #1a4a9e; line-height: 1.0; }
    .cat-details { font-size: 13px !important; color: #333; font-weight: bold; line-height: 1.1; }
    .vote-bar-container { width: 80%; height: 6px; background-color: rgba(0,0,0,0.1); border-radius: 3px; margin-top: 4px; overflow: hidden; }
    .vote-bar-fill { height: 100%; background-color: #ff4d4d; }
    .winner-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: white; z-index: 9999; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
    .tag-container { margin-top: 4px; display: flex; justify-content: center; flex-wrap: wrap; gap: 3px; }
    .tag { font-weight: bold; padding: 2px 6px; border-radius: 4px; font-size: 10px; text-transform: uppercase; }
    .tag-zumrichten { background-color: #007bff; color: white; }
    .tag-biv { background-color: #28a745; color: white; animation: blinker 1.5s linear infinite; }
    .tag-nom { background-color: #ffc107; color: black; animation: blinker 1s linear infinite; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GLOBALER SPEICHER ---
@st.cache_resource
def get_store(): return {"data": {}, "votes": {}}
store = get_store()

if "view" not in st.session_state: st.session_state.view = "Home"

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
        df['KLASSE_INTERNAL'] = df['AUSSTELLUNGSKLASSE'] if 'AUSSTELLUNGSKLASSE' in df.columns else df.get('KLASSE', '')
        df['KAT_STR'] = df['KATALOG-NR'].astype(str).str.replace('.0', '', regex=False)
        return df
    except: return None

def get_full_label(row):
    r = row.get('RASSE_KURZ', row.get('RASSE', ''))
    g = roman_to_numeric(row.get('FARBGRUPPE', ''))
    e = row.get('FARBE', '')
    return f"{r} {g} ({e})".strip()

# --- 4. VIEWS ---

if st.session_state.view == "Home":
    st.title("🐾 KECB Burgdorf 2026")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📢 LIVE-DASHBOARD"): st.session_state.view = "Dashboard"; st.rerun()
        if st.button("🏆 BEST IN SHOW (PUBLIC)"): st.session_state.view = "BIS_Public"; st.rerun()
        if st.button("🗳️ RICHTER-VOTING"): st.session_state.view = "Judge_Voting"; st.rerun()
    with c2:
        if st.button("📝 STEWARD-PULT"): st.session_state.view = "Steward_Login"; st.rerun()
        if st.button("👨‍⚖️ BIS ADMIN / CONTROL"): st.session_state.view = "BIS_Admin_Control"; st.rerun()
        if st.button("⚙️ ADMIN-KONSOLE (RESET)"): st.session_state.view = "Admin_Login"; st.rerun()

elif st.session_state.view == "Dashboard":
    st.title("📢 Live-Aufruf")
    tag = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"]).upper()
    df_full = load_labels()
    if df_full is not None:
        r_col = f"RICHTER {tag}"
        judges = sorted([r for r in df_full[df_full[tag].astype(str).str.upper() == 'X'][r_col].unique() if str(r) != "nan"])
        cols = st.columns(len(judges) if judges else 1)
        for i, j in enumerate(judges):
            with cols[i]:
                st.markdown(f"<div class='judge-header-box'>{j}</div>", unsafe_allow_html=True)
                for k, v in store["data"].items():
                    if "|" in k:
                        kat_nr, r_name = k.split("|")
                        if r_name == j and any(v.values()):
                            m = df_full[df_full['KAT_STR'] == kat_nr]
                            if not m.empty:
                                tags_html = "".join([f"<span class='tag tag-{t.replace(' ', '').lower()}'>{t.upper()}</span>" for t, active in v.items() if active])
                                st.markdown(f"<div class='cat-card'><div class='cat-number'>{kat_nr}</div><div class='cat-details'>{get_full_label(m.iloc[0])}</div><div class='tag-container'>{tags_html}</div></div>", unsafe_allow_html=True)
    if st.button("⬅️ Zurück"): st.session_state.view = "Home"; st.rerun()

elif st.session_state.view == "Steward_Panel":
    st.title("📝 Steward-Pult")
    tag = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"]).upper()
    df_full = load_labels()
    if df_full is not None:
        r_col = f"RICHTER {tag}"
        all_j = sorted([r for r in df_full[df_full[tag].astype(str).str.upper() == 'X'][r_col].unique() if str(r) != "nan"])
        mein_richter = st.selectbox("Richter wählen:", ["--"] + all_j)
        if mein_richter != "--":
            df_j = df_full[(df_full[tag].astype(str).str.upper() == 'X') & (df_full[r_col] == mein_richter)].sort_values('KATALOG-NR')
            for _, row in df_j.iterrows():
                nr = row['KAT_STR']; k = f"{nr}|{mein_richter}"
                if k not in store["data"]: store["data"][k] = {"Zum Richten": False, "BIV": False, "NOM": False}
                c1, c2, c3, c4 = st.columns([3, 1.2, 1, 1])
                c1.write(f"**#{nr}** {get_full_label(row)}")
                store["data"][k]["Zum Richten"] = c2.checkbox("Zum Richten", value=store["data"][k]["Zum Richten"], key=f"auf{k}")
                store["data"][k]["BIV"] = c3.checkbox("BIV", value=store["data"][k]["BIV"], key=f"biv{k}")
                store["data"][k]["NOM"] = c4.checkbox("NOM", value=store["data"][k]["NOM"], key=f"nom{k}")
    if st.button("⬅️ Zurück"): st.session_state.view = "Home"; st.rerun()

elif st.session_state.view == "Judge_Voting":
    st.title("🗳️ Richter Abstimmung")
    df_full = load_labels()
    if df_full is not None:
        tag = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"]).upper()
        r_col = f"RICHTER {tag}"; all_judges = sorted([r for r in df_full[r_col].unique() if str(r) != "nan"])
        active_j = st.selectbox("Identität:", ["--"] + all_judges)
        active_cat = st.selectbox("Kategorie:", sorted(df_full['KATEGORIE'].unique()))
        if active_j != "--":
            bis_defs = [("Adult Male", [1,3,5,7,9], "M"), ("Adult Female", [1,3,5,7,9], "W"), ("Neuter Male", [2,4,6,8,10], "M"), ("Neuter Female", [2,4,6,8,10], "W"), ("Junior 8-12 Male", [11], "M"), ("Junior 8-12 Female", [11], "W"), ("Kitten 4-8 Male", [12], "M"), ("Kitten 4-8 Female", [12], "W")]
            for label, klassen, geschl in bis_defs:
                with st.expander(f"Wahl für {label}"):
                    pool = df_full[(df_full['SELECTION'] == 'X') & (df_full['KATEGORIE'] == active_cat) & (df_full['KLASSE_INTERNAL'].isin(klassen)) & (df_full['GESCHLECHT'] == geschl)]
                    if not pool.empty:
                        opts = {f"#{r['KAT_STR']} - {get_full_label(r)}": r['KAT_STR'] for _, r in pool.iterrows()}
                        v_key = f"v_{active_cat}_{label}_{active_j}"
                        curr = store["votes"].get(v_key, "Keine Wahl")
                        idx = (list(opts.values()).index(curr) + 1) if curr in opts.values() else 0
                        sel = st.radio("Favorit:", ["Keine Wahl"] + list(opts.keys()), index=idx, key=f"r_{v_key}")
                        store["votes"][v_key] = opts[sel] if sel != "Keine Wahl" else "Keine Wahl"
    if st.button("⬅️ Zurück"): st.session_state.view = "Home"; st.rerun()

elif st.session_state.view == "BIS_Admin_Control":
    st.title("👨‍⚖️ BIS Admin Control")
    df_full = load_labels()
    if df_full is not None:
        sel_cat = st.selectbox("Kategorie:", sorted(df_full['KATEGORIE'].unique()))
        bis_defs = [("Adult Male", [1,3,5,7,9], "M"), ("Adult Female", [1,3,5,7,9], "W"), ("Neuter Male", [2,4,6,8,10], "M"), ("Neuter Female", [2,4,6,8,10], "W"), ("Junior 8-12 Male", [11], "M"), ("Junior 8-12 Female", [11], "W"), ("Kitten 4-8 Male", [12], "M"), ("Kitten 4-8 Female", [12], "W")]
        for label, klassen, geschl in bis_defs:
            with st.expander(f"KLASSE: {label}", expanded=True):
                c1, c2 = st.columns(2)
                with c1:
                    store["data"][f"rev_{sel_cat}_{label}"] = st.checkbox("Noms zeigen", value=store["data"].get(f"rev_{sel_cat}_{label}", False), key=f"cbre_{sel_cat}{label}")
                    store["data"][f"win_rev_{sel_cat}_{label}"] = st.checkbox("Winner zeigen", value=store["data"].get(f"win_rev_{sel_cat}_{label}", False), key=f"cbwi_{sel_cat}{label}")
                with c2:
                    prefix = f"v_{sel_cat}_{label}_"
                    v_list = [v for k, v in store["votes"].items() if k.startswith(prefix) and v != "Keine Wahl"]
                    if v_list:
                        top_cat = pd.Series(v_list).value_counts().index[0]
                        if st.button(f"✨ #{top_cat} ZELEBRIEREN", key=f"btn_{sel_cat}{label}"):
                            store["data"]["active_slide"] = top_cat
                            store["data"]["slide_start"] = time.time()
    if st.button("⬅️ Zurück"): st.session_state.view = "Home"; st.rerun()

elif st.session_state.view == "BIS_Public":
    if "active_slide" in store["data"] and store["data"]["active_slide"]:
        if time.time() - store["data"].get("slide_start", 0) > 15:
            store["data"]["active_slide"] = None; st.rerun()
        df_all = load_labels()
        winner = df_all[df_all['KAT_STR'] == str(store["data"]["active_slide"])].iloc[0]
        st.markdown(f"""<div class="winner-overlay">
            <div style="font-size: 50px; font-weight: bold; color: #333;">{winner['KAT_STR']}. {get_full_label(winner)}</div>
            <div style="font-size: 70px; font-weight: 900; color: #1a4a9e; margin: 30px 0;">{winner.get('NAME_DER_KATZE', 'WORLD WINNER')}</div>
            <div style="font-size: 40px; font-style: italic; color: #666;">{winner.get('BESITZER', 'Aussteller')}</div>
            <div style="margin-top: 50px;"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Logo_FIFE.svg/1200px-Logo_FIFE.svg.png" width="120"></div>
        </div>""", unsafe_allow_html=True)
        time.sleep(1); st.rerun()
    else:
        st.title("🏆 Best in Show")
        df_full = load_labels()
        if df_full is not None:
            tag = "TAG 1"; r_col = f"RICHTER {tag}"
            sel_cat = st.selectbox("Kategorie:", sorted(df_full['KATEGORIE'].unique()))
            judges = sorted([r for r in df_full[df_full[tag].astype(str).str.upper() == 'X'][r_col].unique() if str(r) != "nan"])
            bis_defs = [("Adult Male", [1,3,5,7,9], "M"), ("Adult Female", [1,3,5,7,9], "W"), ("Neuter Male", [2,4,6,8,10], "M"), ("Neuter Female", [2,4,6,8,10], "W"), ("Junior 8-12 Male", [11], "M"), ("Junior 8-12 Female", [11], "W"), ("Kitten 4-8 Male", [12], "M"), ("Kitten 4-8 Female", [12], "W")]
            cols = st.columns([1.2] + [1]*len(judges) + [1.2])
            for i, j in enumerate(judges): cols[i+1].markdown(f"<div class='judge-header-box'>{j}</div>", unsafe_allow_html=True)
            cols[-1].markdown(f"<div class='judge-header-box' style='background-color:#b21f2d;'>BEST IN SHOW</div>", unsafe_allow_html=True)
            for label, klassen, geschl in bis_defs:
                row_cols = st.columns([1.2] + [1]*len(judges) + [1.2])
                row_cols[0].markdown(f"<div class='class-label-box'>{label}</div>", unsafe_allow_html=True)
                reveal = store["data"].get(f"rev_{sel_cat}_{label}", False)
                for i, j in enumerate(judges):
                    with row_cols[i+1]:
                        if reveal:
                            m = df_full[(df_full['SELECTION'] == 'X') & (df_full[r_col] == j) & (df_full['KATEGORIE'] == sel_cat) & (df_full['KLASSE_INTERNAL'].isin(klassen)) & (df_full['GESCHLECHT'] == geschl)]
                            if not m.empty: st.markdown(f"<div class='cat-card'><div class='cat-number'>{m.iloc[0]['KAT_STR']}</div></div>", unsafe_allow_html=True)
                            else: st.markdown("<div class='placeholder-box'>–</div>", unsafe_allow_html=True)
                        else: st.markdown("<div class='placeholder-box'>🔒</div>", unsafe_allow_html=True)
                with row_cols[-1]:
                    if store["data"].get(f"win_rev_{sel_cat}_{label}", False):
                        prefix = f"v_{sel_cat}_{label}_"
                        v_list = [v for k, v in store["votes"].items() if k.startswith(prefix) and v != "Keine Wahl"]
                        if v_list:
                            counts = pd.Series(v_list).value_counts(); win_nr = counts.index[0]
                            perc = (counts.iloc[0] / len(judges)) * 100
                            st.markdown(f"<div class='cat-card winner-card'><div class='cat-number'>{win_nr}</div><div class='vote-bar-container'><div class='vote-bar-fill' style='width:{perc}%'></div></div></div>", unsafe_allow_html=True)
                        else: st.markdown("<div class='placeholder-box'>Wahl...</div>", unsafe_allow_html=True)
                    else: st.markdown("<div class='placeholder-box'>🔒</div>", unsafe_allow_html=True)
    if st.button("⬅️ Zurück"): st.session_state.view = "Home"; st.rerun()

elif st.session_state.view == "Steward_Login":
    pwd = st.text_input("Passwort (Steward)", type="password")
    if st.button("Login"):
        if pwd == "steward2026": st.session_state.view = "Steward_Panel"; st.rerun()

elif st.session_state.view == "Admin_Login":
    pwd = st.text_input("Passwort (Admin)", type="password")
    if st.button("Login"):
        if pwd == "admin2026": st.session_state.view = "Admin_Panel"; st.rerun()

elif st.session_state.view == "Admin_Panel":
    if st.button("RESET ALL DATA"): store["data"] = {}; store["votes"] = {}; st.success("Geleert"); st.rerun()
    if st.button("⬅️ Zurück"): st.session_state.view = "Home"; st.rerun()
