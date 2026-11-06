from pathlib import Path

import pandas as pd
import streamlit as st

DOSSIER = Path(__file__).parent / "donnees"


@st.cache_data
def charger_donnees():
    return pd.read_csv(DOSSIER / "consommation_propre.csv")


st.set_page_config(page_title="L'électricité dans 12 quartiers", page_icon="⚡", layout="wide")

st.title("L'électricité dans 12 quartiers")
st.caption("Relevés mensuels de janvier 2024 à décembre 2025. Données fictives.")

donnees = charger_donnees()

st.markdown(
    "Ce tableau de bord présente **279 relevés mensuels** de consommation électrique "
    "dans **12 quartiers** de Port-au-Prince, Delmas, Pétion-Ville et Cap-Haïtien."
)
st.markdown(
    "L'objectif : comprendre si la consommation suit la **chaleur** ou les **heures de courant**."
)

# --- Filtres sidebar ---
communes_disponibles = sorted(donnees["commune"].unique())
communes_choisies = st.sidebar.multiselect(
    "Communes", communes_disponibles, default=communes_disponibles
)
annee_choisie = st.sidebar.selectbox("Année", [2025, 2024])

if not communes_choisies:
    st.warning("Veuillez sélectionner au moins une commune dans la barre latérale.")
    st.stop()

filtrees = donnees[donnees["commune"].isin(communes_choisies)]
filtrees = filtrees[filtrees["annee"] == annee_choisie]

# --- 3 indicateurs ---
col1, col2, col3 = st.columns(3)

conso_totale = filtrees["kwh"].sum() / 1_000_000
kwh_par_abonne = filtrees["kwh_par_abonne"].mean()
heures_moy = filtrees["heures_courant"].mean()

col1.metric("Consommation totale", f"{conso_totale:.2f} M kWh")
col2.metric("kWh par abonné", f"{kwh_par_abonne:.1f}")
col3.metric("Heures de courant (moy.)", f"{heures_moy:.1f} h")

st.dataframe(filtrees.head(10), hide_index=True)