import streamlit as st
import pandas as pd
import re
import json
import os

# --- 1. SETUP & DATEN-SICHERUNG ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

DATA_FILE = "steward_data.json"

def save_json(data):
    # Speichert alles als String-Keys, um JSON-Probleme zu vermeiden
    serializable = {f"{k[0]}|{k[1]}": v for k, v in data.items()}
    with open(DATA_FILE, "w") as f:
        json.dump(serializable, f)

def load_json():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                raw = json.load(f)
                # Wandelt "123|Name" zurück in ("123", "Name")
                return {tuple(k.split("|")): v for k, v in raw.items()}
        except: return {}
    return {}

# --- 2. STYLING ---
st.markdown("""
    <style>
    .judge-col { border: 3px solid #1a4a9e; padding: 15px; border-radius: 20px; background-color: #ffffff; min-height: 700px; margin-bottom: 20px; }
    .judge-col h3 { font-size: 32px !important; color: white; background-color: #1a4a9e; padding: 10px; border-radius: 10px; text-align: center; }
    
    .cat-card { padding: 15px; border-bottom: 2px solid #f0f0f0; margin-bottom: 10px; text-align: center; background-color: #fafafa; border-radius: 10px; }
    .cat-number { font-size: 90px !important; font-weight: 900 !important; color: #1a4a9e; line-height: 0.8; }
    .cat-info { font-size: 22px; color: #333; font-weight: bold; margin-top: 5px; }
    .cat-kategorie { font-size: 18px; color: #666; font-style: italic; }

    .tag { font-weight: bold; padding: 6px 12px; border-radius: 8px; font-size: 18px; display: inline-block; margin: 4px; }
    .tag-aufruf { background-color: #007bff; color: white; }
    @keyframes blinker { 50% { opacity: 0.2; } }
    .tag-biv { background-color: #28a745; color: white; animation: blinker 1.5s linear infinite; }
    .tag-nom { background-color: #ffc107; color: black; animation: blinker 1s linear infinite; }
    
    .judge-section { border: 2px solid #1a4a9e; padding: 15px; border-radius: 12px; background-color: #f0f4fa; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

# Hilfsfunktionen
def roman_to_numeric(text):
    roman_map = {'IX': '9', 'VIII': '8', 'VII': '7', 'VI': '6', 'IV': '4', 'V': '5', 'III': '3', 'II': '2', 'I': '1'}
    if pd.isna(text) or text == "": return ""
    res = str(text).upper()
    for rom, num in roman_map.items():
        res = re.sub(rf'\b{rom}\b', num, res)
    return res

@st.cache_data(ttl=5)
def load_excel():
    try:
        df = pd.read_excel("LABELS.xlsm", engine='openpyxl', header=1)
        df.columns = df.columns.astype(str).str.strip()
        if 'Rasse_Kurz' not in df.columns: df.rename(columns={'Rasse': 'Rasse_Kurz'}, inplace=True)
        # Katalog-Nr als String behandeln für stabilen JSON-Vergleich
        df['Katalog-Nr-Str'] = df['Katalog-Nr'].astype(str).str.replace('.0', '', regex=False)
        return df
    except: return None

# --- 3. LOGIN ---
if 'auth' not in st.session_state:
    st.session_state.auth = st.query_params.get("role")

if not st.session_state.auth:
    st.title("🔑 KECB Login")
    pw = st.text_input("Passwort", type="password")
    if st.button("Login"):
        role = {"Burgdorf26": "admin", "judge26": "richter", "ring26": "steward"}.get(pw)
        if role:
            st.session_state.auth = role
            st.query_params["role"] = role
            st.rerun()
    st.stop()

# --- 4. DATEN INITIALISIEREN ---
df_full = load_excel()
if 'steward_actions' not in st.session_state:
    st.session_state.steward_actions = load_json()

tag = st.sidebar.radio("Tag", ["Tag 1", "Tag 2"])
r_col = f"Richter {tag}"
df_tag = df_full[df_full[tag].astype(str).str.upper() == 'X'].copy() if df_full is not None else None

# Menü
menu = ["Dashboard", "Steward-Eingabe", "Richter-Votum", "Beamer-Regie"]
if st.session_state.auth == "steward": menu = ["Steward-Eingabe", "Dashboard"]
elif st.session_state.auth == "richter": menu = ["Richter-Votum", "Dashboard"]
view = st.sidebar.radio("Navigation", menu)

def get_cat_info_complete(row):
    rasse = row.get('Rasse_Kurz', '')
    # Farbgruppe römisch zu numerisch wandeln
    fg = roman_to_numeric(row.get('Farbgruppe', ''))
    ems = row.get('Farbe', '') # EMS Code
    return f"{rasse} {fg} ({ems})"

# --- 5. DASHBOARD ---
if view == "Dashboard":
    st.title(f"📢 Live-Aufruf ({tag})")
    if df_tag is not None:
        judges = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
        cols = st.columns(len(judges))
        for i, j in enumerate(judges):
            with cols[i]:
                st.markdown(f"<div class='judge-col'><h3>{j}</h3>", unsafe_allow_html=True)
                
                # Filtere alle Katzen für diesen Richter, die mindestens einen Status aktiv haben
                active_list = []
                for (nr_str, j_name), stat in st.session_state.steward_actions.items():
                    if j_name == j and any(stat.values()):
                        match = df_tag[df_tag['Katalog-Nr-Str'] == nr_str]
                        if not match.empty:
                            active_list.append({'row': match.iloc[0], 'stat': stat, 'nr': nr_str})
                
                # Sortierung nach Kategorie (numerisch) und dann Katalog-Nr
                active_list = sorted(active_list, key=lambda x: (x['row'].get('Kategorie', 99), int(x['nr'])))
                
                for item in active_list:
                    r = item['row']
                    kat_text = f"Kategorie {r.get('Kategorie', '')}"
                    st.markdown(f"""
                        <div class='cat-card'>
                            <div class='cat-kategorie'>{kat_text}</div>
                            <div class='cat-number'>{item['nr']}</div>
                            <div class='cat-info'>{get_cat_info_complete(r)}</div>
                        """, unsafe_allow_html=True)
                    tags = "".join([f"<span class='tag tag-{t.lower()}'>{t}</span>" for t, val in item['stat'].items() if val])
                    st.markdown(tags + "</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

# --- 6. STEWARD-EINGABE ---
elif view == "Steward-Eingabe":
    st.title("📝 Steward-Pult")
    if df_tag is not None:
        for j in sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"]):
            with st.expander(f"Richter: {j}", expanded=True):
                st.markdown("<div class='judge-section'>", unsafe_allow_html=True)
                df_j = df_tag[df_tag[r_col] == j].sort_values(['Kategorie', 'Katalog-Nr'])
                for _, row in df_j.iterrows():
                    nr_str = row['Katalog-Nr-Str']
                    key = (nr_str, j)
                    if key not in st.session_state.steward_actions:
                        st.session_state.steward_actions[key] = {"Aufruf": False, "BIV": False, "NOM": False}
                    
                    c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                    c1.write(f"**#{nr_str}** Kat.{row.get('Kategorie','')} - {get_cat_info_complete(row)}")
                    
                    # Checkboxen direkt in den State schreiben
                    st.session_state.steward_actions[key]["Aufruf"] = c2.checkbox("Ruf", value=st.session_state.steward_actions[key]["Aufruf"], key=f"a{nr_str}{j}")
                    st.session_state.steward_actions[key]["BIV"] = c3.checkbox("BIV", value=st.session_state.steward_actions[key]["BIV"], key=f"b{nr_str}{j}")
                    st.session_state.steward_actions[key]["NOM"] = c4.checkbox("NOM", value=st.session_state.steward_actions[key]["NOM"], key=f"n{nr_str}{j}")
                st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("💾 ALLE ÄNDERUNGEN SPEICHERN"):
            save_json(st.session_state.steward_actions)
            st.success("Gespeichert!")
            st.rerun()

# --- 7. RICHTER & BEAMER (identisch) ---
elif view == "Richter-Votum":
    st.title("🏆 Votum")
    st.write("Hier können Richter ihre Wahl treffen (basierend auf den NOM-Katzen).")

elif view == "Beamer-Regie":
    st.title("🎬 Beamer")
    st.write("Anzeige für Best in Show.")
