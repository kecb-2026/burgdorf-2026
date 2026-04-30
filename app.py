import streamlit as st
import pandas as pd
import re

# --- 1. SETUP & STYLING ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

st.markdown("""
    <style>
    html, body, [class*="ViewContainer"] { font-size: 18px !important; }
    
    /* Dashboard Spalten-Design */
    .judge-col { 
        border: 3px solid #1a4a9e; 
        padding: 15px; 
        border-radius: 20px; 
        background-color: #ffffff; 
        min-height: 600px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .judge-col h3 { 
        font-size: 32px !important; 
        color: white; 
        background-color: #1a4a9e;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    
    .cat-card {
        padding: 15px;
        border-bottom: 2px solid #f0f0f0;
        margin-bottom: 15px;
        text-align: center;
    }
    
    .cat-number { 
        font-size: 85px !important; 
        font-weight: 900 !important; 
        color: #1a4a9e; 
        line-height: 0.9;
        margin-bottom: 2px;
    }
    
    .cat-info { font-size: 22px; color: #333; margin-bottom: 12px; font-weight: bold; }

    /* Tags & Animation */
    .tag { font-weight: bold; padding: 6px 12px; border-radius: 8px; font-size: 18px; display: inline-block; margin: 4px; }
    .tag-aufruf { background-color: #007bff; color: white; }
    
    /* Blink-Effekt für BIV und NOM */
    @keyframes blinker {  
        50% { opacity: 0.1; }
    }
    .tag-biv { background-color: #28a745; color: white; animation: blinker 1.5s linear infinite; }
    .tag-nom { background-color: #ffc107; color: black; animation: blinker 1s linear infinite; }
    
    .winner-box { text-align: center; border: 10px solid #1a4a9e; padding: 30px; background-color: white; border-radius: 40px; }
    .stCheckbox label { font-size: 20px !important; font-weight: bold !important; }
    .judge-section { border: 2px solid #1a4a9e; padding: 15px; border-radius: 12px; background-color: #f0f4fa; margin-bottom: 25px; }
    .judge-title { background-color: #1a4a9e; color: white; padding: 8px 15px; border-radius: 8px; font-size: 26px !important; margin-bottom: 12px; }
    </style>
    """, unsafe_allow_html=True)

def roman_to_numeric(text):
    roman_map = {'IX': '9', 'VIII': '8', 'VII': '7', 'VI': '6', 'IV': '4', 'V': '5', 'III': '3', 'II': '2', 'I': '1'}
    if pd.isna(text): return ""
    res = str(text).upper()
    for rom, num in roman_map.items():
        res = re.sub(rf'\b{rom}\b', num, res)
    return res

# --- 2. DATEN LADEN ---
@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_excel("LABELS.xlsm", engine='openpyxl', header=1)
        df.columns = df.columns.astype(str).str.strip()
        if 'Rasse_Kurz' not in df.columns and 'Rasse' in df.columns:
            df = df.rename(columns={'Rasse': 'Rasse_Kurz'})
        df['Katalog-Nr'] = pd.to_numeric(df['Katalog-Nr'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Fehler beim Laden: {e}")
        return None

df_full = load_data()

# --- 3. SESSION STATES ---
if 'steward_actions' not in st.session_state: st.session_state.steward_actions = {}
if 'sieger_id' not in st.session_state: st.session_state.sieger_id = None
if 'auth' not in st.session_state: st.session_state.auth = None

# --- 4. LOGIN ---
if st.session_state.auth is None:
    pw = st.text_input("Passwort", type="password")
    if st.button("Login"):
        if pw == "Burgdorf26": st.session_state.auth = "admin"
        elif pw == "ring26": st.session_state.auth = "steward"
        st.rerun()
    st.stop()

# --- 5. TAGES-FILTER ---
tag = st.sidebar.radio("Tag", ["Tag 1", "Tag 2"])
r_col = "Richter Tag 1" if tag == "Tag 1" else "Richter Tag 2"
df_tag = df_full[df_full[tag].astype(str).str.upper() == 'X'].copy() if df_full is not None else None

if df_tag is not None and r_col in df_tag.columns:
    df_tag = df_tag.sort_values(by=[r_col, 'Kategorie', 'Katalog-Nr'])

# --- 6. NAVIGATION ---
menu = ["Dashboard", "Steward-Eingabe", "Richter-Votum", "Beamer-Regie"]
if st.session_state.auth == "steward": menu = ["Steward-Eingabe", "Dashboard"]
view = st.sidebar.radio("Menü", menu)

def get_cat_info(row):
    rasse = row.get('Rasse_Kurz', row.get('Rasse', ''))
    fg = roman_to_numeric(row.get('Farbgruppe', ''))
    farbe = row.get('Farbe', '')
    return f"{rasse} {fg} ({farbe})"

# --- MODULE ---

if view == "Dashboard":
    st.title(f"📢 Aufruf & Ring-Status ({tag})")
    if df_tag is not None and r_col in df_tag.columns:
        judges = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
        cols = st.columns(len(judges))
        
        for i, j in enumerate(judges):
            with cols[i]:
                st.markdown(f"<div class='judge-col'><h3>{j}</h3>", unsafe_allow_html=True)
                
                # Sammeln und Sortieren der aktiven Katzen
                active_cats = []
                for (nr, j_name), stat in st.session_state.steward_actions.items():
                    if j_name == j and any(stat.values()):
                        row_data = df_tag[df_tag['Katalog-Nr'] == nr]
                        if not row_data.empty:
                            active_cats.append({'nr': nr, 'stat': stat, 'cat': row_data.iloc[0]['Kategorie'], 'row': row_data.iloc[0]})
                
                active_cats = sorted(active_cats, key=lambda x: (x['cat'], x['nr']))
                
                for item in active_cats:
                    nr, stat, row_info = item['nr'], item['stat'], item['row']
                    
                    st.markdown(f"""
                        <div class='cat-card'>
                            <div class='cat-number'>{int(nr)}</div>
                            <div class='cat-info'>{get_cat_info(row_info)}</div>
                        """, unsafe_allow_html=True)
                    
                    tags_html = ""
                    if stat["Aufruf"]: tags_html += "<span class='tag tag-aufruf'>AUFRUF</span>"
                    if stat["BIV"]: tags_html += "<span class='tag tag-biv'>BIV</span>"
                    if stat["NOM"]: tags_html += "<span class='tag tag-nom'>NOM</span>"
                    
                    st.markdown(tags_html + "</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

elif view == "Steward-Eingabe":
    st.title("Steward-Pult")
    # ... (Steward-Eingabe Logik bleibt identisch zum vorherigen Stand)
    # [Hier den Code der Steward-Eingabe einfügen]
