import streamlit as st
import pandas as pd
import re

# --- 1. SETUP & STYLING ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

st.markdown("""
    <style>
    /* Große Buttons für den Startbildschirm */
    .stButton button { width: 100%; height: 100px; font-size: 24px !important; font-weight: bold !important; border-radius: 20px !important; }
    .judge-col { border: 3px solid #1a4a9e; padding: 15px; border-radius: 20px; background-color: #ffffff; margin-bottom: 20px; }
    .judge-col h3 { font-size: 32px !important; color: white; background-color: #1a4a9e; padding: 10px; border-radius: 10px; text-align: center; }
    .cat-card { padding: 20px; border-bottom: 2px solid #f0f0f0; margin-bottom: 25px; text-align: center; background-color: #fafafa; border-radius: 20px; }
    .cat-number { font-size: 110px !important; font-weight: 900 !important; color: #1a4a9e; line-height: 0.8; margin: 10px 0; }
    .cat-label { font-size: 26px; color: #333; font-weight: bold; margin: 10px 0; }
    .tag { font-weight: bold; padding: 10px 20px; border-radius: 10px; font-size: 22px; display: inline-block; margin: 5px; }
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

# --- 3. SESSION STATE INITIALISIERUNG ---
if "view" not in st.session_state:
    st.session_state.view = "Home"
if "auth_role" not in st.session_state:
    st.session_state.auth_role = None

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
        df = pd.read_excel("LABELS.xlsm", engine='openpyxl', header=1)
        df.columns = df.columns.astype(str).str.strip()
        df['KAT_STR'] = df['Katalog-Nr'].astype(str).str.replace('.0', '', regex=False)
        return df
    except: return None

def get_full_label(row):
    r = row.get('Rasse_Kurz', row.get('Rasse', ''))
    g = roman_to_numeric(row.get('Farbgruppe', ''))
    e = row.get('Farbe', '')
    label = f"{r} {g}".strip()
    if pd.notna(e) and e != "": label += f" ({e})"
    return label

# --- 5. KLASSEN LOGIK ---
rows_def = [
    {"label": "Adult M", "f": lambda r: str(r.get('Klasse','')) in ['1','3','5','7','9'] and str(r.get('Geschlecht','')).upper() in ['M','1.0']},
    {"label": "Adult W", "f": lambda r: str(r.get('Klasse','')) in ['1','3','5','7','9'] and str(r.get('Geschlecht','')).upper() in ['W','F','0.1']},
    {"label": "Kastriert M", "f": lambda r: str(r.get('Klasse','')) in ['2','4','6','8','10'] and str(r.get('Geschlecht','')).upper() in ['M','KM','1.0']},
    {"label": "Kastriert W", "f": lambda r: str(r.get('Klasse','')) in ['2','4','6','8','10'] and str(r.get('Geschlecht','')).upper() in ['W','F','KW','0.1']},
    {"label": "Junior 11 (8-12)", "f": lambda r: str(r.get('Klasse','')) == '11'},
    {"label": "Kitten 12 (4-8)", "f": lambda r: str(r.get('Klasse','')) == '12'}
]

# --- 6. LANDING PAGE ---
if st.session_state.view == "Home":
    st.title("🐾 KECB Burgdorf 2026 - Systemauswahl")
    st.write("Bitte wählen Sie Ihren Bereich aus:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📢 DISPLAY (Öffentlich)"):
            st.session_state.view = "Dashboard"
            st.rerun()
        if st.button("📝 STEWARD (Login)"):
            st.session_state.view = "Steward_Login"
            st.rerun()
    with col2:
        if st.button("🏆 BIS GRID (Öffentlich)"):
            st.session_state.view = "BIS_Grid"
            st.rerun()
        if st.button("⚙️ ADMIN / RICHTER"):
            st.session_state.view = "Admin_Login"
            st.rerun()

# --- 7. LOGIN SCREENS ---
elif st.session_state.view == "Steward_Login":
    st.title("🔒 Steward Login")
    pwd = st.text_input("Passwort", type="password")
    if st.button("Anmelden"):
        if pwd == "steward2026":
            st.session_state.auth_role = "steward"
            st.session_state.view = "Steward_Panel"
            st.rerun()
        else: st.error("Falsch")
    if st.button("Zurück"): st.session_state.view = "Home"; st.rerun()

elif st.session_state.view == "Admin_Login":
    st.title("🔒 Admin / Richter Login")
    pwd = st.text_input("Passwort", type="password")
    if st.button("Anmelden"):
        if pwd == "admin2026":
            st.session_state.auth_role = "admin"
            st.session_state.view = "Admin_Panel"
            st.rerun()
        elif pwd == "richter2026":
            st.session_state.auth_role = "richter"
            st.session_state.view = "Richter_Panel"
            st.rerun()
        else: st.error("Falsch")
    if st.button("Zurück"): st.session_state.view = "Home"; st.rerun()

# --- 8. HAUPTANSICHTEN (NACH LOGIN / AUSWAHL) ---
else:
    # Sidebar Navigation für eingeloggte User / gewählte Views
    st.sidebar.title("KECB 2026")
    if st.sidebar.button("🏠 Hauptmenü / Logout"):
        st.session_state.view = "Home"
        st.session_state.auth_role = None
        st.rerun()
    
    tag = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"])
    df_full = load_labels()
    r_col = f"Richter {tag}"
    df_tag = df_full[df_full[tag].astype(str).str.upper() == 'X'].copy() if df_full is not None else None

    if st.session_state.view == "Dashboard":
        st.title(f"Live-Aufruf ({tag})")
        # ... (Dashboard Code wie oben)
        if df_tag is not None:
            judges = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
            cols = st.columns(len(judges))
            for i, j in enumerate(judges):
                with cols[i]:
                    st.markdown(f"<div class='judge-col'><h3>{j}</h3>", unsafe_allow_html=True)
                    for k, v in store.data.items():
                        nr, r_n = k.split("|")
                        if r_n == j and any(v.values()):
                            m = df_tag[df_tag['KAT_STR'] == nr]
                            if not m.empty:
                                row = m.iloc[0]
                                st.markdown(f"<div class='cat-card'><div class='cat-number'>{nr}</div><div class='cat-label'>{get_full_label(row)}</div>", unsafe_allow_html=True)
                                if v.get("Aufruf"): st.markdown("<span class='tag tag-aufruf'>RUF</span>", unsafe_allow_html=True)
                                if v.get("BIV"): st.markdown("<span class='tag tag-biv'>BIV</span>", unsafe_allow_html=True)
                                if v.get("NOM"): st.markdown("<span class='tag tag-nom'>NOM</span>", unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.view == "BIS_Grid":
        st.title("Best in Show Grid")
        # ... (Grid Code wie oben)
        if df_tag is not None:
            judges = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
            html = "<table style='width:100%; border-collapse: collapse; border: 2px solid #1a4a9e;'><tr><th style='border: 2px solid #1a4a9e; background:#1a4a9e; color:white;'>Klasse</th>"
            for j in judges: html += f"<th style='border: 2px solid #1a4a9e; background:#1a4a9e; color:white;'>{j}</th>"
            html += "</tr>"
            for rd in rows_def:
                html += f"<tr><td style='border: 2px solid #1a4a9e; background:#f0f0f0; font-weight:bold;'>{rd['label']}</td>"
                for j in judges:
                    cell = ""
                    for k, v in store.data.items():
                        if v.get("NOM"):
                            nr, r_n = k.split("|")
                            if r_n == j:
                                match = df_tag[df_tag['KAT_STR'] == nr]
                                if not match.empty and rd['f'](match.iloc[0]):
                                    cell += f"<div style='text-align:center;'><span style='font-size:30px; font-weight:bold;'>{nr}</span><br><small>{get_full_label(match.iloc[0])}</small></div>"
                    html += f"<td style='border: 2px solid #1a4a9e;'>{cell}</td>"
                html += "</tr>"
            st.markdown(html + "</table>", unsafe_allow_html=True)

    elif st.session_state.view == "Steward_Panel":
        st.title("Steward-Steuerung")
        all_j = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
        mein_richter = st.selectbox("Richter:", ["--"] + all_j)
        if mein_richter != "--":
            df_j = df_tag[df_tag[r_col] == mein_richter]
            for _, row in df_j.iterrows():
                nr = row['KAT_STR']; k = f"{nr}|{mein_richter}"
                if k not in store.data: store.data[k] = {"Aufruf": False, "BIV": False, "NOM": False}
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                c1.write(f"**#{nr}** - {get_full_label(row)}")
                store.data[k]["Aufruf"] = c2.checkbox("Ruf", value=store.data[k]["Aufruf"], key=f"a{k}")
                store.data[k]["BIV"] = c3.checkbox("BIV", value=store.data[k]["BIV"], key=f"b{k}")
                store.data[k]["NOM"] = c4.checkbox("NOM", value=store.data[k]["NOM"], key=f"n{k}")
