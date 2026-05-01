import streamlit as st
import pandas as pd
import re

# --- 1. SETUP & STYLING ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

st.markdown("""
    <style>
    /* Sidebar Styling */
    section[data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 2px solid #1a4a9e; }
    .nav-header { font-size: 14px; color: #666; font-weight: bold; margin-top: 20px; text-transform: uppercase; border-bottom: 1px solid #ddd; }
    
    /* Display Styles */
    .judge-col { border: 3px solid #1a4a9e; padding: 15px; border-radius: 20px; background-color: #ffffff; margin-bottom: 20px; }
    .judge-col h3 { font-size: 32px !important; color: white; background-color: #1a4a9e; padding: 10px; border-radius: 10px; text-align: center; }
    .cat-card { padding: 20px; border-bottom: 2px solid #f0f0f0; margin-bottom: 25px; text-align: center; background-color: #fafafa; border-radius: 20px; }
    .cat-number { font-size: 110px !important; font-weight: 900 !important; color: #1a4a9e; line-height: 0.8; margin: 10px 0; }
    
    /* BIS Grid Styles */
    .bis-table { width: 100%; border-collapse: collapse; margin-bottom: 30px; table-layout: fixed; background: white; }
    .bis-table th, .bis-table td { border: 2px solid #1a4a9e; padding: 5px; text-align: center; vertical-align: middle; min-height: 100px; }
    .bis-table th { background-color: #1a4a9e; color: white; font-size: 18px; }
    .class-header { background-color: #f0f0f0 !important; font-weight: bold; text-align: left !important; width: 180px; color: #1a4a9e; }
    .bis-nr { font-size: 48px !important; font-weight: 900 !important; color: #000; margin: 0; line-height: 1; }
    
    /* Animationen */
    .tag { font-weight: bold; padding: 10px 20px; border-radius: 10px; font-size: 22px; display: inline-block; margin: 5px; }
    @keyframes blinker { 50% { opacity: 0.2; } }
    .tag-nom { background-color: #ffc107; color: black; animation: blinker 1s linear infinite; }
    .tag-aufruf { background-color: #007bff; color: white; }
    .tag-biv { background-color: #28a745; color: white; }
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

# --- 3. LOGIN LOGIK ---
def check_auth(role, password):
    auth_key = f"auth_{role}"
    if auth_key not in st.session_state:
        st.session_state[auth_key] = False
    
    if not st.session_state[auth_key]:
        with st.container():
            st.warning(f"Zugriff auf {role.upper()} eingeschränkt.")
            pwd_input = st.text_input(f"Passwort für {role}", type="password", key=f"pwd_{role}")
            if st.button(f"Login {role}"):
                if pwd_input == password:
                    st.session_state[auth_key] = True
                    st.rerun()
                else:
                    st.error("Passwort falsch.")
        return False
    return True

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
    {"label": "Adult M (1,3,5,7,9)", "f": lambda r: str(r.get('Klasse','')) in ['1','3','5','7','9'] and str(r.get('Geschlecht','')).upper() in ['M','1.0']},
    {"label": "Adult W (1,3,5,7,9)", "f": lambda r: str(r.get('Klasse','')) in ['1','3','5','7','9'] and str(r.get('Geschlecht','')).upper() in ['W','F','0.1']},
    {"label": "Kastriert M (2,4,6,8,10)", "f": lambda r: str(r.get('Klasse','')) in ['2','4','6','8','10'] and str(r.get('Geschlecht','')).upper() in ['M','KM','1.0']},
    {"label": "Kastriert W (2,4,6,8,10)", "f": lambda r: str(r.get('Klasse','')) in ['2','4','6','8','10'] and str(r.get('Geschlecht','')).upper() in ['W','F','KW','0.1']},
    {"label": "Junior 8-12 (11)", "f": lambda r: str(r.get('Klasse','')) == '11'},
    {"label": "Kitten 4-8 (12/22)", "f": lambda r: str(r.get('Klasse','')) in ['12', '22']}
]

# --- 6. NAVIGATION (SIDEBAR) ---
st.sidebar.image("https://www.kecb.ch/images/logo.png", width=150) # Optionales Logo
st.sidebar.title("KECB Burgdorf 2026")

st.sidebar.markdown("<div class='nav-header'>Allgemein</div>", unsafe_allow_html=True)
tag = st.sidebar.radio("Ausstellungstag:", ["Tag 1", "Tag 2"])

st.sidebar.markdown("<div class='nav-header'>Öffentliche Ansichten</div>", unsafe_allow_html=True)
view = st.sidebar.radio("Gehe zu:", ["📢 Live-Dashboard", "🏆 Best in Show Grid"])

st.sidebar.markdown("<div class='nav-header'>Interner Bereich</div>", unsafe_allow_html=True)
if st.sidebar.button("📝 Steward-Pult"): view = "Steward"
if st.sidebar.button("👨‍⚖️ Richter-Info"): view = "Richter"
if st.sidebar.button("⚙️ Admin-Konsole"): view = "Admin"

if st.sidebar.button("🔓 Logout"):
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()

# --- 7. DATEN LADEN ---
df_full = load_labels()
r_col = f"Richter {tag}"
df_tag = df_full[df_full[tag].astype(str).str.upper() == 'X'].copy() if df_full is not None else None

# --- 8. VIEWS ---

if view == "📢 Live-Dashboard":
    st.title(f"Live-Aufruf ({tag})")
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

elif view == "🏆 Best in Show Grid":
    st.title("BIS Panel")
    if df_tag is not None:
        judges = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
        html = "<table class='bis-table'><tr><th class='class-header'>Klasse</th>"
        for j in judges: html += f"<th>{j}</th>"
        html += "</tr>"
        for rd in rows_def:
            html += f"<tr><td class='class-header'>{rd['label']}</td>"
            for j in judges:
                cell = ""
                for k, v in store.data.items():
                    if v.get("NOM"):
                        nr, r_n = k.split("|")
                        if r_n == j:
                            match = df_tag[df_tag['KAT_STR'] == nr]
                            if not match.empty and rd['f'](match.iloc[0]):
                                cell += f"<div><p class='bis-nr'>{nr}</p><p class='bis-label'>{get_full_label(match.iloc[0])}</p></div>"
                html += f"<td>{cell}</td>"
            html += "</tr>"
        st.markdown(html + "</table>", unsafe_allow_html=True)

elif view == "Steward":
    if check_auth("steward", "steward2026"):
        st.title("Steward-Pult")
        all_j = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
        mein_richter = st.selectbox("Mein Richter:", ["--"] + all_j)
        if mein_richter != "--":
            df_j = df_tag[df_tag[r_col] == mein_richter].sort_values(['Klasse', 'Katalog-Nr'])
            for _, row in df_j.iterrows():
                nr = row['KAT_STR']; k = f"{nr}|{mein_richter}"
                if k not in store.data: store.data[k] = {"Aufruf": False, "BIV": False, "NOM": False}
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                c1.write(f"**#{nr}** - {get_full_label(row)} (Kl. {row.get('Klasse','')})")
                store.data[k]["Aufruf"] = c2.checkbox("Ruf", value=store.data[k]["Aufruf"], key=f"a{k}")
                store.data[k]["BIV"] = c3.checkbox("BIV", value=store.data[k]["BIV"], key=f"b{k}")
                store.data[k]["NOM"] = c4.checkbox("NOM", value=store.data[k]["NOM"], key=f"n{k}")

elif view == "Richter":
    if check_auth("richter", "richter2026"):
        st.title("Richter-Ansicht")
        all_j = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
        j_sel = st.selectbox("Ich bin:", all_j)
        st.dataframe(df_tag[df_tag[r_col] == j_sel][['Katalog-Nr', 'Rasse_Kurz', 'Farbe', 'Klasse', 'Geschlecht']])

elif view == "Admin":
    if check_auth("admin", "admin2026"):
        st.title("Admin-Zentrale")
        if st.button("🚨 ALLE LIVE-DATEN LÖSCHEN"):
            store.data = {}
            st.success("Daten wurden zurückgesetzt.")
        st.write("Debug-Daten:", store.data)
