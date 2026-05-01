import streamlit as st
import pandas as pd
import re

# --- 1. SETUP & STYLING ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

st.markdown("""
    <style>
    /* Home Buttons */
    .stButton button { width: 100%; height: 100px; font-size: 24px !important; font-weight: bold !important; border-radius: 15px !important; margin-bottom: 20px; border: 2px solid #1a4a9e !important; }
    
    /* Dashboard Cards */
    .judge-col { border: 3px solid #1a4a9e; padding: 15px; border-radius: 20px; background-color: #ffffff; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .judge-col h3 { font-size: 32px !important; color: white; background-color: #1a4a9e; padding: 10px; border-radius: 10px; text-align: center; }
    
    .cat-card { 
        padding: 20px; border: 1px solid #e0e0e0; margin-bottom: 25px; text-align: center; 
        background-color: #ffffff; border-radius: 20px; box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
    }
    .cat-number { font-size: 110px !important; font-weight: 900 !important; color: #1a4a9e; line-height: 0.8; margin: 10px 0; }
    .cat-label { font-size: 26px; color: #333; font-weight: bold; margin: 5px 0 15px 0; }
    
    /* Tags */
    .tag-container { margin-top: 10px; display: flex; justify-content: center; flex-wrap: wrap; gap: 10px; }
    .tag { font-weight: bold; padding: 10px 20px; border-radius: 10px; font-size: 22px; display: inline-block; }
    .tag-aufruf { background-color: #007bff; color: white; }
    @keyframes blinker { 50% { opacity: 0.2; } }
    .tag-biv { background-color: #28a745; color: white; animation: blinker 1.5s linear infinite; }
    .tag-nom { background-color: #ffc107; color: black; animation: blinker 1s linear infinite; }

    /* Steward Modul Optimierung */
    .steward-row { 
        padding: 15px; border-radius: 10px; margin-bottom: 10px; 
        border: 1px solid #ddd; background-color: #f9f9f9;
        display: flex; align-items: center;
    }
    .steward-row:nth-child(even) { background-color: #ffffff; }
    .steward-info { font-size: 18px; border-right: 2px solid #eee; padding-right: 15px; }
    .steward-check { text-align: center; }

    /* Best in Show Grid */
    .bis-table { width: 100%; border-collapse: collapse; margin-bottom: 30px; table-layout: fixed; background: white; }
    .bis-table th, .bis-table td { border: 2px solid #1a4a9e; padding: 5px; text-align: center; vertical-align: middle; min-height: 100px; }
    .bis-table th { background-color: #1a4a9e; color: white; font-size: 18px; }
    .class-header { background-color: #f0f0f0 !important; font-weight: bold; text-align: left !important; width: 180px; color: #1a4a9e; }
    .bis-nr { font-size: 48px !important; font-weight: 900 !important; color: #000; margin: 0; line-height: 1; }
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

@st.cache_data(ttl=30)
def load_labels():
    try:
        df = pd.read_excel("LABELS.xlsm", engine='openpyxl', header=1)
        df.columns = df.columns.astype(str).str.strip()
        df['KAT_STR'] = df['Katalog-Nr'].astype(str).str.replace('.0', '', regex=False)
        return df
    except Exception as e:
        st.error(f"Fehler beim Laden der Excel: {e}")
        return None

def get_full_label(row):
    r = row.get('Rasse_Kurz', row.get('Rasse', ''))
    g = roman_to_numeric(row.get('Farbgruppe', ''))
    e = row.get('Farbe', '')
    label = f"{r} {g}".strip()
    if pd.notna(e) and e != "": label += f" ({e})"
    return label

# --- 4. KLASSEN LOGIK ---
rows_def = [
    {"label": "Adult M (1,3,5,7,9)", "f": lambda r: str(r.get('Klasse','')) in ['1','3','5','7','9'] and str(r.get('Geschlecht','')).upper() in ['M','1.0']},
    {"label": "Adult W (1,3,5,7,9)", "f": lambda r: str(r.get('Klasse','')) in ['1','3','5','7','9'] and str(r.get('Geschlecht','')).upper() in ['W','F','0.1']},
    {"label": "Kastriert M (2,4,6,8,10)", "f": lambda r: str(r.get('Klasse','')) in ['2','4','6','8','10'] and str(r.get('Geschlecht','')).upper() in ['M','KM','1.0']},
    {"label": "Kastriert W (2,4,6,8,10)", "f": lambda r: str(r.get('Klasse','')) in ['2','4','6','8','10'] and str(r.get('Geschlecht','')).upper() in ['W','F','KW','0.1']},
    {"label": "Junior 11 (8-12)", "f": lambda r: str(r.get('Klasse','')) == '11'},
    {"label": "Kitten 12 (4-8)", "f": lambda r: str(r.get('Klasse','')) == '12'}
]

def set_view(name):
    st.session_state.view = name
    st.rerun()

# --- 5. VIEWS ---

if st.session_state.view == "Home":
    st.title("🐾 KECB Burgdorf 2026")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📢 LIVE-DASHBOARD"): set_view("Dashboard")
        if st.button("🏆 BEST IN SHOW GRID"): set_view("BIS_Grid")
    with col2:
        if st.button("📝 STEWARD-PULT"): set_view("Steward_Login")
        if st.button("👨‍⚖️ RICHTER / ⚙️ ADMIN"): set_view("Admin_Login")

elif "Login" in st.session_state.view:
    st.title(f"🔒 Login")
    pwd = st.text_input("Passwort", type="password")
    if st.button("Anmelden"):
        if "Steward" in st.session_state.view and pwd == "steward2026": set_view("Steward_Panel")
        elif "Admin" in st.session_state.view:
            if pwd == "admin2026": set_view("Admin_Panel")
            elif pwd == "richter2026": set_view("Richter_Panel")
        else: st.error("Passwort falsch")
    if st.button("Abbrechen"): set_view("Home")

else:
    st.sidebar.title("KECB 2026")
    tag = st.sidebar.radio("Tag:", ["Tag 1", "Tag 2"])
    df_full = load_labels()
    r_col = f"Richter {tag}"
    df_tag = df_full[df_full[tag].astype(str).str.upper() == 'X'].copy() if df_full is not None else None
    
    if st.sidebar.button("🏠 Logout"): set_view("Home")

    if st.session_state.view == "Dashboard":
        cat_options = sorted(df_tag['Kategorie'].unique().tolist()) if df_tag is not None else [1,2,3,4]
        cat_filter = st.sidebar.multiselect("Kategorien filtern:", cat_options, default=cat_options)
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
                            m = df_tag[(df_tag['KAT_STR'] == nr) & (df_tag['Kategorie'].isin(cat_filter))]
                            if not m.empty:
                                row = m.iloc[0]
                                card_html = f"<div class='cat-card'><div class='cat-number'>{nr}</div><div class='cat-label'>{get_full_label(row)}</div><div class='tag-container'>"
                                if v.get("Aufruf"): card_html += "<span class='tag tag-aufruf'>AUFRUF</span>"
                                if v.get("BIV"): card_html += "<span class='tag tag-biv'>BIV</span>"
                                if v.get("NOM"): card_html += "<span class='tag tag-nom'>NOM</span>"
                                st.markdown(card_html + "</div></div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.view == "BIS_Grid":
        st.title("Best in Show Grid")
        cat_list = sorted(df_tag['Kategorie'].unique().tolist()) if df_tag is not None else []
        for cat in cat_list:
            st.subheader(f"Kategorie {cat}")
            judges_cat = sorted([r for r in df_tag[df_tag['Kategorie'] == cat][r_col].unique() if str(r) != "nan"])
            if not judges_cat: continue
            html = "<table class='bis-table'><tr><th class='class-header'>Klasse</th>"
            for j in judges_cat: html += f"<th>{j}</th>"
            html += "</tr>"
            for rd in rows_def:
                html += f"<tr><td class='class-header'>{rd['label']}</td>"
                for j in judges_cat:
                    cell = ""
                    for k, v in store.data.items():
                        if v.get("NOM"):
                            nr, r_n = k.split("|")
                            if r_n == j:
                                match = df_tag[(df_tag['KAT_STR'] == nr) & (df_tag['Kategorie'] == cat)]
                                if not match.empty and rd['f'](match.iloc[0]):
                                    cell += f"<div><p class='bis-nr'>{nr}</p><small>{get_full_label(match.iloc[0])}</small></div>"
                    html += f"<td>{cell}</td>"
                html += "</tr>"
            st.markdown(html + "</table>", unsafe_allow_html=True)

    elif st.session_state.view == "Steward_Panel":
        st.title("Steward-Steuerung")
        all_j = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
        mein_richter = st.selectbox("Richter wählen:", ["--"] + all_j)
        
        if mein_richter != "--":
            # Header Zeile für die Checkboxen
            h1, h2, h3, h4 = st.columns([3, 1, 1, 1])
            h1.write("**Katze / Info**")
            h2.write("**AUFRUF**")
            h3.write("**BIV**")
            h4.write("**NOM**")
            st.markdown("---")
            
            df_j = df_tag[df_tag[r_col] == mein_richter].sort_values(['Kategorie', 'Katalog-Nr'])
            
            for _, row in df_j.iterrows():
                nr = row['KAT_STR']
                k = f"{nr}|{mein_richter}"
                if k not in store.data: 
                    store.data[k] = {"Aufruf": False, "BIV": False, "NOM": False}
                
                # Jede Katze in einem Container (für optische Trennung)
                with st.container():
                    c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                    
                    # Info-Spalte
                    c1.markdown(f"""
                        <div style="background-color:#eee; padding:10px; border-radius:5px; border-left:5px solid #1a4a9e;">
                            <span style="font-size:24px; font-weight:bold;">#{nr}</span><br>
                            <span style="font-size:14px;">Cat {row.get('Kategorie','?')}: {get_full_label(row)}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Checkboxen (zentriert durch Spalten-Layout)
                    store.data[k]["Aufruf"] = c2.checkbox("Ruf", value=store.data[k]["Aufruf"], key=f"a{k}", label_visibility="collapsed")
                    store.data[k]["BIV"] = c3.checkbox("BIV", value=store.data[k]["BIV"], key=f"b{k}", label_visibility="collapsed")
                    store.data[k]["NOM"] = c4.checkbox("NOM", value=store.data[k]["NOM"], key=f"n{k}", label_visibility="collapsed")
                    
                    st.markdown("<hr style='margin: 5px 0; border:0; border-top:1px solid #eee;'>", unsafe_allow_html=True)

    elif st.session_state.view == "Admin_Panel":
        st.title("Admin")
        if st.button("🔴 ALLE DATEN RESET"):
            store.data = {}
            st.rerun()

    elif st.session_state.view == "Richter_Panel":
        st.title("Richter-Vorschau")
        all_j = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
        j_sel = st.selectbox("Wähle Richter:", all_j)
        df_j = df_tag[df_tag[r_col] == j_sel].sort_values(['Kategorie', 'Katalog-Nr'])
        st.table(df_j[['Katalog-Nr', 'Kategorie', 'Rasse_Kurz', 'Klasse']])
