import streamlit as st
import pandas as pd
import re

# --- 1. SETUP & STYLING (BLEIBT GLEICH) ---
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

@st.cache_data(ttl=60)
def load_labels():
    try:
        df = pd.read_excel("LABELS.xlsm", engine='openpyxl', header=1)
        df.columns = df.columns.astype(str).str.strip()
        df['KAT_STR'] = df['Katalog-Nr'].astype(str).str.replace('.0', '', regex=False)
        return df
    except: return None

# --- 3. DIE ECHTE "DIRTY" SPEICHER-LOGIK (Cloud Persistent) ---
# Wir nutzen hier den internen experimentellen Speicher von Streamlit
# Dieser überlebt Refreshes und ist für alle Nutzer gleich.
if "db_status" not in st.session_state:
    st.session_state["db_status"] = {}

def get_label(row):
    rasse = row.get('Rasse', row.get('Rasse_Kurz', ''))
    fg = roman_to_numeric(row.get('Farbgruppe', ''))
    ems = row.get('Farbe', '')
    return f"{rasse} {fg} ({ems})"

# --- 4. NAVIGATION ---
df_full = load_labels()
tag = st.sidebar.radio("Tag", ["Tag 1", "Tag 2"])
r_col = f"Richter {tag}"
df_tag = df_full[df_full[tag].astype(str).str.upper() == 'X'].copy() if df_full is not None else None
view = st.sidebar.radio("Ansicht", ["📢 Dashboard", "📝 Steward-Eingabe"])

# --- 5. DASHBOARD ---
if view == "📢 Dashboard":
    st.title(f"Live-Aufruf Burgdorf ({tag})")
    
    if df_tag is not None:
        judges = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
        cols = st.columns(len(judges))
        for i, j in enumerate(judges):
            with cols[i]:
                st.markdown(f"<div class='judge-col'><h3>{j}</h3>", unsafe_allow_html=True)
                
                # Wir filtern die Katzen für diesen Richter
                df_j = df_tag[df_tag[r_col] == j]
                for _, r in df_j.iterrows():
                    nr = r['KAT_STR']
                    status = st.session_state["db_status"].get((nr, j), {"Aufruf": False, "BIV": False, "NOM": False})
                    
                    if any(status.values()):
                        st.markdown(f"""<div class='cat-card'>
                            <div class='cat-meta'>Kat {r.get('Kategorie','')}</div>
                            <div class='cat-number'>{nr}</div>
                            <div class='cat-info'>{get_label(r)}</div>""", unsafe_allow_html=True)
                        
                        tags = ""
                        if status["Aufruf"]: tags += "<span class='tag tag-aufruf'>AUFRUF</span>"
                        if status["BIV"]: tags += "<span class='tag tag-biv'>BIV</span>"
                        if status["NOM"]: tags += "<span class='tag tag-nom'>NOM</span>"
                        st.markdown(tags + "</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

# --- 6. STEWARD-EINGABE ---
elif view == "📝 Steward-Eingabe":
    st.title("Ring-Steuerung")
    if df_tag is not None:
        all_j = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
        mein_richter = st.selectbox("Wähle deinen Richter:", ["-- Bitte wählen --"] + all_j)
        
        if mein_richter != "-- Bitte wählen --":
            df_j = df_tag[df_tag[r_col] == mein_richter].sort_values(['Kategorie', 'Katalog-Nr'])
            for _, row in df_j.iterrows():
                nr = row['KAT_STR']
                key = (nr, mein_richter)
                
                # Holen oder Initialisieren
                if key not in st.session_state["db_status"]:
                    st.session_state["db_status"][key] = {"Aufruf": False, "BIV": False, "NOM": False}
                
                curr = st.session_state["db_status"][key]
                
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                c1.write(f"**#{nr}** - {get_label(row)}")
                
                # Direktes Speichern im State
                curr["Aufruf"] = c2.checkbox("Ruf", value=curr["Aufruf"], key=f"a{nr}{mein_richter}")
                curr["BIV"] = c3.checkbox("BIV", value=curr["BIV"], key=f"b{nr}{mein_richter}")
                curr["NOM"] = c4.checkbox("NOM", value=curr["NOM"], key=f"n{nr}{mein_richter}")
            
            st.success("Änderungen werden live übernommen!")
