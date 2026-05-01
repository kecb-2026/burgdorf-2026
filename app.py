elif st.session_state.view == "BIS_Admin_Control":
    st.title("🏆 BIS Steuerung & Gewinner-Kür")
    df_full = load_labels()
    if df_full is not None:
        sel_cat = st.selectbox("Kategorie verwalten:", sorted(df_full['KATEGORIE'].unique()))
        bis_defs = ["Adult Male", "Adult Female", "Neuter Male", "Neuter Female", "Junior (11) Male", "Junior (11) Female", "Kitten (12) Male", "Kitten (12) Female"]
        
        st.subheader("1. Sichtbarkeit & Gewinner")
        # Wir speichern die Gewinner kurz zwischen, um sie unten in der Tabelle zu markieren
        current_winners_dict = {}

        for label in bis_defs:
            with st.expander(f"Klasse: {label}"):
                c1, c2 = st.columns([1, 2])
                key_reveal = f"reveal_{sel_cat}_{label}"
                key_winner = f"winner_{sel_cat}_{label}"
                
                # Sichtbarkeit auf dem Public Screen[span_2](start_span)[span_2](end_span)
                store.data[key_reveal] = c1.checkbox("Anzeigen", value=store.data.get(key_reveal, False), key=f"cb_{key_reveal}")
                
                # Pool der nominierten Katzen für diese Klasse[span_3](start_span)[span_3](end_span)
                klassen_ids = {"Adult Male": ([1,3,5,7,9], "M"), "Adult Female": ([1,3,5,7,9], "W"), "Neuter Male": ([2,4,6,8,10], "M"), "Neuter Female": ([2,4,6,8,10], "W"), "Junior (11) Male": ([11], "M"), "Junior (11) Female": ([11], "W"), "Kitten (12) Male": ([12], "M"), "Kitten (12) Female": ([12], "W")}
                kl, gs = klassen_ids[label]
                pool = df_full[(df_full['SELECTION'].astype(str).str.upper() == 'X') & (df_full['KATEGORIE'] == sel_cat) & (df_full['KLASSE_INTERNAL'].isin(kl)) & (df_full['GESCHLECHT'].astype(str).str.upper() == gs)]
                
                cat_options = ["-- Kein Gewinner --"] + sorted(pool['KAT_STR'].tolist())
                current_winner = store.data.get(key_winner, "-- Kein Gewinner --")
                winner_idx = cat_options.index(current_winner) if current_winner in cat_options else 0
                
                # Auswahl des Gewinners[span_4](start_span)[span_4](end_span)
                selected_winner = c2.selectbox("🏆 GEWINNER WÄHLEN:", cat_options, index=winner_idx, key=f"sel_{key_winner}")
                store.data[key_winner] = selected_winner
                current_winners_dict[label] = selected_winner

        st.divider()
        st.subheader("2. Detaillierte Wahlergebnisse (mit Gewinner-Status)")
        if "votes" in store.data:
            for label in bis_defs:
                prefix = f"v_{sel_cat}_{label}_"
                votes_in_class = {k.replace(prefix, ""): v for k, v in store.data["votes"].items() if k.startswith(prefix) and v != "Keine Wahl"}
                
                if votes_in_class:
                    summary = {}
                    for judge, kat_nr in votes_in_class.items():
                        if kat_nr not in summary: summary[kat_nr] = []
                        summary[kat_nr].append(judge)
                    
                    st.write(f"**Stimmen in {label}:**")
                    
                    # Hier integrieren wir den Gewinner-Status in die Liste[span_5](start_span)[span_5](end_span)
                    res_list = []
                    official_winner = current_winners_dict.get(label, "-- Kein Gewinner --")
                    
                    for kat_nr, judges_list in summary.items():
                        is_winner = "🏆 GEWINNER" if kat_nr == official_winner else "–"
                        res_list.append({
                            "Status": is_winner,
                            "Katze": f"#{kat_nr}",
                            "Stimmen": len(judges_list),
                            "Richter": ", ".join(judges_list)
                        })
                    
                    # Tabelle anzeigen, Gewinner steht idealerweise oben
                    df_res = pd.DataFrame(res_list).sort_values(by=["Status", "Stimmen"], ascending=[False, False])
                    st.table(df_res)
        else: 
            st.info("Noch keine Voting-Daten von den Richtern vorhanden.")
    
    if st.button("⬅️ Zurück zum Menü"): 
        set_view("Home")
