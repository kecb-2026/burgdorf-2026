import streamlit as st
import pandas as pd
import re

# --- 1. SETUP & STYLING ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

st.markdown("""
    <style>
    /* Buttons */
    .stButton button { 
        width: 100%; height: 60px; font-size: 13px !important; 
        font-weight: bold !important; border-radius: 12px !important;
        margin-bottom: 5px; border: 2px solid #1a4a9e !important;
    }
    
    /* Gitter für Dashboard */
    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 15px;
        padding: 10px;
    }

    /* Katzen-Karten & Platzhalter (Exakt identisch in der Struktur) */
    .cat-card, .placeholder-box { 
        padding: 15px; border-radius: 18px; text-align: center; 
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 10px;
        min-height: 180px; /* Fixe Mindesthöhe für Gleichheit */
        display: flex; flex-direction: column; justify-content: center; align-items: center;
    }

    .cat-card { 
        border: 2px solid #1a4a9e; 
        background-color: #ffffff; 
    }

    .placeholder-box {
        border: 2px dashed #d1d1d1; 
        background-color: rgba(240, 240, 240, 0.5);
        color: #bbbbbb; font-size: 24px;
    }

    .cat-number { font-size: 42px !important; font-weight: 900 !important; color: #1a4a9e; line-height: 1.0; margin: 0; }
    .cat-details { font-size: 11px; color: #333; font-weight: bold; margin-top: 6px; }
    
    /* Tags */
    .tag-container { margin-top: 8px; display: flex; flex-direction: column; gap: 4px; width: 100%; }
    .tag { font-weight: bold; padding: 3px 8px; border-radius: 5px; font-size: 11px; color: white; }
    .tag-aufruf { background-color: #007bff; }
    .tag-biv { background-color: #28a745; }
    .tag-nom { background-color: #ffc107; color: black; }
    
    .judge-col { 
        border: 2px solid #1a4a9e; padding: 10px; border-radius: 15px; 
        background-color: #f8f9fa; margin-bottom: 10px; 
    }
    .judge-title { 
        font-size: 14px; font-weight: bold; color: white; background-color: #1a4a9e; 
        padding: 5px; border-radius: 8px; text-align: center; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GLOBALER SPEICHER ---
class GlobalStore:
    def __init__(self): self.data = {} 

@st.cache_resource
def get_store(): return GlobalStore()
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
        df['KL_INT'] = df['AUSSTELLUNGSKLASSE'] if 'AUSSTELLUNGSKLASSE' in df.columns else df.get('KLASSE', '')
        if 'KATALOG-NR' in df.columns:
            df['KAT_STR'] = df['KATALOG-NR'].astype(str).str.replace('.0', '', regex=False)
        return df
    except: return None

def set_view(name):
    st.session_state.view = name
    st.rerun()

# --- 4. VIEWS ---

if st.session_state.view == "Home":
    st.title("🐾 KECB Burgdorf 2026")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📢 LIVE-DASHBOARD"): set_view("Dashboard")
        if st.button("🏆 BEST IN SHOW (PUBLIC)"): set_view("BIS_Public")
    with c2:
        if st.button("📝 STEWARD-PULT"): set_view("Steward_Login")
        if st.button("👨‍⚖️ BIS ADMIN"): set_view("BIS_Admin")

elif st.session_state.view == "Dashboard":
    st.title("📢 Live-Aufruf & Status")
    active_cats = {}
    for k, v in store.data.items():
        if "|" in k:
            nr, _ = k.split("|")
            if any(v.values()):
                if nr not in active_cats: active_cats[nr] = {"Aufruf": False, "BIV": False, "NOM": False}
                for s in ["Aufruf", "BIV", "NOM"]:
                    if v.get(s): active_cats[nr][s] = True
    if active_cats:
        sorted_nrs = sorted(active_cats.keys(), key=lambda x: int(x) if x.isdigit() else 999)
        html = "<div class='dashboard-grid'>"
        for nr in sorted_nrs:
            s = active_cats[nr]
            tags = "".join([f"<span class='tag tag-{t.lower()}'>{t}</span>" for t, active in s.items() if active])
            html += f"<div class='cat-card'><div class='cat-number'>{nr}</div><div class='tag-container'>{tags}</div></div>"
        st.markdown(html + "</div>", unsafe_allow_html=True)
    if st.button("⬅️ Zurück"): set_view("Home")

elif st.session_state.view == "BIS_Public":
    st.title("🏆 Best in Show")
    df = load_labels()
    if df is not None:
        tag = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"]).upper()
        sel_cat = st.selectbox("Kategorie:", sorted(df['KATEGORIE'].unique()))
        bis_defs = [("Adult Male", [1,3,5,7,9], "M"), ("Adult Female", [1,3,5,7,9], "W"), ("Neuter Male", [2,4,6,8,10], "M"), ("Neuter Female", [2,4,6,8,10], "W")]
        r_col = f"RICHTER {tag}"
        judges = sorted([r for r in df[df[tag]=='X'][r_col].unique() if str(r)!="nan"])
        for label, kl, gs in bis_defs:
            if store.data.get(f"rev_{sel_cat}_{label}", True):
                st.subheader(label)
                cols = st.columns(len(judges) if judges else 1)
                for i, j in enumerate(judges):
                    with cols[i]:
                        st.markdown(f"<div class='judge-title'>{j}</div>", unsafe_allow_html=True)
                        m = df[(df['SELECTION']=='X') & (df[r_col]==j) & (df['KATEGORIE']==sel_cat) & (df['KL_INT'].isin(kl)) & (df['GESCHLECHT']==gs)]
                        if not m.empty:
                            nr = m.iloc[0]['KAT_STR']
                            st.markdown(f"<div class='cat-card'><div class='cat-number'>{nr}</div></div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div class='placeholder-box'>–</div>", unsafe_allow_html=True)
    if st.button("⬅️ Zurück"): set_view("Home")

elif st.session_state.view == "Steward_Panel":
    st.title("📝 Steward")
    df = load_labels()
    if df is not None:
        tag = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"]).upper()
        r_col = f"RICHTER {tag}"
        all_j = sorted([r for r in df[df[tag]=='X'][r_col].unique() if str(r)!="nan"])
        mein_j = st.selectbox("Richter:", ["--"] + all_j)
        if mein_j != "--":
            df_j = df[(df[tag]=='X') & (df[r_col]==mein_j)].sort_values('KATALOG-NR')
            for _, row in df_j.iterrows():
                nr = row['KAT_STR']; k = f"{nr}|{mein_j}"
                if k not in store.data: store.data[k] = {"Aufruf": False, "BIV": False, "NOM": False}
                c1, c2, c3, c4 = st.columns([2,1,1,1])
                c1.write(f"**#{nr}**")
                store.data[k]["Aufruf"] = c2.checkbox("Ruf", value=store.data[k]["Aufruf"], key=f"a{k}")
                store.data[k]["BIV"] = c3.checkbox("BIV", value=store.data[k]["BIV"], key=f"b{k}")
                store.data[k]["NOM"] = c4.checkbox("NOM", value=store.data[k]["NOM"], key=f"n{k}")
    if st.button("⬅️ Zurück"): set_view("Home")

elif st.session_state.view == "Steward_Login":
    st.title("🔒 Login")
    pwd = st.text_input("Passwort", type="password")
    if st.button("Anmelden") and pwd == "steward2026": set_view("Steward_Panel")
    if st.button("⬅️ Zurück"): set_view("Home")

elif st.session_state.view == "BIS_Admin":
    st.title("👨‍⚖️ Admin Control")
    if st.button("DATEN RESET"): store.data = {}; st.success("Geleert!")
    if st.button("⬅️ Zurück"): set_view("Home")
