# app.py
import streamlit as st
import pandas as pd
import zipfile
from io import BytesIO
import requests
from processFiles import *


def telecharger_fichier_google_drive(lien):
    # Extraire l'ID du fichier Google Drive
    id_fichier = lien.split('/')[-2]
    url = f"https://drive.google.com/uc?id={id_fichier}"
    response = requests.get(url)
    return BytesIO(response.content)

def main():
    st.title("Application de traitement Excel")
    st.write("Fournissez un lien Google Drive vers votre fichier Excel.")

    # Champ pour le lien Google Drive
    lien = st.text_input("Lien Google Drive vers le fichier Excel")
    dfs = []
   
    if lien:
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

            if colonnes_a_traiter:
                df_voyages = df[colonnes_a_traiter]

            # Exécuter la fonction personnalisée
        except FileNotFoundError:
          st.write(f"Error: The file was not found at {lien}")
          st.write("Please make sure the file exists and the path is correct.")
          # Exit or handle the error appropriately
          df_voyages = None # Set df_voyages to None to prevent further processing       
            
        TotalVoyages = None # Initialize TotalVoyages outside the if block

        if st.button("Lancer le traitement") and df_voyages is not None:
        # Select the specified columns interactively
          columns_to_select = select_columns_interactively(df_voyages)
          TotalVoyages = df_voyages[columns_to_select]    
            
          # Define the new column names in the desired order
          new_column_names = ["Ligne", "Numéro interne -Voy", "Parcours", "Js srv", "Direction", "Arrêt", "Heure", "Description", "Contexte service", "Position -ArV"]

          # Check if the number of selected columns matches the number of new column names
          if len(columns_to_select) == len(new_column_names):
          # Rename the columns
            TotalVoyages.columns = new_column_names
            st.write("Columns renamed successfully.")
        else:
            st.write("Warning: Number of selected columns does not match the number of specified new column names. Columns were not renamed.")


        # Display the first few rows of the new DataFrame
        st.dataframe(TotalVoyages.head())

        # Create a mapping from 'Arrêt1' to 'Description arrêt' using the first Dataframe
        # Assuming the Description arrêt is consistent for a given Arrêt1 across voyages
        # This part might need adjustment based on selected columns, assuming 'Arrêt' and 'Description' are selected  
        if 'Arrêt' in TotalVoyages.columns and 'Description' in TotalVoyages.columns:
          stop_description_map = TotalVoyages.set_index('Arrêt')['Description'].to_dict()
        else:
          st.write("Warning: 'Arrêt' or 'Description' column not selected. Cannot create stop description map.")
          stop_description_map = {}

        st.write("\n DataFrame created:")
        st.write(f"  TotalVoyages")    
            
        # Dataframe des periodes
        dfs_by_context = split_dataframe_by_contexte_service(TotalVoyages)

        # Dataframe des periodes avec leurs dataframe de lignes
        dfs_period_ligne = split_dataframe_by_ligne_from_dict(dfs_by_context)

        # Loop through periods, lines, directions, and service days
        for period, dfs_by_ligne in dfs_period_ligne.items():
          st.write(f"\nProcessing Period: {period}")
          for line_number, df_ligne in dfs_by_ligne.items():
            st.write(f"\nProcessing Ligne: {line_number}")
            # Create DataFrames by direction and Js srv for the current line and period
            line_dfs_by_direction_js_srv = create_direction_js_srv_dfs(line_number, {line_number: df_ligne})

            if line_dfs_by_direction_js_srv:
                # Create DataFrames for each voyage, sorted by Position -ArV
                all_voyages_sorted_for_line = create_voyage_dataframes(line_dfs_by_direction_js_srv)

                # Generate CSV for each Direction_Js srv group within the current line and period
                for group_key in all_voyages_sorted_for_line.keys():
                    st.write(f"Generating timetable for group: {group_key}")
                    # Extract direction and js_srv from the group_key
                    direction, js_srv = group_key.split('_')
                    # Get the merged stops list for the group before calling the function
                    merged_stops_list, _, _, _ = get_merged_stops_for_group(all_voyages_sorted_for_line, group_key)
                    if merged_stops_list is not None:
                         dfs.append(generate_timetable_csv_for_group(line_number, period, direction, js_srv, all_voyages_sorted_for_line, stop_description_map, merged_stops_list))
                    else:
                       st.write(f"Could not generate timetable for group {group_key} due to missing merged stops.")
            else:
                st.write(f"Could not create direction/Js srv DataFrames for Ligne {line_number} in Period {period}.")    
            
            


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

if __name__ == "__main__":
    main()