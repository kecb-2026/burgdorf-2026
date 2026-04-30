import streamlit as st
import pandas as pd

# --- 1. SETUP ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

st.markdown("""
    <style>
    .stCheckbox { background-color: #f0f2f6; padding: 5px; border-radius: 5px; margin-bottom: 2px; }
    .judge-col { border: 2px solid #1a4a9e; padding: 15px; border-radius: 15px; background-color: #ffffff; min-height: 400px; }
    .cat-card { padding: 10px; border-bottom: 1px solid #eee; font-size: 14px; }
    .status-tag { font-weight: bold; color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATEN LADEN ---
@st.cache_data(ttl=10)
def load_data():
    try:
        # Header ist in Zeile 2 (Index 1)
        df = pd.read_excel("LABELS.xlsm", engine='openpyxl', header=1)
        df.columns = df.columns.astype(str).str.strip()
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Excel-Fehler: {e}")
        return None

df_full = load_data()

# --- 3. LOGIN ---
if 'auth' not in st.session_state: st.session_state.auth = None
if st.session_state.auth is None:
    pw = st.text_input("Passwort", type="password")
    if st.button("Anmelden"):
        if pw == "ring26": st.session_state.auth = "steward"
        elif pw == "Burgdorf26": st.session_state.auth = "admin"
        elif pw == "hallenaufl": st.session_state.auth = "monitor"
        st.rerun()
    st.stop()

# --- 4. TAGES-FILTER ---
selected_tag = st.sidebar.radio("Tag wählen", ["Tag 1", "Tag 2"])
tag_col = selected_tag
df_tag = df_full[df_full[tag_col].str.upper() == 'X'].copy()

# Live-Status Speicher (wer ist gerade aufgerufen/BIV/NOM)
if 'steward_actions' not in st.session_state:
    st.session_state.steward_actions = {} 

# --- 5. STEWARD-PANEL ---
st.title(f"📋 Steward-Management ({selected_tag})")

# Gruppen nach Kategorien
categories = sorted([c for c in df_tag['Kategorie'].unique() if c != "nan"])
richter_col_name = "Richter Tag 1" if selected_tag == "Tag 1" else "Richter Tag 2"
all_judges = sorted([r for r in df_tag[richter_col_name].unique() if r != "nan"])

# --- ANZEIGE DER RICHTER-SPALTEN (Dashboard) ---
st.subheader("Aktueller Status in den Ringen")
judge_cols = st.columns(len(all_judges))

for i, judge in enumerate(all_judges):
    with judge_cols[i]:
        st.markdown(f"<div class='judge-col'><h3>{judge}</h3>", unsafe_allow_html=True)
        # Zeige nur Katzen, die für diesen Richter aktiviert wurden
        active_for_judge = [
            (nr, status) for (nr, j_name), status in st.session_state.steward_actions.items() 
            if j_name == judge and any(status.values())
        ]
        if not active_for_judge:
            st.write("Keine aktiven Aufrufe")
        for nr, status in active_for_judge:
            tags = [k for k, v in status.items() if v]
            st.markdown(f"<div class='cat-card'><b>Nr. {nr}</b>: <span class='status-tag'>{', '.join(tags)}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# --- EINGABE-BEREICH FÜR STEWARDS ---
st.subheader("Katzen verwalten (Checkboxes)")

for cat_name in categories:
    with st.expander(f"Kategorie {cat_name}", expanded=True):
        df_cat = df_tag[df_tag['Kategorie'] == cat_name].sort_values('Katalog-Nr')
        
        # Tabellarische Ansicht für Checkboxen
        for _, row in df_cat.iterrows():
            nr = row['Katalog-Nr']
            r_name = row[richter_col_name]
            
            # Key für Session State
            state_key = (nr, r_name)
            if state_key not in st.session_state.steward_actions:
                st.session_state.steward_actions[state_key] = {"Aufruf": False, "BIV": False, "NOM": False}
            
            c1, c2, c3, c4, c5 = st.columns([1, 2, 1, 1, 1])
            with c1: st.write(f"**{nr}**")
            with c2: st.write(f"{row['Rasse']} ({r_name})")
            with c3: 
                st.session_state.steward_actions[state_key]["Aufruf"] = st.checkbox("Aufruf", value=st.session_state.steward_actions[state_key]["Aufruf"], key=f"auf_{nr}_{cat_name}")
            with c4: 
                st.session_state.steward_actions[state_key]["BIV"] = st.checkbox("BIV", value=st.session_state.steward_actions[state_key]["BIV"], key=f"biv_{nr}_{cat_name}")
            with c5: 
                st.session_state.steward_actions[state_key]["NOM"] = st.checkbox("NOM", value=st.session_state.steward_actions[state_key]["NOM"], key=f"nom_{nr}_{cat_name}")

if st.button("Änderungen für alle Ringe bestätigen"):
    st.rerun()
