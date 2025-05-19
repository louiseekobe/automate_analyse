import streamlit as st
import pandas as pd

def show():
    st.title("🔍 Analyse Générale")

    # ✅ Vérification que les DataFrames sont bien disponibles
    if "df_fmr" not in st.session_state or "df_nat" not in st.session_state or "df_merged" not in st.session_state:
        st.warning("⚠️ Les données n'ont pas été chargées ou fusionnées. Veuillez le faire dans la page d'accueil.")
        return
    
    if "active_analysis" not in st.session_state:
                st.session_state.active_analysis = None
    
    # ✅ Récupération des DataFrames depuis la session
    df_fmr = st.session_state["df_fmr"]
    df_nat = st.session_state["df_nat"]
    df_merged = st.session_state["df_merged"]

    st.success("✅ Données chargées avec succès.")

    # Navigation des analyses avec menu persistant
    buttons = {
        "personnes": "👥 Total + Moyenne déplacée",
        "fmp": "📦 Informations FMP",
        "nationalites": "🌐 Nationalités",
        "profil": "🧭 Profil voyageur",
        "transport": "✅ Moyen de transport",
        "depart": "🏁 Pays de départ",
        "destination": "🏁 Pays de destination"
    }

    for key, label in buttons.items():
        if st.button(label):
            st.session_state.active_analysis = key
            for state_key in list(st.session_state.keys()):
                if state_key.startswith("selected_"):
                    del st.session_state[state_key]

    
    # --- ANALYSE PERSONNES ---
    if st.session_state.active_analysis == "personnes":
        st.markdown("### 👥 Analyse du nombre de personnes déplacées")
        colnames = df_fmr.columns.tolist()
        count_col = st.selectbox("🔢 Colonne : nombre total de personnes", colnames, key="selected_count")
        date_col = st.selectbox("📅 Colonne : date de l'enquête", colnames, key="selected_date")
        if st.button("Lancer l'analyse"):   
            if count_col and date_col:
                try:
                    df_fmr[count_col] = pd.to_numeric(df_fmr[count_col], errors='coerce')
                    df_fmr[date_col] = pd.to_datetime(df_fmr[date_col], errors='coerce')
                    total = df_fmr[count_col].sum(skipna=True)
                    nb_jours = len(df_fmr[date_col].dt.date.unique())
                    moyenne = round(total / nb_jours, 2) if nb_jours else 0
                    st.success(f"✅ Total : {int(total)} personnes")
                    st.info(f"📊 Moyenne journalière : {moyenne} personnes/jour sur {nb_jours} jours")
                    st.session_state["total_personnes"] = total
                except Exception as e:
                    st.error(f"Erreur : {e}")
    
    ## == ANALYSES FMP ==
    elif st.session_state.active_analysis == "fmp":
        st.markdown("### 📦 Analyse des FMP")
        colnames = df_fmr.columns.tolist()
        fmp_col = st.selectbox("🏷️ Colonne : nom FMP", colnames, key="selected_fmp")
        count_col = st.selectbox("🔢 Colonne : nombre total de personnes", colnames, key="selected_count_fmp")
        type_flux_col = st.selectbox("🔄 Colonne : type de flux", colnames, key="selected_flux_fmp")
        if st.button("Lancer l'analyse"):    
            if fmp_col and count_col and type_flux_col:
                try:
                    df_fmr[count_col] = pd.to_numeric(df_fmr[count_col], errors='coerce')
                    grouped = df_fmr.dropna(subset=[type_flux_col, count_col]) \
                                     .groupby(type_flux_col)[count_col].sum()
                    st.success(f"✅ Nombre de FMP : {df_fmr[fmp_col].nunique()}")
                    st.markdown("#### 🔄 Nombre de personnes par type de flux")
                    st.dataframe(grouped)
                    pourcentages = round((grouped / grouped.sum()) * 100, 2)
                    st.markdown("#### 📊 Pourcentage par type de flux")
                    st.dataframe(pourcentages)
                except Exception as e:
                    st.error(f"Erreur : {e}")
                
    # == NATIONALITES  ==
    elif st.session_state.active_analysis == "nationalites":
        st.markdown("### 🌐 Répartition des nationalités")
        colnames = df_merged.columns.tolist()
        nat_col = st.selectbox("🌍 Colonne : nationalité", colnames, key="selected_nat")
        count_col = st.selectbox("🔢 Colonne : nombre de personnes", colnames, key="selected_nat_count")
        flux_col = st.selectbox("🔄 Colonne : type de flux", colnames, key="selected_nat_flux")
        if st.button("Lancer l'analyse"):    
            if nat_col and count_col and flux_col:
                try:
                    grouped = df_merged.groupby(nat_col)[count_col].sum()
                    st.markdown("#### 📊 nombre de personnes par nationalité")
                    st.dataframe(grouped.sort_values(ascending=False).head(10))
                    pourcentages = round((grouped / grouped.sum()) * 100, 2)
                    st.markdown("#### 📊 Pourcentage par nationalité")
                    st.dataframe(pourcentages.sort_values(ascending=False).head(10))
                    pivot = df_merged.pivot_table(
                        index=nat_col,
                        columns=flux_col,
                        values=count_col,
                        fill_value=0
                    )
                    total_all = pivot.values.sum()
                    pivot_percent = round((pivot / total_all) * 100, 2)
                    st.markdown("#### 📉 Répartition (%) par flux et nationalité")
                    st.dataframe(pivot_percent.sort_values(by=pivot_percent.columns[0], ascending=False))
                except Exception as e:
                    st.error(f"Erreur : {e}")
                
    # == PROFIL  ==
    elif st.session_state.active_analysis == "profil":
        st.markdown("### 🧭 Profil des voyageurs")
        colnames = df_fmr.columns.tolist()
        selected_homme_col = st.selectbox("👨 Colonne : hommes 18-59 ans", colnames, key="homme_col")
        selected_femme_col = st.selectbox("👩 Colonne : femmes 18-59 ans", colnames, key="femme_col")
        selected_fille_col = st.selectbox("👧 Colonne : filles", colnames, key="fille_col")
        selected_garcon_col = st.selectbox("👦 Colonne : garçons", colnames, key="garcon_col")
        selected_homme60_col = st.selectbox("👴 Colonne : hommes 60+", colnames, key="homme60_col")
        selected_femme60_col = st.selectbox("👵 Colonne : femmes 60+", colnames, key="femme60_col")
        # Vérifier que toutes les colonnes sont sélectionnées
        if not all([
            selected_homme_col, selected_femme_col, selected_fille_col,
            selected_garcon_col, selected_homme60_col, selected_femme60_col
            ]):
            st.warning("⚠️ Veuillez sélectionner toutes les colonnes nécessaires.")
        else:
            if st.button("Lancer l'analyse"):    
                try:
                    # Conversion en numérique
                    df_fmr[selected_homme_col] = pd.to_numeric(df_fmr[selected_homme_col], errors='coerce')
                    df_fmr[selected_femme_col] = pd.to_numeric(df_fmr[selected_femme_col], errors='coerce')
                    df_fmr[selected_fille_col] = pd.to_numeric(df_fmr[selected_fille_col], errors='coerce')
                    df_fmr[selected_garcon_col] = pd.to_numeric(df_fmr[selected_garcon_col], errors='coerce')
                    df_fmr[selected_homme60_col] = pd.to_numeric(df_fmr[selected_homme60_col], errors='coerce')
                    df_fmr[selected_femme60_col] = pd.to_numeric(df_fmr[selected_femme60_col], errors='coerce')
                    # Total global
                    total = st.session_state.get("total_personnes")
                    if total is None or total == 0:
                        total = (
                            df_fmr[selected_homme_col].sum() +
                            df_fmr[selected_femme_col].sum() +
                            df_fmr[selected_fille_col].sum() +
                            df_fmr[selected_garcon_col].sum() +
                            df_fmr[selected_homme60_col].sum() +
                            df_fmr[selected_femme60_col].sum()
                        )
                    # Calculs
                    pvo = df_fmr[selected_femme60_col].sum() + df_fmr[selected_homme60_col].sum()
                    homme = round((df_fmr[selected_homme_col].sum() + df_fmr[selected_homme60_col].sum()) / total * 100, 2)
                    femme = round((df_fmr[selected_femme_col].sum() + df_fmr[selected_femme60_col].sum()) / total * 100, 2)
                    garcon = round(df_fmr[selected_garcon_col].sum() / total * 100, 2)
                    fille = round(df_fmr[selected_fille_col].sum() / total * 100, 2)
                    # Affichage
                    st.success(f"👥 Personnes vulnérables (60+) : **{int(pvo)}**")
                    st.info(f"👨 Hommes (avec 60+) : **{homme}%**")
                    st.info(f"👩 Femmes (avec 60+) : **{femme}%**")
                    st.info(f"👦 Garçons : **{garcon}%**")
                    st.info(f"👧 Filles : **{fille}%**")
                except Exception as e:
                    st.error(f"❌ Erreur lors du traitement : {e}")
    
    # == TRANSPORTS ==
    elif st.session_state.active_analysis == "transport":
        st.markdown("### ✅ Moyen de transport")
        colnames = df_fmr.columns.tolist()
        transport_col = st.selectbox("🌍 Colonne : moyen de transport", colnames, key="selected_transport")
        counting_col = st.selectbox("🔢 Colonne : date de l'enquête", colnames, key="selected_date_enq_count")
        if st.button("Lancer l'analyse"):    
            if transport_col and counting_col:
                try:
                    grouped = df_fmr.groupby(transport_col)[counting_col].count()
                    pourcentages = round((grouped / grouped.sum()) * 100, 2)
                    st.markdown("#### 📊 Les différents moyens de transport")
                    st.dataframe(pourcentages.sort_values(ascending=False).head(10))
        
                except Exception as e:
                    st.error(f"Erreur : {e}")
                
    # == DEPART  ==
    elif st.session_state.active_analysis == "depart":
        st.markdown("### 🏁 Pays de départ")
        colnames = df_fmr.columns.tolist()
        depart_col = st.selectbox("🌍 Colonne : pays de départ", colnames, key="depart_col")
        depart_count_col = st.selectbox("🔢 Colonne : nombre de personnes", colnames, key="depart_count_col")
        if st.button("Lancer l'analyse"):    
            if depart_col and depart_count_col:
                try:
                    df_fmr[depart_count_col] = pd.to_numeric(df_fmr[depart_count_col], errors='coerce')
                    grouped = df_fmr.groupby(depart_col)[depart_count_col].sum() 
                    pourcentages = round((grouped / grouped.sum()) * 100, 2)
                    st.markdown("#### 📊 Pourcentage par pays de destination")
                    st.dataframe(pourcentages.sort_values(ascending=False).head(6))
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'analyse : {e}")
            # 🔽 Sélection du Flux à analyser
            selected_flux_col_1 = st.selectbox("🏷️ Colonne contenant les type de flux :", colnames, key="selected_flux_col")
            selected_region_col_1 = st.selectbox("🏷️ Colonne les regions de départ ou admin 1 :", colnames, key="selected_region_col1")
            if selected_flux_col_1 and selected_region_col_1:
                flux_list = df_fmr[selected_flux_col_1].dropna().unique().tolist()
                selected_flux_value_1 = st.selectbox("📍 Sélectionnez le flux entrant :", sorted(flux_list), key="selected_flux_value")

                # 🔁 DataFrames filtrés pour ce Flux uniquement
                df_fmr_entrant = df_fmr[df_fmr[selected_flux_col_1] == selected_flux_value_1]
                if st.button("Lancer l'analyse pour les pays de provenance du flux entrant"):
                    try:
                        df_fmr_entrant[depart_count_col] = pd.to_numeric(df_fmr_entrant[depart_count_col], errors='coerce')
                        grouped = df_fmr_entrant.groupby([depart_col, selected_region_col_1])[depart_count_col].sum() 
                        pourcentages = round((grouped / grouped.sum()) * 100, 2)
                        pourcentages_df = pourcentages.reset_index(name='Pourcentage')
                        pourcentages_df = pourcentages_df.sort_values(by='Pourcentage', ascending=False)
                        st.markdown(f"#### 📊 Pourcentage par pays de depart et region pour type flux : {selected_flux_col_1}")
                        st.dataframe(pourcentages.sort_values(ascending=False).head(6))
                    except Exception as e:
                        st.error(f"❌ Erreur lors de l'analyse : {e}")
            else:
                st.warning("⚠️ Aucune colonne FLux détectée.")
                return
        
    # == DESTINATION  ==
    elif st.session_state.active_analysis == "destination":
        st.markdown("### 🏁 Analyse par pays de destination")
        colnames = df_fmr.columns.tolist()
        destination_col = st.selectbox("🌍 Colonne : pays de destination", colnames, key="destination")
        destination_count_col = st.selectbox("🔢 Colonne : nombre de personnes", colnames, key="destination_count_col")
        if st.button("Lancer l'analyse"):
            if destination_col and destination_count_col:
                try:
                    df_fmr[destination_count_col] = pd.to_numeric(df_fmr[destination_count_col], errors='coerce')
                    grouped = df_fmr.groupby(destination_col)[destination_count_col].sum()
                    pourcentages = round((grouped / grouped.sum()) * 100, 2)
                    st.markdown("#### 📊 Pourcentage par pays de destination")
                    st.dataframe(pourcentages.sort_values(ascending=False).head(6))
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'analyse : {e}")
            # 🔽 Sélection du Flux à analyser
            selected_flux_col_2 = st.selectbox("🏷️ Colonne contenant les type de flux :", colnames, key="selected_flux_col2")
            selected_region_col_2 = st.selectbox("🏷️ Colonne les regions de destination ou admin 1 :", colnames, key="selected_region_col2")
            if selected_flux_col_2 and selected_region_col_2:
                flux_list = df_fmr[selected_flux_col_2].dropna().unique().tolist()
                selected_flux_value_2 = st.selectbox("📍 Sélectionnez le flux sortant :", sorted(flux_list), key="selected_flux_value2")

                # 🔁 DataFrames filtrés pour ce Flux uniquement
                df_fmr_sortant = df_fmr[df_fmr[selected_flux_col_2] == selected_flux_value_2]
                if st.button("Lancer l'analyse pour les pays de destination du flux sortant"):
                    try:
                        df_fmr_sortant[destination_count_col] = pd.to_numeric(df_fmr_sortant[destination_count_col], errors='coerce')
                        grouped = df_fmr_sortant.groupby([destination_col, selected_region_col_2])[destination_count_col].sum() 
                        pourcentages = round((grouped / grouped.sum()) * 100, 2)
                        pourcentages_df = pourcentages.reset_index(name='Pourcentage')
                        pourcentages_df = pourcentages_df.sort_values(by='Pourcentage', ascending=False)
                        st.markdown(f"#### 📊 Pourcentage par pays de destination et region pour type flux : {selected_flux_col_2}")
                        st.dataframe(pourcentages.sort_values(ascending=False).head(6))
                    except Exception as e:
                        st.error(f"❌ Erreur lors de l'analyse : {e}")
            else:
                st.warning("⚠️ Aucune colonne FLux détectée.")
                return
