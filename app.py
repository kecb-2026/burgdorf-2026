import streamlit as st
import pandas as pd
import re


# Zeigt die aktuelle Netzwerk-URL in der Seitenleiste an (hilfreich für Stewards)
import socket
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
st.sidebar.info(f"Netzwerk-URL: http://{local_ip}:8501")



# --- 1. SETUP & STYLING ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

st.markdown("""
    <style>
    html, body, [class*="ViewContainer"] { font-size: 18px !important; }
    
    /* Dashboard / Display */
    .judge-col { 
        border: 3px solid #1a4a9e; padding: 15px; border-radius: 20px; 
        background-color: #ffffff; min-height: 600px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .judge-col h3 { 
        font-size: 32px !important; color: white; background-color: #1a4a9e;
        padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 20px;
    }
    .cat-card { padding: 15px; border-bottom: 2px solid #f0f0f0; margin-bottom: 15px; text-align: center; }
    .cat-number { 
        font-size: 85px !important; font-weight: 900 !important; 
        color: #1a4a9e; line-height: 0.9; margin-bottom: 2px;
    }
    .cat-info { font-size: 22px; color: #333; margin-bottom: 12px; font-weight: bold; }

    /* Tags & Animation */
    .tag { font-weight: bold; padding: 6px 12px; border-radius: 8px; font-size: 18px; display: inline-block; margin: 4px; }
    .tag-aufruf { background-color: #007bff; color: white; }
    @keyframes blinker { 50% { opacity: 0.1; } }
    .tag-biv { background-color: #28a745; color: white; animation: blinker 1.5s linear infinite; }
    .tag-nom { background-color: #ffc107; color: black; animation: blinker 1s linear infinite; }
    
    /* Steward-Eingabe Styling */
    .judge-section { border: 2px solid #1a4a9e; padding: 15px; border-radius: 12px; background-color: #f0f4fa; margin-bottom: 25px; }
    .judge-title { background-color: #1a4a9e; color: white; padding: 8px 15px; border-radius: 8px; font-size: 26px !important; margin-bottom: 12px; }
    </style>
    """, unsafe_allow_html=True)

# Hilfsfunktionen
def roman_to_numeric(text):
    roman_map = {'IX': '9', 'VIII': '8', 'VII': '7', 'VI': '6', 'IV': '4', 'V': '5', 'III': '3', 'II': '2', 'I': '1'}
    if pd.isna(text): return ""
    res = str(text).upper()
    for rom, num in roman_map.items():
        res = re.sub(rf'\b{rom}\b', num, res)
    return res

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_excel("LABELS.xlsm", engine='openpyxl', header=1)
        df.columns = df.columns.astype(str).str.strip()
        if 'Rasse_Kurz' not in df.columns and 'Rasse' in df.columns:
            df = df.rename(columns={'Rasse': 'Rasse_Kurz'})
        df['Katalog-Nr'] = pd.to_numeric(df['Katalog-Nr'], errors='coerce')
        return df
    except:
        return None

# --- 2. AUTHENTIFIZIERUNG (URL-Memory) ---
if 'auth' not in st.session_state:
    query_params = st.query_params
    if "role" in query_params:
        st.session_state.auth = query_params["role"]
    else:
        st.session_state.auth = None

if st.session_state.auth is None:
    st.title("🔑 Login KECB Burgdorf 2026")
    pw = st.text_input("Passwort", type="password")
    if st.button("Einloggen"):
        role = None
        if pw == "Burgdorf26": role = "admin"
        elif pw == "judge26": role = "richter"
        elif pw == "ring26": role = "steward"
        
        if role:
            st.session_state.auth = role
            st.query_params["role"] = role
            st.rerun()
    st.stop()

if st.sidebar.button("Abmelden"):
    st.session_state.auth = None
    st.query_params.clear()
    st.rerun()

# --- 3. DATEN & LOGIK ---
df_full = load_data()
if 'steward_actions' not in st.session_state: st.session_state.steward_actions = {}

tag = st.sidebar.radio("Tag wählen", ["Tag 1", "Tag 2"])
r_col = "Richter Tag 1" if tag == "Tag 1" else "Richter Tag 2"
df_tag = df_full[df_full[tag].astype(str).str.upper() == 'X'].copy() if df_full is not None else None

if df_tag is not None and r_col in df_tag.columns:
    df_tag = df_tag.sort_values(by=[r_col, 'Kategorie', 'Katalog-Nr'])

# Navigation
menu = ["Dashboard", "Steward-Eingabe"]
if st.session_state.auth == "admin": 
    menu = ["Dashboard", "Steward-Eingabe", "Richter-Votum", "Beamer-Regie"]
elif st.session_state.auth == "richter":
    menu = ["Richter-Votum", "Dashboard"]

