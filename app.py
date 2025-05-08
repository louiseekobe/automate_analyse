import streamlit as st
import pandas as pd
from contain_pages import analyse, visualisation, analyse_by_fmp
# Config
st.set_page_config(
    page_title="Multipage App",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)


# Sidebar
st.sidebar.title("📂 Navigation")

pages = {
    "🏠 Accueil": "Accueil",
    "📊 Analyse générale": "Analyse",
    "📍 Analyse par FMP": "Analyse par fmp",
    "📈 Visualisation": "Visualisation"
}

selection = st.sidebar.radio("Choisissez une page :", list(pages.keys()))
page = pages[selection]

# Page Accueil
if page == "Accueil":
    st.title("Page d'accueil")
    st.write("📂 Chargez un fichier Excel avec plusieurs feuilles.")

    uploaded_file = st.file_uploader("Fichier Excel", type=["xlsx", "xls"])

    if uploaded_file is not None:
        try:
            # Lecture des feuilles + suppression des colonnes 'Unnamed'
            xls_raw = pd.read_excel(uploaded_file, sheet_name=None, index_col=None)
            xls = {
                name: df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
                for name, df in xls_raw.items()
            }

            # Sélection des feuilles pour FMR et Nationalité
            sheet_names = list(xls.keys())
            fmr_sheet = st.selectbox("📄 Feuille FMR :", sheet_names, key="fmr_sheet")
            nat_sheet = st.selectbox("📄 Feuille Nationalités :", sheet_names, key="nat_sheet")

            # Création des DataFrames
            df_fmr = xls[fmr_sheet]
            st.subheader("🔍 Aperçu FMR")
            st.dataframe(df_fmr.head(3))
            df_nat = xls[nat_sheet]
            st.subheader("🔍 Aperçu Nationalités")
            st.dataframe(df_nat.head(3))

            # Stockage dans la session
            st.session_state["df_fmr"] = df_fmr
            st.session_state["df_nat"] = df_nat
            st.session_state["excel_file"] = uploaded_file  # garde le fichier original

            # Fusion personnalisée
            st.markdown("### 🔗 Fusion des données")
            merge_col_fmr = st.selectbox("🧩 Colonne de jointure dans FMR", df_fmr.columns.tolist(), key="merge_col_fmr")
            merge_col_nat = st.selectbox("🧩 Colonne de jointure dans Nationalités", df_nat.columns.tolist(), key="merge_col_nat")

            if st.button("Fusionner les deux feuilles"):
                try:
                    # Conversion automatique des colonnes de jointure (si nécessaires)
                    df_nat[merge_col_nat] = df_nat[merge_col_nat].astype(str)
                    df_fmr[merge_col_fmr] = df_fmr[merge_col_fmr].astype(str)
                    # Fusionner les DataFrames
                    df_merged = pd.merge(
                        df_nat,
                        df_fmr,
                        left_on=merge_col_nat,
                        right_on=merge_col_fmr,
                        how="inner"
                    )
                    st.session_state["df_merged"] = df_merged
                    st.success(f"✅ Fusion réussie : {len(df_merged)} lignes.")
                    st.subheader("🔍 Aperçu du DataFrame fusionné")
                    st.dataframe(df_merged.head())

                except Exception as e:
                    st.error(f"❌ Erreur lors de la fusion : {e}")

        except Exception as e:
            st.error(f"Erreur lors du chargement : {e}")

# Page Analyse
elif page == "Analyse":
    analyse.show()
    
# Page Analyse
elif page == "Analyse par fmp":
    analyse_by_fmp.show()

# Page Visualisation
elif page == "Visualisation":
    visualisation.show()
