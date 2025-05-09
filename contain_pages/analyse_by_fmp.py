import streamlit as st
import pandas as pd

def show():
    st.title("🔍 Analyse Par FMP sélectionné")

    # ✅ Vérification des données
    if "df_fmr" not in st.session_state or "df_nat" not in st.session_state or "df_merged" not in st.session_state:
        st.warning("⚠️ Les données n'ont pas été chargées ou fusionnées. Veuillez le faire dans la page d'accueil.")
        return

    # ✅ Récupération des DataFrames
    df_fmr = st.session_state["df_fmr"]
    df_nat = st.session_state["df_nat"]
    df_merged = st.session_state["df_merged"]

    st.success("✅ Données chargées avec succès.")

    # 🔽 Sélection FMP
    colnames = df_fmr.columns.tolist()
    selected_fmp_col_01 = st.selectbox("🏷️ Colonne contenant les FMP :", colnames, key="selected_fmp_col_01")

    if selected_fmp_col_01:
        fmp_list = df_fmr[selected_fmp_col_01].dropna().unique().tolist()
        selected_fmp_value_01 = st.selectbox("📍 Sélectionnez un FMP :", sorted(fmp_list), key="selected_fmp_value_01")

        # Bouton de confirmation de sélection
        if st.button("🔎 Sélectionner le point de suivi des flux"):
            st.session_state["fmp_selection_active"] = True
            st.session_state["df_fmr_filtered"] = df_fmr[df_fmr[selected_fmp_col_01] == selected_fmp_value_01]
            st.session_state["df_merged_filtered"] = df_merged[df_merged[selected_fmp_col_01] == selected_fmp_value_01]
            st.session_state["selected_fmp_label"] = selected_fmp_value_01

    # ✅ Si FMP sélectionné : affichage suite
    if st.session_state.get("fmp_selection_active", False):
        df_fmr_filtered = st.session_state["df_fmr_filtered"]
        df_merged_filtered = st.session_state["df_merged_filtered"]
        selected_fmp_value_01 = st.session_state["selected_fmp_label"]

        if df_fmr_filtered.empty or df_merged_filtered.empty:
            st.warning("⚠️ Aucun résultat pour cette sélection.")
            return

        st.success(f"✅ FMP « {selected_fmp_value_01} » sélectionné avec succès.")

        # 📍 Navigation des analyses
        buttons = {
            "personnes par fmp": "👥 Total + Moyenne déplacée",
            "fmp selectionne": "📦 Informations FMP",
            "nationalites par fmp": "🌐 Nationalités",
            "profil par fmp": "🧭 Profil voyageur",
            "depart par fmp": "🏁 Pays de départ",
            "destination par fmp": "🏁 Pays de destination"
        }

        if "active_analysis" not in st.session_state:
            st.session_state.active_analysis = None

        for key, label in buttons.items():
            if st.button(label, key=f"btn_{key}"):
                st.session_state.active_analysis = key

        # 📊 Analyse spécifique : personnes par FMP
        if st.session_state.active_analysis == "personnes par fmp":
            st.markdown(f"### 👥 Analyse du nombre de personnes déplacées : **{selected_fmp_value_01}**")

            colnames = df_fmr_filtered.columns.tolist()
            count_col = st.selectbox("🔢 Colonne : nombre total de personnes", colnames, key="selected_count_01")
            date_col = st.selectbox("📅 Colonne : date de l'enquête", colnames, key="selected_date_01")

            if st.button("📈 Lancer l'analyse"):
                if count_col and date_col:
                    try:
                        df_fmr_filtered.loc[:, count_col] = pd.to_numeric(df_fmr_filtered[count_col], errors='coerce')

                        df_fmr_filtered[date_col] = pd.to_datetime(df_fmr_filtered[date_col], errors='coerce')

                        total = df_fmr_filtered[count_col].sum(skipna=True)
                        nb_jours = len(df_fmr_filtered[date_col].dt.date.unique())
                        moyenne = round(total / nb_jours, 2) if nb_jours else 0

                        st.success(f"✅ Total : {int(total)} personnes")
                        st.info(f"📊 Moyenne journalière : {moyenne} personnes/jour sur {nb_jours} jours")
                        st.session_state["total_personnes"] = total

                    except Exception as e:
                        st.error(f"Erreur lors de l'analyse : {e}")
                        
        elif st.session_state.active_analysis == "fmp selectionne":
            st.markdown(f"### 📦 Informations FMP : {selected_fmp_value_01}")
            colnames = df_fmr_filtered.columns.tolist()
            fmp_col = st.selectbox("🏷️ Colonne : nom FMP", colnames, key="selected_fmp_0101")
            count_col = st.selectbox("🔢 Colonne : nombre total de personnes", colnames, key="selected_count_fmp_0101")
            type_flux_col = st.selectbox("🔄 Colonne : type de flux", colnames, key="selected_flux_fmp_0101")
            if st.button("📈 Lancer l'analyse"):    
                if fmp_col and count_col and type_flux_col:
                    try:
                        df_fmr_filtered.loc[:, count_col] = pd.to_numeric(df_fmr_filtered[count_col], errors='coerce')

                        grouped = df_fmr_filtered.dropna(subset=[type_flux_col, count_col]) \
                                         .groupby(type_flux_col)[count_col].sum()
                        st.markdown(f"#### 🔄 Nombre de personnes par type de flux pour : {selected_fmp_value_01}")
                        st.dataframe(grouped)
                        pourcentages = round((grouped / grouped.sum()) * 100, 2)
                        st.markdown(f"#### 📊 Pourcentage par type de flux pour : {selected_fmp_value_01}")
                        st.dataframe(pourcentages)
                    except Exception as e:
                        st.error(f"Erreur : {e}")
        
        elif st.session_state.active_analysis == "nationalites par fmp":
           st.markdown(f"### 🌐 Nationalités pour FMP : {selected_fmp_value_01}")
           colnames = df_merged_filtered.columns.tolist()
           nat_col = st.selectbox("🌍 Colonne : nationalité", colnames, key="selected_nat_01")
           count_col = st.selectbox("🔢 Colonne : nombre de personnes", colnames, key="selected_nat_count_01")
           flux_col = st.selectbox("🔄 Colonne : type de flux", colnames, key="selected_nat_flux_01")
           if st.button("📈 Lancer l'analyse"):    
               if nat_col and count_col and flux_col:
                   try:
                       grouped = df_merged_filtered.groupby(nat_col)[count_col].sum()
                       st.markdown("#### 📊 nombre de personnes par nationalité")
                       st.dataframe(grouped.sort_values(ascending=False).head(10))
                       pourcentages = round((grouped / grouped.sum()) * 100, 2)
                       st.markdown("#### 📊 Pourcentage par nationalité")
                       st.dataframe(pourcentages.sort_values(ascending=False).head(10))
                       pivot = df_merged_filtered.pivot_table(
                           index=nat_col,
                           columns=flux_col,
                           values=count_col,
                           fill_value=0
                       )
                       total_all = pivot.values.sum()
                       pivot_percent = round((pivot / total_all) * 100, 2)
                       st.markdown(f"#### 📉 Répartition (%) par flux et nationalité dans : {selected_fmp_value_01}")
                       st.dataframe(pivot_percent.sort_values(by=pivot_percent.columns[0], ascending=False))
                   except Exception as e:
                       st.error(f"Erreur : {e}")

        elif st.session_state.active_analysis == "profil par fmp":
           st.markdown(f"### 🧭 Profil des voyageurs pour FMP : {selected_fmp_value_01}")
           colnames = df_fmr_filtered.columns.tolist()
           selected_homme_col_01  = st.selectbox("👨 Colonne : hommes 18-59 ans", colnames, key="homme_col_01")
           selected_femme_col_01  = st.selectbox("👩 Colonne : femmes 18-59 ans", colnames, key="femme_col_01")
           selected_fille_col_01  = st.selectbox("👧 Colonne : filles", colnames, key="fille_col_01")
           selected_garcon_col_01 = st.selectbox("👦 Colonne : garçons", colnames, key="garcon_col_01")
           selected_homme60_col_01 = st.selectbox("👴 Colonne : hommes 60+", colnames, key="homme60_col_01")
           selected_femme60_col_01 = st.selectbox("👵 Colonne : femmes 60+", colnames, key="femme60_col_01")
           # Vérifier que toutes les colonnes sont sélectionnées
           if not all([
               selected_homme_col_01, selected_femme_col_01, selected_fille_col_01,
               selected_garcon_col_01, selected_homme60_col_01, selected_femme60_col_01
               ]):
               st.warning("⚠️ Veuillez sélectionner toutes les colonnes nécessaires.")
           else:
               if st.button("📈 Lancer l'analyse"):    
                   try:
                       # Conversion en numérique
                       df_fmr_filtered[selected_homme_col_01]   = pd.to_numeric(df_fmr_filtered[selected_homme_col_01], errors='coerce')
                       df_fmr_filtered[selected_femme_col_01]   = pd.to_numeric(df_fmr_filtered[selected_femme_col_01], errors='coerce')
                       df_fmr_filtered[selected_fille_col_01]   = pd.to_numeric(df_fmr_filtered[selected_fille_col_01], errors='coerce')
                       df_fmr_filtered[selected_garcon_col_01]  = pd.to_numeric(df_fmr_filtered[selected_garcon_col_01], errors='coerce')
                       df_fmr_filtered[selected_homme60_col_01] = pd.to_numeric(df_fmr_filtered[selected_homme60_col_01], errors='coerce')
                       df_fmr_filtered[selected_femme60_col_01] = pd.to_numeric(df_fmr_filtered[selected_femme60_col_01], errors='coerce')
                       # Total global
                       total = st.session_state.get("total_personnes")
                       if total is None or total == 0:
                           total = (
                               df_fmr_filtered[selected_homme_col_01].sum() +
                               df_fmr_filtered[selected_femme_col_01].sum() +
                               df_fmr_filtered[selected_fille_col_01].sum() +
                               df_fmr_filtered[selected_garcon_col_01].sum() +
                               df_fmr_filtered[selected_homme60_col_01].sum() +
                               df_fmr_filtered[selected_femme60_col_01].sum()
                           )
                       # Calculs
                       pvo = df_fmr_filtered[selected_femme60_col_01].sum() + df_fmr_filtered[selected_homme60_col_01].sum()
                       homme  = round((df_fmr_filtered[selected_homme_col_01].sum() + df_fmr_filtered[selected_homme60_col_01].sum()) / total * 100, 2)
                       femme  = round((df_fmr_filtered[selected_femme_col_01].sum() + df_fmr_filtered[selected_femme60_col_01].sum()) / total * 100, 2)
                       garcon = round(df_fmr_filtered[selected_garcon_col_01].sum() / total * 100, 2)
                       fille  = round(df_fmr_filtered[selected_fille_col_01].sum() / total * 100, 2)
                       # Affichage
                       st.success(f"👥 Personnes vulnérables (60+) de  {selected_fmp_value_01} : **{int(pvo)}**")
                       st.info(f"👨 Hommes (avec 60+) de : {selected_fmp_value_01} : **{homme}%**")
                       st.info(f"👩 Femmes (avec 60+) de : {selected_fmp_value_01} : **{femme}%**")
                       st.info(f"👦 Garçons de : {selected_fmp_value_01} : **{garcon}%**")
                       st.info(f"👧 Filles  de : {selected_fmp_value_01}: **{fille}%**")
                   except Exception as e:
                       st.error(f"❌ Erreur lors du traitement : {e}")
        
        elif st.session_state.active_analysis == "depart par fmp":
            st.markdown(f"### 🏁 Pays de départ pour FMP : {selected_fmp_value_01}")
            st.markdown("### 🏁 Pays de départ")
            colnames = df_fmr_filtered.columns.tolist()
            depart_col = st.selectbox("🌍 Colonne : pays de départ", colnames, key="depart_col_01")
            depart_count_col = st.selectbox("🔢 Colonne : nombre de personnes", colnames, key="depart_count_col_01")
            if st.button("📈 Lancer l'analyse"):    
                if depart_col and depart_count_col:
                    try:
                        df_fmr_filtered[depart_count_col] = pd.to_numeric(df_fmr_filtered[depart_count_col], errors='coerce')
                        grouped = df_fmr_filtered.groupby(depart_col)[depart_count_col].sum() 
                        pourcentages = round((grouped / grouped.sum()) * 100, 2)
                        st.markdown(f"#### 📊 Pourcentage par pays de destination : {selected_fmp_value_01}")
                        st.dataframe(pourcentages.sort_values(ascending=False).head(6))
                    except Exception as e:
                        st.error(f"❌ Erreur lors de l'analyse : {e}")
        
        elif st.session_state.active_analysis == "destination par fmp":
           st.markdown(f"### 🏁 Analyse par pays de destination pour FMP : {selected_fmp_value_01}")
           colnames = df_fmr_filtered.columns.tolist()
           destination_col = st.selectbox("🌍 Colonne : pays de destination", colnames, key="destination_01")
           destination_count_col = st.selectbox("🔢 Colonne : nombre de personnes", colnames, key="destination_count_col_01")
           if st.button("📈 Lancer l'analyse"):
               if destination_col and destination_count_col:
                   try:
                       df_fmr_filtered[destination_count_col] = pd.to_numeric(df_fmr_filtered[destination_count_col], errors='coerce')
                       grouped = df_fmr_filtered.groupby(destination_col)[destination_count_col].sum()
                       pourcentages = round((grouped / grouped.sum()) * 100, 2)
                       st.markdown(f"#### 📊 Pourcentage par pays de destination : {selected_fmp_value_01}")
                       st.dataframe(pourcentages.sort_values(ascending=False).head(6))
                   except Exception as e:
                       st.error(f"❌ Erreur lors de l'analyse : {e}")




