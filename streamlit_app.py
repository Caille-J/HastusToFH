# app.py
import streamlit as st
import pandas as pd
import zipfile
from io import BytesIO
import requests
from ma_fonction import traiter_excel

def telecharger_fichier_google_drive(lien):
    id_fichier = lien.split('/')[-2]
    url = f"https://drive.google.com/uc?id={id_fichier}"
    response = requests.get(url)
    return BytesIO(response.content)

def main():
    st.title("Application de traitement Excel")
    st.write("Fournissez un lien Google Drive vers votre fichier Excel.")

    lien = st.text_input("Lien Google Drive vers le fichier Excel")

    if lien:
        try:
            fichier_excel = telecharger_fichier_google_drive(lien)
            df = pd.read_excel(fichier_excel)

            st.subheader("Aperçu des données")
            st.dataframe(df.head())

            st.subheader("Colonnes disponibles")
            colonnes_disponibles = df.columns.tolist()
            st.write(colonnes_disponibles)

            # Réarranger les colonnes
            st.subheader("Réarranger les colonnes (glisser-déposer)")
            colonnes_rearrangees = st.multiselect(
                "Sélectionnez l'ordre des colonnes :",
                options=colonnes_disponibles,
                default=colonnes_disponibles
            )

            # Sélectionner les colonnes pour le traitement
            st.subheader("Sélectionner les colonnes à traiter")
            colonnes_a_traiter = st.multiselect(
                "Choisissez les colonnes à inclure dans le traitement :",
                options=colonnes_disponibles,
                default=colonnes_disponibles
            )

            if colonnes_a_traiter:
                df_selectionne = df[colonnes_a_traiter]

                if st.button("Lancer le traitement"):
                    # Exécuter la fonction personnalisée
                    #dfs = traiter_excel
                    dfs= (df_selectionne)

                    # Créer un dossier ZIP en mémoire
                    buffer = BytesIO()
                    with zipfile.ZipFile(buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                        for i, df_csv in enumerate(dfs):
                            csv_buffer = BytesIO()
                            df_csv.to_csv(csv_buffer, index=False)
                            csv_buffer.seek(0)
                            zip_file.writestr(f"fichier_{i}.csv", csv_buffer.getvalue())

                    # Préparer le téléchargement du ZIP
                    buffer.seek(0)
                    st.download_button(
                        label="Télécharger le dossier ZIP",
                        data=buffer,
                        file_name="resultats.zip",
                        mime="application/zip"
                    )

        except Exception as e:
            st.error(f"Erreur : {e}")

if __name__ == "__main__":
    main()