import streamlit as st
import pandas as pd
from collections import Counter

# --- 1. SETUP & STYLING (Bleibt bestehen) ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

st.markdown("""
    <style>
    html, body, [class*="ViewContainer"] { font-size: 24px !important; }
    .judge-col { border: 4px solid #1a4a9e; padding: 15px; border-radius: 20px; background-color: #ffffff; min-height: 450px; }
    .judge-col h3 { font-size: 40px !important; color: #1a4a9e; text-align: center; border-bottom: 2px solid #eee; }
    
    .tag-aufruf { background-color: #007bff; color: white; padding: 4px 10px; border-radius: 8px; font-weight: bold; font-size: 20px; }
    .tag-biv { background-color: #28a745; color: white; padding: 4px 10px; border-radius: 8px; font-weight: bold; font-size: 20px; }
    .tag-nom { background-color: #ffc107; color: black; padding: 4px 10px; border-radius: 8px; font-weight: bold; font-size: 20px; }
    
    .winner-box { text-align: center; border: 15px solid #1a4a9e; padding: 40px; background-color: white; border-radius: 50px; }
    .stCheckbox label { font-size: 28px !important; font-weight: bold !important; }
    
    /* Styling für die Richter-Sektionen in der Eingabe */
    .judge-section { border: 3px solid #1a4a9e; padding: 20px; border-radius: 15px; background-color: #f0f4fa; margin-bottom: 30px; }
    .judge-title { background-color: #1a4a9e; color: white; padding: 10px 20px; border-radius: 10px; font-size: 35px !important; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATEN LADEN (Header & Sortierung integriert) ---
@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_excel("LABELS.xlsm", engine='openpyxl', header=1)
        df.columns = df.columns.astype(str).str.strip()
        # Numerische Konvertierung für korrekte Sortierung der Nummern
        df['Katalog-Nr'] = pd.to_numeric(df['Katalog-Nr'], errors='coerce')
        return df
    except:
        return None

df_full = load_data()

# --- 3. SESSION STATES ---
if 'steward_actions' not in st.session_state: st.session_state.steward_actions = {}
if 'judge_votes' not in st.session_state: st.session_state.judge_votes = {}
if 'sieger_id' not in st.session_state: st.session_state.sieger_id = None
if 'auth' not in st.session_state: st.session_state.auth = None

# --- 4. LOGIN ---
if st.session_state.auth is None:
    pw = st.text_input("Passwort", type="password")
    if st.button("Login"):
        if pw == "Burgdorf26": st.session_state.auth = "admin"
        elif pw == "judge26": st.session_state.auth = "richter"
        elif pw == "ring26": st.session_state.auth = "steward"
        st.rerun()
    st.stop()

# --- 5. TAGES-FILTER & SORTIER-LOGIK ---
tag = st.sidebar.radio("Tag", ["Tag 1", "Tag 2"])
r_col = "Richter Tag 1" if tag == "Tag 1" else "Richter Tag 2"
df_tag = df_full[df_full[tag].astype(str).str.upper() == 'X'].copy() if df_full is not None else None

# Hier wird die verlangte Sortierung angewendet: Richter -> Kategorie -> Nummer
if df_tag is not None:
    df_tag = df_tag.sort_values(by=[r_col, 'Kategorie', 'Katalog-Nr'])

# --- 6. NAVIGATION ---
if st.session_state.auth == "admin":
    menu = ["Dashboard", "Steward-Eingabe", "Richter-Votum", "Beamer-Regie"]
elif st.session_state.auth == "richter":
    menu = ["Richter-Votum", "Dashboard"]
else:
    menu = ["Steward-Eingabe", "Dashboard"]

view = st.sidebar.radio("Menü", menu)

# --- MODUL: DASHBOARD (Aufstellung in Spalten) ---
if view == "Dashboard":
    st.title(f"Ring-Status {tag}")
    judges = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
    cols = st.columns(len(judges))
    
    for i, j in enumerate(judges):
        with cols[i]:
            st.markdown(f"<div class='judge-col'><h3>{j}</h3>", unsafe_allow_html=True)
            active = [(nr, stat) for (nr, j_name), stat in st.session_state.steward_actions.items() 
                      if j_name == j and any(stat.values())]
            for nr, stat in active:
                st.write(f"**Nr. {int(nr)}**")
                if stat["Aufruf"]: st.markdown("<span class='tag-aufruf'>AUFRUF</span>", unsafe_allow_html=True)
                if stat["BIV"]: st.markdown("<span class='tag-biv'>BIV</span>", unsafe_allow_html=True)
                if stat["NOM"]: st.markdown("<span class='tag-nom'>NOM</span>", unsafe_allow_html=True)
                st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# --- MODUL: STEWARD-EINGABE (Sortiert nach Richter, Kat, Nr) ---
elif view == "Steward-Eingabe":
    st.title("Steward-Pult")
    judges = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
    
    for j in judges:
        st.markdown(f"<div class='judge-title'>Richter: {j}</div>", unsafe_allow_html=True)
        st.markdown("<div class='judge-section'>", unsafe_allow_html=True)
        
        df_judge = df_tag[df_tag[r_col] == j]
        cats = sorted([c for c in df_judge['Kategorie'].unique() if str(c) != "nan"])
        
        for c in cats:
            st.markdown(f"<u>**Kategorie {c}**</u>", unsafe_allow_html=True)
            df_cat = df_judge[df_judge['Kategorie'] == c]
            
            for _, row in df_cat.iterrows():
                nr = row['Katalog-Nr']
                if pd.isna(nr): continue
                key = (nr, j)
                
                if key not in st.session_state.steward_actions:
                    st.session_state.steward_actions[key] = {"Aufruf": False, "BIV": False, "NOM": False}
                
                c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
                with c1: st.write(f"**#{int(nr)}**")
                with c2: st.session_state.steward_actions[key]["Aufruf"] = st.checkbox("Aufruf", value=st.session_state.steward_actions[key]["Aufruf"], key=f"a{nr}{j}")
                with c3: st.session_state.steward_actions[key]["BIV"] = st.checkbox("BIV", value=st.session_state.steward_actions[key]["BIV"], key=f"b{nr}{j}")
                with c4: st.session_state.steward_actions[key]["NOM"] = st.checkbox("NOM", value=st.session_state.steward_actions[key]["NOM"], key=f"n{nr}{j}")
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("ALLE ÄNDERUNGEN SPEICHERN"):
        st.rerun()

# --- RESTLICHE MODULE (Votum & Regie bleiben identisch) ---
elif view == "Richter-Votum":
    st.title("Richter-Abstimmung")
    mein_name = st.selectbox("Mein Name", sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"]))
    nom_fuer_mich = [nr for (nr, j_name), stat in st.session_state.steward_actions.items() if j_name == mein_name and stat["NOM"]]
    if nom_fuer_mich:
        for nr in nom_fuer_mich:
            st.info(f"Nominiert: Katze Nr. {int(nr)}")
            st.session_state.judge_votes[(nr, mein_name)] = st.text_input(f"Votum für {int(nr)}", key=f"v_{mein_name}_{nr}")
    else: st.write("Keine Nominationen.")

elif view == "Beamer-Regie":
    st.title("Regie & Beamer")
    nom_gesamt = list(set([nr for (nr, j), stat in st.session_state.steward_actions.items() if stat["NOM"]]))
    choice = st.selectbox("Sieger wählen", ["-"] + sorted(nom_gesamt))
    if st.button("Sieg anzeigen") and choice != "-":
        st.session_state.sieger_id = choice
        st.rerun()
    if st.session_state.sieger_id:
        res = df_tag[df_tag['Katalog-Nr'] == st.session_state.sieger_id].iloc[0]
        st.markdown(f"<div class='winner-box'><h1>{int(res['Katalog-Nr'])}</h1><h2>{res['Name']}</h2></div>", unsafe_allow_html=True)
        if st.button("Reset"): st.session_state.sieger_id = None; st.rerun()
