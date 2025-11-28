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

# Liste des colonnes attendues
colonnes_attendues = [
    "Ligne", "Numéro interne -Voy", "Parcours", "Js srv", "Direction",
    "Arrêt", "Heure", "Description", "Contexte service", "Position -ArV"
]
def telecharger_fichier_google_drive(lien):
    # Reset session state to start fresh and return a BytesIO stream on success
    st.session_state['fichier_excel'] = None

    # Try to extract a Drive file id from various link formats (d/<id>/, id=<id>, or last segment)
    id_fichier = None
    if 'id=' in lien:
        import urllib.parse as urlparse
def main():
    # Initialize session state keys to avoid KeyError on first run
    if 'fichier_excel' not in st.session_state:
        st.session_state['fichier_excel'] = None
    if 'page' not in st.session_state:
        st.session_state['page'] = None

    if st.session_state.get('fichier_excel') is None:

        st.title("Application de traitement Excel")
        st.write("Fournissez un lien Google Drive vers votre fichier Excel.")

        # Champ pour le lien Google Drive
        lien = st.text_input("Lien Google Drive vers le fichier Excel")

        if lien and st.button("Télécharger et traiter le fichier"):
            try:
                # Télécharger le fichier depuis Google Drive
                fichier_excel_stream = telecharger_fichier_google_drive(lien)
                df = pd.read_excel(fichier_excel_stream)
    if not id_fichier:
        raise ValueError("Impossible d'extraire l'identifiant de fichier depuis le lien Google Drive fourni.")

    url = f"https://drive.google.com/uc?id={id_fichier}&export=download"
    response = requests.get(url, allow_redirects=True, timeout=10)

    if response.status_code != 200:
        raise ValueError(f"Échec du téléchargement depuis Google Drive (HTTP {response.status_code}).")

    fichier_stream = BytesIO(response.content)
    fichier_stream.seek(0)
    st.session_state['fichier_excel'] = fichier_stream
    return fichier_stream

def main():
    if st.session_state['fichier_excel'] == None :

        st.title("Application de traitement Excel")
        st.write("Fournissez un lien Google Drive vers votre fichier Excel.")

        # Champ pour le lien Google Drive
        lien = st.text_input("Lien Google Drive vers le fichier Excel")

        if lien and st.button("Télécharger et traiter le fichier"):
            try:
                # Télécharger le fichier depuis Google Drive
                fichier_excel = telecharger_fichier_google_drive(lien)
                df = pd.read_excel(fichier_excel)
            try:
                if len(colonnes_a_traiter) == 0:
                    est_valide = False
                    message = "Veuillez sélectionner au moins une colonne."
                    st.error(message)
                else:
                    # Vérifier que les colonnes sélectionnées correspondent aux colonnes attendues
                    est_valide, message = valider_colonnes_selectionnees(colonnes_a_traiter, colonnes_attendues)

                if est_valide:
                    st.session_state['colonnes_a_traiter'] = colonnes_a_traiter
                    st.session_state['df'] = df[colonnes_a_traiter]
                    st.session_state['page'] = "renommage"
                    st.success(message)
                    st.experimental_rerun()
                else:
                    st.error(message)
            except Exception as e:
                st.error(f"Une erreur est survenue lors de la validation des colonnes : {e}")chier : {e}")
    else : 
        df = pd.read_excel(st.session_state['fichier_excel'])
        st.subheader("Colonnes disponibles")
        colonnes_disponibles = df.columns.tolist()
        st.write(colonnes_attendues)

        st.write(colonnes_disponibles)

        # Sélectionner les colonnes pour le traitement
        st.subheader("Sélectionner les colonnes à traiter")
        colonnes_a_traiter = st.multiselect(
            "Choisissez les colonnes à inclure dans le traitement :",
            options=colonnes_disponibles,
            default=colonnes_disponibles
        )

        if st.button("Valider les colonnes sélectionnées"):
            try :
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
                    st.success(message)
                else:
                    st.error(message)
            except Exception as e:
                st.error(f"Une erreur est survenue lors de la validation des colonnes : {e}")   