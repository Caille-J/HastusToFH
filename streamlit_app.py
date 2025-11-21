# app.py
import streamlit as st
import pandas as pd
from io import BytesIO
import requests

# Fonction pour télécharger le fichier depuis Google Drive
def telecharger_fichier_google_drive(lien):
    id_fichier = lien.split('/')[-2]
    url = f"https://drive.google.com/uc?id={id_fichier}"
    response = requests.get(url)
    return BytesIO(response.content)

# Fonction pour afficher la première page
def page_selection_colonnes():
    st.title("Étape 1 : Sélection des colonnes")
    st.write("Veuillez fournir un lien Google Drive vers votre fichier Excel.")

    # Champ pour le lien Google Drive
    lien = st.text_input("Lien Google Drive vers le fichier Excel")

    if lien:
        try:
            # Télécharger le fichier depuis Google Drive
            fichier_excel = telecharger_fichier_google_drive(lien)
            df = pd.read_excel(fichier_excel)

            st.subheader("Aperçu des données")
            st.dataframe(df.head())

            st.subheader("Colonnes disponibles dans le fichier")
            colonnes_disponibles = df.columns.tolist()
            st.write(colonnes_disponibles)

            # Indication des colonnes à conserver
            st.markdown("""
            **Colonnes à conserver (obligatoires) :**
            - Ligne
            - Numéro interne -Voy
            - Parcours
            - Js srv
            - Direction
            - Arrêt
            - Heure
            - Description
            - Contexte service
            - Position -ArV
            """)

            # Sélection des colonnes
            st.subheader("Sélectionnez les colonnes à conserver")
            colonnes_a_traiter = st.multiselect(
                "Choisissez les colonnes à inclure dans le traitement :",
                options=colonnes_disponibles,
                default=colonnes_disponibles
            )

            # Bouton de validation
            if st.button("Valider les colonnes sélectionnées"):
                if len(colonnes_a_traiter) == 0:
                    st.error("Veuillez sélectionner au moins une colonne.")
                else:
                    st.session_state['colonnes_a_traiter'] = colonnes_a_traiter
                    st.session_state['df'] = df[colonnes_a_traiter]
                    st.session_state['page'] = "renommage"
                    st.experimental_rerun()

        except Exception as e:
            st.error(f"Erreur lors du téléchargement ou de la lecture du fichier : {e}")

# Fonction pour afficher la page de renommage
def page_renommage_colonnes():
    st.title("Étape 2 : Renommage des colonnes")

    # Récupérer les données de la session
    colonnes_a_traiter = st.session_state.get('colonnes_a_traiter', [])
    df = st.session_state.get('df', pd.DataFrame())

    st.write("Voici les colonnes que vous avez sélectionnées :")
    st.write(colonnes_a_traiter)

    st.subheader("Aperçu des données avec les colonnes sélectionnées")
    st.dataframe(df.head())

    # Interface pour renommer les colonnes
    st.subheader("Renommez les colonnes")

    new_column_names = [
        "Ligne", "Numéro interne -Voy", "Parcours", "Js srv", "Direction",
        "Arrêt", "Heure", "Description", "Contexte service", "Position -ArV"
    ]

    # Créer un dictionnaire pour le renommage
    renommage = {}
    for i, colonne in enumerate(colonnes_a_traiter):
        renommage[colonne] = st.selectbox(
            f"Renommer '{colonne}' en :",
            options=new_column_names,
            index=i if i < len(new_column_names) else 0
        )

    # Bouton pour valider le renommage
    if st.button("Valider le renommage"):
        # Appliquer le renommage
        df_renomme = df.rename(columns=renommage)
        st.session_state['df_renomme'] = df_renomme
        st.success("Colonnes renommées avec succès !")
        st.dataframe(df_renomme.head())

        # Bouton pour passer à l'étape suivante
        if st.button("Lancer le traitement"):
            st.write("Traitement en cours...")

# Gestion de la navigation entre les pages
def main():
    if 'page' not in st.session_state:
        st.session_state['page'] = "selection"

    if st.session_state['page'] == "selection":
        page_selection_colonnes()
    elif st.session_state['page'] == "renommage":
        page_renommage_colonnes()

if __name__ == "__main__":
    main()
