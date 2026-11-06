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
col1.metric("Consommation totale", f"{filtrees['kwh'].sum() / 1_000_000:.2f} M kWh")
col2.metric("kWh par abonné", f"{filtrees['kwh_par_abonne'].mean():.1f}")
col3.metric("Heures de courant (moy.)", f"{filtrees['heures_courant'].mean():.1f} h")

# --- 5 onglets ---
onglet1, onglet2, onglet3, onglet4, onglet5 = st.tabs([
    "Quartiers", "Évolution", "Chaleur ou courant", "Coupures", "Hors norme"
])

# Onglet 1 : consommation par type
with onglet1:
    st.subheader("Consommation par abonné selon le type de quartier")
    par_type = filtrees.groupby("type")["kwh_par_abonne"].mean().round(1)
    st.bar_chart(par_type, horizontal=True)
    st.write(f"Commercial : {par_type.get('Commercial', 0):.1f} kWh/abonné, "
             f"Résidentiel : {par_type.get('Résidentiel', 0):.1f} kWh/abonné.")

# Onglet 2 : évolution par commune
with onglet2:
    st.subheader("Évolution mensuelle du kWh par abonné, par commune")
    evolution = filtrees.pivot_table(index="mois", columns="commune",
                                     values="kwh_par_abonne", aggfunc="mean")
    st.line_chart(evolution)
    totaux = filtrees.groupby("commune")["kwh"].sum() / 1_000_000
    top = totaux.idxmax()
    st.write(f"Commune la plus consommatrice en {annee_choisie} : **{top}** "
             f"({totaux.max():.2f} M kWh).")

# Onglet 3 : chaleur ou courant
with onglet3:
    st.subheader("Plus de courant, plus de consommation")
    residentiel = filtrees[filtrees["type"] == "Résidentiel"]
    st.scatter_chart(residentiel, x="heures_courant", y="kwh_par_abonne", color="commune",
                     x_label="Heures de courant par jour", y_label="kWh par abonné")
    courant = residentiel["heures_courant"].corr(residentiel["kwh_par_abonne"])
    chaleur = residentiel["temperature_c"].corr(residentiel["kwh_par_abonne"])
    st.write(f"Quartiers résidentiels : corrélation de **{courant:.2f}** avec les heures "
             f"de courant, **{chaleur:.2f}** avec la température.")

# Onglet 4 : coupures
with onglet4:
    st.subheader("Les coupures les plus longues")
    medianes = filtrees.groupby("commune")["heures_courant"].median().round(1)
    st.bar_chart(medianes, horizontal=True)
    faibles = filtrees[filtrees["heures_courant"] < 8]
    st.write(f"{len(faibles)} relevé(s) sous 8 heures de courant sur la période filtrée.")

# Onglet 5 : hors norme
with onglet5:
    st.subheader("Les 5 plus grosses consommations")
    top5 = filtrees.nlargest(5, "kwh")[["mois", "quartier", "type", "kwh"]]
    st.dataframe(top5, hide_index=True)
    premier = top5.iloc[0]
    st.write(f"Le pic est à **{premier['quartier']}** en {premier['mois']} "
             f"avec {premier['kwh']:.0f} kWh.")