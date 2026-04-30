import streamlit as st
import pandas as pd
import re
import json
import os

# --- 1. SETUP & DATEN-SICHERUNG ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

DATA_FILE = "steward_data.json"
VOTE_FILE = "judge_votes.json"

def save_json(data, filename):
    serializable = {f"{k[0]}|{k[1]}" if isinstance(k, tuple) else k: v for k, v in data.items()}
    with open(filename, "w") as f:
        json.dump(serializable, f)

def load_json(filename):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                raw = json.load(f)
                return {tuple(k.split("|")) if "|" in k else k: v for k, v in raw.items()}
        except: return {}
    return {}

# --- 2. STYLING ---
st.markdown("""
    <style>
    .judge-col { border: 3px solid #1a4a9e; padding: 15px; border-radius: 20px; background-color: #ffffff; min-height: 650px; }
    .judge-col h3 { font-size: 32px !important; color: white; background-color: #1a4a9e; padding: 10px; border-radius: 10px; text-align: center; }
    .cat-card { padding: 20px; border-bottom: 2px solid #f0f0f0; margin-bottom: 15px; text-align: center; }
    .cat-number { font-size: 100px !important; font-weight: 900 !important; color: #1a4a9e; line-height: 0.8; }
    .cat-info { font-size: 24px; color: #333; font-weight: bold; }
    .tag { font-weight: bold; padding: 8px 16px; border-radius: 10px; font-size: 20px; display: inline-block; margin: 4px; }
    .tag-aufruf { background-color: #007bff; color: white; }
    @keyframes blinker { 50% { opacity: 0.2; } }
    .tag-biv { background-color: #28a745; color: white; animation: blinker 1.5s linear infinite; }
    .tag-nom { background-color: #ffc107; color: black; animation: blinker 1s linear infinite; }
    .winner-box { text-align: center; border: 15px solid #1a4a9e; padding: 40px; background-color: white; border-radius: 50px; margin-top: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN & AUTH ---
if 'auth' not in st.session_state:
    st.session_state.auth = st.query_params.get("role")

if not st.session_state.auth:
    st.title("🔑 KECB Burgdorf 2026")
    pw = st.text_input("Passwort", type="password")
    if st.button("Einloggen"):
        role = {"Burgdorf26": "admin", "judge26": "richter", "ring26": "steward"}.get(pw)
        if role:
            st.session_state.auth = role
            st.query_params["role"] = role
            st.rerun()
    st.stop()

# --- 4. DATEN LADEN ---
@st.cache_data(ttl=5)
def load_excel():
    try:
        df = pd.read_excel("LABELS.xlsm", engine='openpyxl', header=1)
        df.columns = df.columns.astype(str).str.strip()
        if 'Rasse_Kurz' not in df.columns: df.rename(columns={'Rasse': 'Rasse_Kurz'}, inplace=True)
        df['Katalog-Nr'] = pd.to_numeric(df['Katalog-Nr'], errors='coerce')
        return df
    except: return None

df_full = load_excel()
if 'steward_actions' not in st.session_state: st.session_state.steward_actions = load_json(DATA_FILE)
if 'judge_votes' not in st.session_state: st.session_state.judge_votes = load_json(VOTE_FILE)
if 'sieger_id' not in st.session_state: st.session_state.sieger_id = None

tag = st.sidebar.radio("Tag", ["Tag 1", "Tag 2"])
r_col = f"Richter {tag}"
df_tag = df_full[df_full[tag].astype(str).str.upper() == 'X'].copy() if df_full is not None else None
if df_tag is not None: df_tag = df_tag.sort_values(by=[r_col, 'Kategorie', 'Katalog-Nr'])

# --- 5. NAVIGATION ---
menu = ["Dashboard", "Steward-Eingabe", "Richter-Votum", "Beamer-Regie"]
if st.session_state.auth == "steward": menu = ["Steward-Eingabe", "Dashboard"]
if st.session_state.auth == "richter": menu = ["Richter-Votum", "Dashboard"]
view = st.sidebar.radio("Navigation", menu)

def get_cat_info(row):
    return f"{row.get('Rasse_Kurz','')} ({row.get('Farbe','')})"

# --- 6. MODULE ---

if view == "Dashboard":
    st.title(f"📢 Live-Aufruf ({tag})")
    if df_tag is not None:
        judges = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
        cols = st.columns(len(judges))
        for i, j in enumerate(judges):
            with cols[i]:
                st.markdown(f"<div class='judge-col'><h3>{j}</h3>", unsafe_allow_html=True)
                active = sorted([{'nr': k[0], 'stat': v, 'row': df_tag[df_tag['Katalog-Nr']==int(k[0])].iloc[0]} 
                                for k, v in st.session_state.steward_actions.items() if k[1] == j and any(v.values())], 
                                key=lambda x: (x['row']['Kategorie'], x['nr']))
                for item in active:
                    st.markdown(f"<div class='cat-card'><div class='cat-number'>{int(item['nr'])}</div><div class='cat-info'>{get_cat_info(item['row'])}</div>", unsafe_allow_html=True)
                    tags = "".join([f"<span class='tag tag-{t.lower()}'>{t}</span>" for t, active in item['stat'].items() if active])
                    st.markdown(tags + "</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

elif view == "Steward-Eingabe":
    st.title("📝 Steward-Pult")
    if df_tag is not None:
        for j in sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"]):
            with st.expander(f"Richter: {j}", expanded=True):
                df_j = df_tag[df_tag[r_col] == j]
                for _, row in df_j.iterrows():
                    nr = str(int(row['Katalog-Nr']))
                    key = (nr, j)
                    if key not in st.session_state.steward_actions: st.session_state.steward_actions[key] = {"Aufruf": False, "BIV": False, "NOM": False}
                    c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                    c1.write(f"**#{nr}** {get_cat_info(row)}")
                    st.session_state.steward_actions[key]["Aufruf"] = c2.checkbox("Ruf", value=st.session_state.steward_actions[key]["Aufruf"], key=f"a{nr}{j}")
                    st.session_state.steward_actions[key]["BIV"] = c3.checkbox("BIV", value=st.session_state.steward_actions[key]["BIV"], key=f"b{nr}{j}")
                    st.session_state.steward_actions[key]["NOM"] = c4.checkbox("NOM", value=st.session_state.steward_actions[key]["NOM"], key=f"n{nr}{j}")
        if st.button("💾 SPEICHERN"):
            save_json(st.session_state.steward_actions, DATA_FILE)
            st.rerun()

elif view == "Richter-Votum":
    st.title("🏆 Richter-Abstimmung")
    mein_name = st.selectbox("Name wählen", sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"]))
    noms = [k[0] for k, v in st.session_state.steward_actions.items() if k[1] == mein_name and v["NOM"]]
    for nr in noms:
        st.session_state.judge_votes[(nr, mein_name)] = st.text_input(f"Votum für Katze #{nr}", value=st.session_state.judge_votes.get((nr, mein_name), ""), key=f"v{nr}")
    if st.button("💾 VOTUM SPEICHERN"):
        save_json(st.session_state.judge_votes, VOTE_FILE)
        st.success("Stimme gespeichert!")

elif view == "Beamer-Regie":
    st.title("🎬 Beamer-Regie")
    noms_alle = sorted(list(set([k[0] for k, v in st.session_state.steward_actions.items() if v["NOM"]])), key=int)
    choice = st.selectbox("Sieger-Katze auswählen", ["-"] + noms_alle)
    if st.button("👑 SIEGER ANZEIGEN"): st.session_state.sieger_id = choice
    if st.button("❌ RESET"): st.session_state.sieger_id = None
    
    if st.session_state.sieger_id and st.session_state.sieger_id != "-":
        res = df_tag[df_tag['Katalog-Nr'] == int(st.session_state.sieger_id)].iloc[0]
        st.markdown(f"<div class='winner-box'><h1 style='font-size: 60px;'>BEST IN SHOW</h1><div class='cat-number'>{st.session_state.sieger_id}</div><h2 style='font-size: 40px;'>{res.get('Name','')}</h2><h3>{get_cat_info(res)}</h3></div>", unsafe_allow_html=True)
