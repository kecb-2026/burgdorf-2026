import streamlit as st
import pandas as pd
import re

# --- 1. SETUP & STYLING ---
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
        padding: 20px; border-bottom: 2px solid #f0f0f0; margin-bottom: 25px; 
        text-align: center; background-color: #fafafa; border-radius: 20px; 
    }
    .cat-number { 
        font-size: 110px !important; font-weight: 900 !important; 
        color: #1a4a9e; line-height: 0.8; margin: 10px 0;
    }
    .cat-label { 
        font-size: 26px; color: #333; font-weight: bold; margin: 10px 0;
    }
    .cat-meta { font-size: 18px; color: #666; font-style: italic; margin-bottom: 5px; }
    
    /* Tags innerhalb der Karte */
    .tag { font-weight: bold; padding: 10px 20px; border-radius: 10px; font-size: 22px; display: inline-block; margin: 5px; }
    .tag-aufruf { background-color: #007bff; color: white; }
    
    @keyframes blinker { 50% { opacity: 0.2; } }
    .tag-biv { background-color: #28a745; color: white; animation: blinker 1.5s linear infinite; }
    .tag-nom { background-color: #ffc107; color: black; animation: blinker 1s linear infinite; }
    
    .stCheckbox { transform: scale(1.4); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GLOBALER SPEICHER (Refresh-sicher) ---
class GlobalStore:
    def __init__(self):
        self.data = {}

@st.cache_resource
def get_store():
    return GlobalStore()

store = get_store()

# --- 3. HILFSFUNKTIONEN ---
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

def get_full_label(row):
    rasse = row.get('Rasse_Kurz', row.get('Rasse', ''))
    gruppe = roman_to_numeric(row.get('Farbgruppe', ''))
    return f"{rasse} {gruppe}".strip()

# --- 4. NAVIGATION ---
df_full = load_labels()
tag = st.sidebar.radio("Ausstellungstag", ["Tag 1", "Tag 2"])
r_col = f"Richter {tag}"
df_tag = df_full[df_full[tag].astype(str).str.upper() == 'X'].copy() if df_full is not None else None
view = st.sidebar.radio("Modus", ["📢 Dashboard", "📝 Steward-Eingabe"])

# --- 5. DASHBOARD (LIVE-ANZEIGE) ---
if view == "📢 Dashboard":
    st.title(f"Live-Aufruf Burgdorf ({tag})")
    if st.button("🔄 Ansicht aktualisieren"):
        st.rerun()

    if df_tag is not None:
        judges = sorted([r for r in df_tag[r_col].unique() if str(r) != "nan"])
        cols = st.columns(len(judges))
        
        for i, j in enumerate(judges):
            with cols[i]:
                st.markdown(f"<div class='judge-col'><h3>{j}</h3>", unsafe_allow_html=True)
                
                active_entries = []
                for key, stat in store.data.items():
                    if "|" in key:
                        nr, richter = key.split("|")
                        if richter == j and any(stat.values()):
                            match = df_tag[df_tag['KAT_STR'] == nr]
                            if not match.empty:
                                active_entries.append({'row': match.iloc[0], 'stat': stat, 'nr': nr})
                
                # Sortierung: Kategorie -> Nummer
                active_entries = sorted(active_entries, key=lambda x: (int(x['row'].get('Kategorie', 99)), int(x['nr'])))
                
                for item in active_entries:
                    r = item['row']
                    # Start der weißen Karte
                    st.markdown(f"""
                        <div class='cat-card'>
                            <div class='cat-meta'>Kategorie {r.get('Kategorie','')}</div>
                            <div class='cat-number'>{item['nr']}</div>
                            <div class='cat-label'>{get_full_label(r)}</div>
                        """, unsafe_allow_html=True)
                    
                    # Tags direkt unter dem Label (noch innerhalb der cat-card)
                    tags = ""
                    if item['stat'].get("Aufruf"): tags += "<span class='tag tag-aufruf'>AUFRUF</span>"
                    if item['stat'].get("BIV"): tags += "<span class='tag tag-biv'>BIV</span>"
                    if item['stat'].get("NOM"): tags += "<span class='tag tag-nom'>NOM</span>"
                    
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
                db_key = f"{nr}|{mein_richter}"
                
                if db_key not in store.data:
                    store.data[db_key] = {"Aufruf": False, "BIV": False, "NOM": False}
                
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                c1.write(f"**#{nr}** - {get_full_label(row)} (Kat {row.get('Kategorie','')})")
                
                store.data[db_key]["Aufruf"] = c2.checkbox("Ruf", value=store.data[db_key]["Aufruf"], key=f"a{db_key}")
                store.data[db_key]["BIV"] = c3.checkbox("BIV", value=store.data[db_key]["BIV"], key=f"b{db_key}")
                store.data[db_key]["NOM"] = c4.checkbox("NOM", value=store.data[db_key]["NOM"], key=f"n{db_key}")
            
            st.divider()
            st.success("Änderungen sind live im Dashboard sichtbar.")
