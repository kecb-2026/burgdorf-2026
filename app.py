import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import re
import json

# --- 1. SETUP & STYLING (BEIBEHALTEN) ---
st.set_page_config(layout="wide", page_title="KECB Burgdorf 2026", page_icon="🐾")

st.markdown("""
    <style>
    .judge-col { 
        border: 3px solid #1a4a9e; padding: 15px; border-radius: 20px; 
        background-color: #ffffff; min-height: 800px; margin-bottom: 20px; 
        box-shadow: 2px 2px 15px rgba(0,0,0,0.1);
    }
    .judge-col h3 { 
        font-size: 32px !important; color: white; background-color: #1a4a9e; 
        padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 20px;
    }
    .cat-card { 
        padding: 15px; border-bottom: 2px solid #f0f0f0; margin-bottom: 15px; 
        text-align: center; background-color: #fafafa; border-radius: 15px; 
    }
    .cat-number { 
        font-size: 100px !important; font-weight: 900 !important; 
        color: #1a4a9e; line-height: 0.8; margin: 10px 0;
    }
    .cat-info { font-size: 22px; color: #333; font-weight: bold; }
    .cat-meta { font-size: 18px; color: #666; font-style: italic; }
    .tag { font-weight: bold; padding: 8px 16px; border-radius: 8px; font-size: 20px; display: inline-block; margin: 4px; }
    .tag-aufruf { background-color: #007bff; color: white; }
    @keyframes blinker { 50% { opacity: 0.2; } }
    .tag-biv { background-color: #28a745; color: white; animation: blinker 1.5s linear infinite; }
    .tag-nom { background-color: #ffc107; color: black; animation: blinker 1s linear infinite; }
    .stCheckbox { transform: scale(1.3); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HILFSFUNKTIONEN ---
def roman_to_numeric(text):
    roman_map = {'IX': '9', 'VIII': '8', 'VII': '7', 'VI': '6', 'IV': '4', 'V': '5', 'III': '3', 'II': '2', 'I': '1'}
    if pd.isna(text) or text == "": return ""
    res = str(text).upper()
    for rom, num in roman_map.items():
        res = re.sub(rf'\b{rom}\b', num, res)
    return res

@st.cache_data(ttl=15)
def load_labels():
    try:
        df = pd.read_excel("LABELS.xlsm", engine='openpyxl', header=1)
        df.columns = df.columns.astype(str).str.strip()
        if 'Rasse_Kurz' not in df.columns: df.rename(columns={'Rasse': 'Rasse_Kurz'}, inplace=True)
        df['KAT_STR'] = df['Katalog-Nr'].astype(str).str.replace('.0', '', regex=False)
        return df
    except Exception as e:
        st.error(f"Excel-Fehler: {e}")
        return None

# --- 3. DIE "DIRTY" CLOUD-VERBINDUNG ---
# Wir nutzen hier die URL-basierte Methode, die weniger Rechte-Stress macht
conn = st.connection("gsheets", type=GSheetsConnection)

def get_cloud_data():
    try:
        # TTL=0 zwingt zum Neuladen ohne Cache
        df = conn.read(worksheet="Status", ttl=0)
        data = {}
        if df is not None and not df.empty:
            for _, row in df.iterrows():
                key = (str(row['ID']), str(row['Richter']))
                data[key] = json.loads(row['Status_JSON'])
        return data
    except:
        return {}

def save_judge_data(current_state, target_judge):
    try:
        # Dirty Trick: Wir holen alles, mergen lokal und pushen alles neu
        all_data = get_cloud_data()
        for key, status in current_state.items():
            if key[1] == target_judge:
                all_data[key] = status
        
        rows = []
        for (nr, j_name), stat in all_data.items():
            rows.append({"ID": nr, "Richter": j_name, "Status_JSON": json.dumps(stat)})
        
        if rows:
            df_save = pd.DataFrame(rows)
            # WICHTIG: Falls conn.update() fehlschlägt, ist das Sheet nicht auf Editor gestellt!
            conn.update(worksheet="Status", data=df_save)
            st.cache_data.clear()
            return True
    except Exception as e:
        st.error(f"Fehler beim Schreiben. Ist das Google Sheet auf 'Editor für jeden' gestellt? {e}")
        return False

# --- 4. INITIALISIERUNG ---
df_full = load_labels()
if 'steward_actions' not in st.session_state:
    st.session_state.steward_actions = get_cloud_data()

tag = st.sidebar.radio("Tag", ["Tag 1", "Tag 2"])
r_col = f"Richter {tag}"
df_tag = df_full[df_full[tag].astype(str).str.upper() == 'X'].copy() if df_full is not None else None

view = st.sidebar.radio("Ansicht", ["📢 Dashboard", "📝 Steward-Eingabe"])

def get_label(row):
    return f"{row.get('Rasse_Kurz','')} {roman_to_numeric(row.get('Farbgruppe',''))} ({row.get('Farbe','')})"

# --- 5. DASHBOARD ---
if view == "📢 Dashboard":
    st.title(f"Live-Aufruf Burgdorf ({tag})")
    # Manuelles Refresh-Button für das Dashboard (Dirty & Sicher)
    if st.button("🔄 Ansicht aktualisieren"):
        st.session_state.steward_actions = get_cloud_data()
        st.rerun()

    if df_tag is not None:
        judges = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
        cols = st.columns(len(judges))
        for i, j in enumerate(judges):
            with cols[i]:
                st.markdown(f"<div class='judge-col'><h3>{j}</h3>", unsafe_allow_html=True)
                active = []
                # Aktuellen Cloud-Stand für diesen Richter ziehen
                current_cloud = get_cloud_data()
                for (nr, richter), stat in current_cloud.items():
                    if richter == j and any(stat.values()):
                        match = df_tag[df_tag['KAT_STR'] == nr]
                        if not match.empty: 
                            active.append({'row': match.iloc[0], 'stat': stat, 'nr': nr})
                
                if active:
                    active = sorted(active, key=lambda x: (int(x['row'].get('Kategorie', 99)), int(x['nr'])))
                    for item in active:
                        r = item['row']
                        st.markdown(f"""<div class='cat-card'><div class='cat-meta'>Kat {r.get('Kategorie','')}</div>
                            <div class='cat-number'>{item['nr']}</div><div class='cat-info'>{get_label(r)}</div>""", unsafe_allow_html=True)
                        tags = "".join([f"<span class='tag tag-{t.lower()}'>{t.upper()}</span>" for t, v in item['stat'].items() if v])
                        st.markdown(tags + "</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

# --- 6. STEWARD-EINGABE ---
elif view == "📝 Steward-Eingabe":
    st.title("Ring-Steuerung")
    if df_tag is not None:
        all_j = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
        mein_richter = st.selectbox("Wähle deinen Richter:", ["-- Bitte wählen --"] + all_j)
        
        if mein_richter != "-- Bitte wählen --":
            # Beim Wechseln des Richters kurz die Cloud fragen
            if st.button("📥 Aktuellen Stand von Ring laden"):
                st.session_state.steward_actions = get_cloud_data()
                st.rerun()

            df_j = df_tag[df_tag[r_col] == mein_richter].sort_values(['Kategorie', 'Katalog-Nr'])
            for _, row in df_j.iterrows():
                nr = row['KAT_STR']
                key = (nr, mein_richter)
                if key not in st.session_state.steward_actions:
                    st.session_state.steward_actions[key] = {"Aufruf": False, "BIV": False, "NOM": False}
                
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                c1.write(f"**#{nr}** (Kat {row.get('Kategorie','')}) - {get_label(row)}")
                st.session_state.steward_actions[key]["Aufruf"] = c2.checkbox("Ruf", value=st.session_state.steward_actions[key]["Aufruf"], key=f"a{nr}{mein_richter}")
                st.session_state.steward_actions[key]["BIV"] = c3.checkbox("BIV", value=st.session_state.steward_actions[key]["BIV"], key=f"b{nr}{mein_richter}")
                st.session_state.steward_actions[key]["NOM"] = c4.checkbox("NOM", value=st.session_state.steward_actions[key]["NOM"], key=f"n{nr}{mein_richter}")
            
            st.divider()
            if st.button(f"💾 ÄNDERUNGEN FÜR {mein_richter} SPEICHERN", use_container_width=True):
                if save_judge_data(st.session_state.steward_actions, mein_richter):
                    st.success("Erfolgreich gespeichert!")
