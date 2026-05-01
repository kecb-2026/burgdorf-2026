import streamlit as st
import pandas as pd
import re

# --- 1. SETUP & STYLING ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

st.markdown("""
    <style>
    /* Startbildschirm Buttons - Höhe reduziert */
    .stButton button { 
        width: 100%; 
        height: 60px; 
        font-size: 13px !important; 
        font-weight: bold !important; 
        border-radius: 12px !important;
        margin-bottom: 5px;
        border: 2px solid #1a4a9e !important;
    }
    
    /* Dashboard & Cards - Kompakterer Rahmen und Abstände */
    .judge-col { 
        border: 2px solid #1a4a9e; 
        padding: 5px; 
        border-radius: 15px; 
        background-color: #ffffff; 
        margin-bottom: 8px; 
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        display: flex; 
        flex-direction: column;
        gap: 5px;
    }

    .judge-col h3 { 
        font-size: 14px !important; 
        color: white; 
        background-color: #1a4a9e; 
        padding: 3px; 
        border-radius: 8px; 
        text-align: center; 
        margin-bottom: 5px;
    }

    .cat-card { 
        padding: 5px; 
        border: 1px solid #e0e0e0; 
        text-align: center; 
        background-color: #ffffff; 
        border-radius: 15px; 
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
        height: 160px; 
        display: flex;
        flex-direction: column;
        justify-content: center; 
    }
    .cat-number { font-size: 38px !important; font-weight: 900 !important; color: #1a4a9e; line-height: 0.9; margin: 2px 0; }
    .cat-label { font-size: 11px; color: #333; font-weight: bold; margin: 2px 0; }
    .cat-category-red { font-size: 10px; font-weight: bold; color: #ff0000; margin-bottom: 2px; }

    .tag-container { margin-top: 5px; display: flex; justify-content: center; flex-wrap: wrap; gap: 5px; }
    .tag { font-weight: bold; padding: 4px 10px; border-radius: 6px; font-size: 10px; display: inline-block; }
    .tag-aufruf { background-color: #007bff; color: white; }
    @keyframes blinker { 50% { opacity: 0.2; } }
    .tag-biv { background-color: #28a745; color: white; animation: blinker 1.5s linear infinite; }
    .tag-nom { background-color: #ffc107; color: black; animation: blinker 1s linear infinite; }

    .bis-table { width: 100%; border-collapse: collapse; margin-bottom: 15px; table-layout: fixed; background: white; }
    .bis-table th, .bis-table td { border: 1px solid #1a4a9e; padding: 3px; text-align: center; vertical-align: middle; }
    .bis-table th { background-color: #1a4a9e; color: white; font-size: 9px; }
    .class-header { background-color: #f0f0f0 !important; font-weight: bold; text-align: left !important; width: 150px; color: #1a4a9e; font-size: 11px; }
    .bis-nr { font-size: 18px !important; font-weight: 900 !important; color: #000; margin: 0; line-height: 1; }
    .bis-label { font-size: 9px; font-weight: bold; color: #333; margin-top: 1px; }
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

# --- 4. HILFSFUNKTIONEN ---
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
        df = pd.read_excel("LABELS.xlsm", engine='openpyxl', header=0)
        df.columns = [str(c).strip().upper() for c in df.columns]
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

# --- 7. VIEWS ---

if st.session_state.view == "Home":
    st.title("🐾 KECB Burgdorf 2026")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📢 LIVE-DASHBOARD"): set_view("Dashboard")
        if st.button("🏆 BEST IN SHOW (PUBLIC)"): set_view("BIS_Public")
    with col2:
        if st.button("📝 STEWARD-PULT"): set_view("Steward_Login")
        if st.button("👨‍⚖️ BIS ADMIN / CONTROL"): set_view("BIS_Admin_Control")

elif st.session_state.view == "Steward_Login":
    st.title("🔒 Steward Login")
    pwd = st.text_input("Passwort", type="password")
    if st.button("Anmelden") and pwd == "steward2026": set_view("Steward_Panel")
    if st.button("Zurück"): set_view("Home")

elif st.session_state.view == "Admin_Login":
    st.title("⚙️ Admin / Richter Login")
    pwd = st.text_input("Passwort", type="password")
    if st.button("Anmelden") and pwd == "admin2026": set_view("Admin_Panel")
    if st.button("Zurück"): set_view("Home")

elif st.session_state.view == "Admin_Panel":
    st.title("👨‍⚖️ Admin-Konsole")
    st.subheader("🧹 Daten-Management")
    with st.expander("Gefahrenzone: Speicher leeren"):
        st.warning("Dies löscht alle aktuellen Aufrufe von den Dashboards!")
        if st.button("🚨 ALLE DATEN ZURÜCKSETZEN"):
            store.data = {} 
            st.success("Speicher geleert!")
            st.rerun()
    st.divider()
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
                                        <div class='cat-category-red'>Kategorie {row.get('KATEGORIE', '–')}</div>
                                        <div class='cat-number'>{nr}</div>
                                        <div class='cat-label'>{get_full_label(row)}</div>
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
        st.title("👨‍⚖️ BIS Admin Steuerung")
        if df_full is not None:
            all_cats = sorted(df_full['KATEGORIE'].unique())
            sel_cat = st.selectbox("Kategorie verwalten:", all_cats, key="admin_cat")
            bis_defs = [
                ("Adult Male", [1, 3, 5, 7, 9], "M"), ("Adult Female", [1, 3, 5, 7, 9], "W"),
                ("Neuter Male", [2, 4, 6, 8, 10], "M"), ("Neuter Female", [2, 4, 6, 8, 10], "W"),
                ("Junior Male (11)", [11], "M"), ("Junior Female (11)", [11], "W"),
                ("Kitten Male (12)", [12], "M"), ("Kitten Female (12)", [12], "W")
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
            
            if 'SELECTION' in df_full.columns:
                # Hole alle Nominierten dieser Kategorie (Basis für Richterliste)
                df_nom = df_full[(df_full['SELECTION'].astype(str).str.upper() == 'X') & (df_full['KATEGORIE'] == sel_cat)].copy()
                
                # Richterliste aus ALLEN Nominierten dieser Kategorie generieren
                judges = sorted([r for r in df_nom[r_col].unique() if str(r) != "nan"]) if r_col in df_nom.columns else []
                
                # Tabellen-Header (Immer sichtbar)
                h_cols = st.columns([1.5] + [1] * len(judges))
                h_cols[0].markdown("**Klasse**")
                for i, j in enumerate(judges):
                    h_cols[i+1].markdown(f"<div style='background-color:#1a4a9e; color:white; padding:5px; border-radius:8px; text-align:center; font-size:10px; font-weight:bold;'>{j}</div>", unsafe_allow_html=True)
                st.divider()

                bis_defs = [
                    ("Adult Male", [1, 3, 5, 7, 9], "M"), ("Adult Female", [1, 3, 5, 7, 9], "W"),
                    ("Neuter Male", [2, 4, 6, 8, 10], "M"), ("Neuter Female", [2, 4, 6, 8, 10], "W"),
                    ("Junior Male (11)", [11], "M"), ("Junior Female (11)", [11], "W"),
                    ("Kitten Male (12)", [12], "M"), ("Kitten Female (12)", [12], "W")
                ]

                for label, klassen, geschlecht in bis_defs:
                    r_cols = st.columns([1.5] + [1] * len(judges))
                    r_cols[0].markdown(f"<div style='font-size:12px; font-weight:bold; padding-top:15px;'>{label}</div>", unsafe_allow_html=True)
                    
                    is_revealed = store.data.get(f"reveal_{sel_cat}_{label}", False)
                    for i, j in enumerate(judges):
                        with r_cols[i+1]:
                            if is_revealed:
                                match = df_nom[(df_nom[r_col] == j) & (df_nom['KLASSE'].isin(klassen)) & (df_nom['GESCHLECHT'].astype(str).str.upper() == geschlecht)]
                                if not match.empty:
                                    for _, row in match.iterrows():
                                        st.markdown(f"""
                                            <div class='cat-card' style='height: auto; padding: 5px; border: 2px solid #1a4a9e; margin-bottom:5px;'>
                                                <div class='cat-number' style='font-size: 26px !important;'>{row['KAT_STR']}</div>
                                                <div style='font-size: 10px; font-weight: bold;'>{row['RASSE']} {row['FARBGRUPPE']}</div>
                                                <div style='font-size: 9px; line-height: 1.1;'>{row['FARBE']}</div>
                                            </div>
                                        """, unsafe_allow_html=True)
                            else:
                                st.markdown("<div style='height:80px; border:1px dashed #ccc; border-radius:10px; margin-bottom:5px;'></div>", unsafe_allow_html=True)
                    st.divider()
            else:
                st.error("Spalte 'SELECTION' nicht gefunden!")
