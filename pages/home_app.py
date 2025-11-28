# app.py
import streamlit as st
import pandas as pd
from io import BytesIO
import requests
import os
import sys

# Ensure project root is on sys.path so the local 'Functions' package can be imported from 'pages'
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import only the function(s) actually used by this module instead of using a wildcard import
from Functions.manipExcel import valider_colonnes_selectionnees


def telecharger_fichier_google_drive(lien):
    id_fichier = lien.split('/')[-2]
    url = f"https://drive.google.com/uc?id={id_fichier}"
    response = requests.get(url)
    return BytesIO(response.content)

def main():
    st.title("Application de traitement Excel")
    st.write("Fournissez un lien Google Drive vers votre fichier Excel.")

    # Champ pour le lien Google Drive
    lien = st.text_input("Lien Google Drive vers le fichier Excel")

    # Liste des colonnes attendues
    colonnes_attendues = [
        "Ligne", "Numéro interne -Voy", "Parcours", "Js srv", "Direction",
        "Arrêt", "Heure", "Description", "Contexte service", "Position -ArV"
    ]

    if lien and st.button("Télécharger et traiter le fichier"):
        try:
            # Télécharger le fichier depuis Google Drive
            fichier_excel = telecharger_fichier_google_drive(lien)
            df = pd.read_excel(fichier_excel)

            st.subheader("Aperçu des données")
            st.dataframe(df.head())

            st.subheader("Colonnes disponibles")
            colonnes_disponibles = df.columns.tolist()
            st.write(colonnes_disponibles)

            # Sélectionner les colonnes pour le traitement
            st.subheader("Sélectionner les colonnes à traiter")
            colonnes_a_traiter = st.multiselect(
                "Choisissez les colonnes à inclure dans le traitement :",
                options=colonnes_disponibles,
                default=colonnes_disponibles
            )
            
            if st.button("Valider les colonnes sélectionnées"):
                if len(colonnes_a_traiter) == 0:
                    st.error("Veuillez sélectionner au moins une colonne.")
                else:
                    # Vérifier que les colonnes sélectionnées correspondent aux colonnes attendues
                    est_valide, message = valider_colonnes_selectionnees(colonnes_a_traiter, colonnes_attendues)

                    if est_valide:
                        st.session_state['colonnes_a_traiter'] = colonnes_a_traiter
                        st.session_state['df'] = df[colonnes_a_traiter]
                        st.session_state['page'] = "renommage"
                        st.experimental_rerun()
                    else:
                        st.error(message)
        except Exception as e:
            st.error(f"Une erreur est survenue lors du téléchargement ou du traitement du fichier : {e}")