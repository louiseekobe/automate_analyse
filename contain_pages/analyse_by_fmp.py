import streamlit as st
import pandas as pd

def show():
    st.title("🔍 Analyse Par FMP sélectionné")

    # ✅ Vérification que les DataFrames sont bien disponibles
    if "df_fmr" not in st.session_state or "df_nat" not in st.session_state or "df_merged" not in st.session_state:
        st.warning("⚠️ Les données n'ont pas été chargées ou fusionnées. Veuillez le faire dans la page d'accueil.")
        return

    # ✅ Récupération des DataFrames depuis la session
    df_fmr = st.session_state["df_fmr"]
    df_nat = st.session_state["df_nat"]
    df_merged = st.session_state["df_merged"]

    st.success("✅ Données chargées avec succès.")

    # 🔽 Sélection du FMP à analyser
    colnames = df_fmr.columns.tolist()
    selected_fmp_col = st.selectbox("🏷️ Colonne contenant les FMP :", colnames, key="selected_fmp_col")

    if selected_fmp_col:
        fmp_list = df_fmr[selected_fmp_col].dropna().unique().tolist()
        selected_fmp_value = st.selectbox("📍 Sélectionnez un FMP :", sorted(fmp_list), key="selected_fmp_value")

        # 🔁 DataFrames filtrés pour ce FMP uniquement
        df_fmr_filtered = df_fmr[df_fmr[selected_fmp_col] == selected_fmp_value]
        df_merged_filtered = df_merged[df_merged[selected_fmp_col] == selected_fmp_value]
    else:
        st.warning("⚠️ Aucune colonne FMP détectée.")
        return

    # Navigation des analyses avec menu persistant
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
        if st.button(label):
            st.session_state.active_analysis = key
            for state_key in list(st.session_state.keys()):
                if state_key.startswith("selected_"):
                    del st.session_state[state_key]

    if st.session_state.active_analysis == "personnes par fmp":
        st.markdown(f"### 👥 Analyse du nombre de personnes déplacées : {selected_fmp_value}")
        colnames = df_fmr_filtered.columns.tolist()
        count_col = st.selectbox("🔢 Colonne : nombre total de personnes", colnames, key="selected_count")
        date_col = st.selectbox("📅 Colonne : date de l'enquête", colnames, key="selected_date")
        if st.button("Lancer l'analyse"):   
            if count_col and date_col:
                try:
                    df_fmr_filtered[count_col] = pd.to_numeric(df_fmr_filtered[count_col], errors='coerce')
                    df_fmr_filtered[date_col] = pd.to_datetime(df_fmr_filtered[date_col], errors='coerce')
                    total = df_fmr_filtered[count_col].sum(skipna=True)
                    nb_jours = len(df_fmr_filtered[date_col].dt.date.unique())
                    moyenne = round(total / nb_jours, 2) if nb_jours else 0
                    st.success(f"✅ Total : {int(total)} personnes")
                    st.info(f"📊 Moyenne journalière : {moyenne} personnes/jour sur {nb_jours} jours")
                    st.session_state["total_personnes"] = total
                except Exception as e:
                    st.error(f"Erreur : {e}")

    elif st.session_state.active_analysis == "fmp selectionne":
        st.markdown(f"### 📦 Informations FMP : {selected_fmp_value}")
        colnames = df_fmr_filtered.columns.tolist()
        fmp_col = st.selectbox("🏷️ Colonne : nom FMP", colnames, key="selected_fmp")
        count_col = st.selectbox("🔢 Colonne : nombre total de personnes", colnames, key="selected_count_fmp")
        type_flux_col = st.selectbox("🔄 Colonne : type de flux", colnames, key="selected_flux_fmp")
        if st.button("Lancer l'analyse"):    
            if fmp_col and count_col and type_flux_col:
                try:
                    df_fmr_filtered[count_col] = pd.to_numeric(df_fmr_filtered[count_col], errors='coerce')
                    grouped = df_fmr_filtered.dropna(subset=[type_flux_col, count_col]) \
                                     .groupby(type_flux_col)[count_col].sum()
                    st.markdown(f"#### 🔄 Nombre de personnes par type de flux pour : {selected_fmp_value}")
                    st.dataframe(grouped)
                    pourcentages = round((grouped / grouped.sum()) * 100, 2)
                    st.markdown(f"#### 📊 Pourcentage par type de flux pour : {selected_fmp_value}")
                    st.dataframe(pourcentages)
                except Exception as e:
                    st.error(f"Erreur : {e}")

    elif st.session_state.active_analysis == "nationalites par fmp":
        st.markdown(f"### 🌐 Nationalités pour FMP : {selected_fmp_value}")
        colnames = df_merged_filtered.columns.tolist()
        nat_col = st.selectbox("🌍 Colonne : nationalité", colnames, key="selected_nat")
        count_col = st.selectbox("🔢 Colonne : nombre de personnes", colnames, key="selected_nat_count")
        flux_col = st.selectbox("🔄 Colonne : type de flux", colnames, key="selected_nat_flux")
        if st.button("Lancer l'analyse"):    
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
                    st.markdown(f"#### 📉 Répartition (%) par flux et nationalité dans : {selected_fmp_value}")
                    st.dataframe(pivot_percent.sort_values(by=pivot_percent.columns[0], ascending=False))
                except Exception as e:
                    st.error(f"Erreur : {e}")

    elif st.session_state.active_analysis == "profil par fmp":
        st.markdown(f"### 🧭 Profil des voyageurs pour FMP : {selected_fmp_value}")
        colnames = df_fmr_filtered.columns.tolist()
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
                    df_fmr_filtered[selected_homme_col]   = pd.to_numeric(df_fmr_filtered[selected_homme_col], errors='coerce')
                    df_fmr_filtered[selected_femme_col]   = pd.to_numeric(df_fmr_filtered[selected_femme_col], errors='coerce')
                    df_fmr_filtered[selected_fille_col]   = pd.to_numeric(df_fmr_filtered[selected_fille_col], errors='coerce')
                    df_fmr_filtered[selected_garcon_col]  = pd.to_numeric(df_fmr_filtered[selected_garcon_col], errors='coerce')
                    df_fmr_filtered[selected_homme60_col] = pd.to_numeric(df_fmr_filtered[selected_homme60_col], errors='coerce')
                    df_fmr_filtered[selected_femme60_col] = pd.to_numeric(df_fmr_filtered[selected_femme60_col], errors='coerce')
                    # Total global
                    total = st.session_state.get("total_personnes")
                    if total is None or total == 0:
                        total = (
                            df_fmr_filtered[selected_homme_col].sum() +
                            df_fmr_filtered[selected_femme_col].sum() +
                            df_fmr_filtered[selected_fille_col].sum() +
                            df_fmr_filtered[selected_garcon_col].sum() +
                            df_fmr_filtered[selected_homme60_col].sum() +
                            df_fmr_filtered[selected_femme60_col].sum()
                        )
                    # Calculs
                    pvo = df_fmr_filtered[selected_femme60_col].sum() + df_fmr_filtered[selected_homme60_col].sum()
                    homme  = round((df_fmr_filtered[selected_homme_col].sum() + df_fmr_filtered[selected_homme60_col].sum()) / total * 100, 2)
                    femme  = round((df_fmr_filtered[selected_femme_col].sum() + df_fmr_filtered[selected_femme60_col].sum()) / total * 100, 2)
                    garcon = round(df_fmr_filtered[selected_garcon_col].sum() / total * 100, 2)
                    fille  = round(df_fmr_filtered[selected_fille_col].sum() / total * 100, 2)
                    # Affichage
                    st.success(f"👥 Personnes vulnérables (60+) de  {selected_fmp_value} : **{int(pvo)}**")
                    st.info(f"👨 Hommes (avec 60+) de : {selected_fmp_value} : **{homme}%**")
                    st.info(f"👩 Femmes (avec 60+) de : {selected_fmp_value} : **{femme}%**")
                    st.info(f"👦 Garçons de : {selected_fmp_value} : **{garcon}%**")
                    st.info(f"👧 Filles  de : {selected_fmp_value}: **{fille}%**")
                except Exception as e:
                    st.error(f"❌ Erreur lors du traitement : {e}")

    elif st.session_state.active_analysis == "depart par fmp":
        st.markdown(f"### 🏁 Pays de départ pour FMP : {selected_fmp_value}")
        st.markdown("### 🏁 Pays de départ")
        colnames = df_fmr_filtered.columns.tolist()
        depart_col = st.selectbox("🌍 Colonne : pays de départ", colnames, key="depart_col")
        depart_count_col = st.selectbox("🔢 Colonne : nombre de personnes", colnames, key="depart_count_col")
        if st.button("Lancer l'analyse"):    
            if depart_col and depart_count_col:
                try:
                    df_fmr_filtered[depart_count_col] = pd.to_numeric(df_fmr_filtered[depart_count_col], errors='coerce')
                    grouped = df_fmr_filtered.groupby(depart_col)[depart_count_col].sum() 
                    pourcentages = round((grouped / grouped.sum()) * 100, 2)
                    st.markdown(f"#### 📊 Pourcentage par pays de destination : {selected_fmp_value}")
                    st.dataframe(pourcentages.sort_values(ascending=False).head(6))
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'analyse : {e}")

    elif st.session_state.active_analysis == "destination par fmp":
        st.markdown(f"### 🏁 Analyse par pays de destination pour FMP : {selected_fmp_value}")
        colnames = df_fmr_filtered.columns.tolist()
        destination_col = st.selectbox("🌍 Colonne : pays de destination", colnames, key="destination")
        destination_count_col = st.selectbox("🔢 Colonne : nombre de personnes", colnames, key="destination_count_col")
        if st.button("Lancer l'analyse"):
            if destination_col and destination_count_col:
                try:
                    df_fmr_filtered[destination_count_col] = pd.to_numeric(df_fmr_filtered[destination_count_col], errors='coerce')
                    grouped = df_fmr_filtered.groupby(destination_col)[destination_count_col].sum()
                    pourcentages = round((grouped / grouped.sum()) * 100, 2)
                    st.markdown(f"#### 📊 Pourcentage par pays de destination : {selected_fmp_value}")
                    st.dataframe(pourcentages.sort_values(ascending=False).head(6))
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'analyse : {e}")