view = st.sidebar.radio("Menü", menu)

def get_cat_info(row):
    rasse = row.get('Rasse_Kurz', row.get('Rasse', ''))
    fg = roman_to_numeric(row.get('Farbgruppe', ''))
    farbe = row.get('Farbe', '')
    return f"{rasse} {fg} ({farbe})"

# --- 4. MODUL: DASHBOARD ---
if view == "Dashboard":
    st.title(f"📢 Aufruf & Ring-Status ({tag})")
    if df_tag is not None:
        judges = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
        cols = st.columns(len(judges))
        for i, j in enumerate(judges):
            with cols[i]:
                st.markdown(f"<div class='judge-col'><h3>{j}</h3>", unsafe_allow_html=True)
                active_cats = []
                for (nr, j_name), stat in st.session_state.steward_actions.items():
                    if j_name == j and any(stat.values()):
                        row_data = df_tag[df_tag['Katalog-Nr'] == nr]
                        if not row_data.empty:
                            active_cats.append({'nr': nr, 'stat': stat, 'cat': row_data.iloc[0]['Kategorie'], 'row': row_data.iloc[0]})
                
                active_cats = sorted(active_cats, key=lambda x: (x['cat'], x['nr']))
                for item in active_cats:
                    st.markdown(f"<div class='cat-card'><div class='cat-number'>{int(item['nr'])}</div><div class='cat-info'>{get_cat_info(item['row'])}</div>", unsafe_allow_html=True)
                    tags = ""
                    if item['stat']["Aufruf"]: tags += "<span class='tag tag-aufruf'>AUFRUF</span>"
                    if item['stat']["BIV"]: tags += "<span class='tag tag-biv'>BIV</span>"
                    if item['stat']["NOM"]: tags += "<span class='tag tag-nom'>NOM</span>"
                    st.markdown(tags + "</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

# --- 5. MODUL: STEWARD-EINGABE ---
elif view == "Steward-Eingabe":
    st.title("📝 Steward-Pult")
    if df_tag is not None:
        judges = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
        for j in judges:
            st.markdown(f"<div class='judge-title'>Richter: {j}</div>", unsafe_allow_html=True)
            st.markdown("<div class='judge-section'>", unsafe_allow_html=True)
            df_j = df_tag[df_tag[r_col] == j]
            for c in sorted(df_j['Kategorie'].unique()):
                st.markdown(f"<u>**Kategorie {c}**</u>", unsafe_allow_html=True)
                for _, row in df_j[df_j['Kategorie'] == c].iterrows():
                    nr = row['Katalog-Nr']
                    if pd.isna(nr): continue
                    key = (nr, j)
                    if key not in st.session_state.steward_actions:
                        st.session_state.steward_actions[key] = {"Aufruf": False, "BIV": False, "NOM": False}
                    
                    c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                    with c1: st.write(f"**#{int(nr)} {get_cat_info(row)}**")
                    # Checkboxen
                    st.session_state.steward_actions[key]["Aufruf"] = c2.checkbox("Aufruf", value=st.session_state.steward_actions[key]["Aufruf"], key=f"a{nr}{j}")
                    st.session_state.steward_actions[key]["BIV"] = c3.checkbox("BIV", value=st.session_state.steward_actions[key]["BIV"], key=f"b{nr}{j}")
                    st.session_state.steward_actions[key]["NOM"] = c4.checkbox("NOM", value=st.session_state.steward_actions[key]["NOM"], key=f"n{nr}{j}")
            st.markdown("</div>", unsafe_allow_html=True)
        if st.button("💾 ALLE ÄNDERUNGEN SPEICHERN"):
            st.success("Daten wurden aktualisiert!")
            st.rerun()

# --- 6. WEITERE MODULE ---
elif view == "Richter-Votum":
    st.title("🏆 Richter-Abstimmung")
    mein_name = st.selectbox("Wähle deinen Namen", sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"]))
    nom_fuer_mich = [nr for (nr, j_name), stat in st.session_state.steward_actions.items() if j_name == mein_name and stat["NOM"]]
    if nom_fuer_mich:
        for nr in nom_fuer_mich:
            row_info = df_tag[df_tag['Katalog-Nr'] == nr].iloc[0]
            st.info(f"Nominiert: {int(nr)} ({get_cat_info(row_info)})")
            st.text_input(f"Votum für {int(nr)}", key=f"v_{mein_name}_{nr}")
    else: st.write("Keine Nominationen vorhanden.")

elif view == "Beamer-Regie":
    st.title("🎬 Beamer-Regie")
    # Hier können später die Auswertungen der Richterstimmen angezeigt werden
    st.write("Warte auf Abstimmungs-Ergebnisse...")
