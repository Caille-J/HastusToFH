# app.py
import streamlit as st
import pandas as pd
import zipfile
from io import BytesIO
import requests
from Functions.processFiles import *
from pages.home_app import *

def main1():
    st.title("Application de traitement Excel")
    st.write("Fournissez un lien Google Drive vers votre fichier Excel.")

    # Champ pour le lien Google Drive
    lien = st.text_input("Lien Google Drive vers le fichier Excel")

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
                st.success("Colonnes sélectionnées avec succès !")

                if st.button("Lancer le traitement"):
                    with st.spinner("Traitement en cours..."):
                        # Sélection interactive des colonnes
                        columns_to_select = select_columns_interactively(df_voyages)

                        # Vérification du nombre de colonnes
                        new_column_names = ["Ligne", "Numéro interne -Voy", "Parcours", "Js srv", "Direction", "Arrêt", "Heure", "Description", "Contexte service", "Position -ArV"]
                        if len(columns_to_select) != len(new_column_names):
                            st.error("Le nombre de colonnes sélectionnées ne correspond pas aux noms de colonnes attendus. Veuillez réessayer.")
                        else:
                            # Renommer les colonnes
                            df_voyages.columns = new_column_names
                            st.success("Colonnes renommées avec succès !")

                            # Afficher un aperçu
                            st.subheader("Aperçu des données après renommage")
                            st.dataframe(df_voyages.head())

                            # Créer le mapping des arrêts
                            if 'Arrêt' in df_voyages.columns and 'Description' in df_voyages.columns:
                                stop_description_map = df_voyages.set_index('Arrêt')['Description'].to_dict()
                            else:
                                st.error("Les colonnes 'Arrêt' ou 'Description' sont manquantes. Impossible de créer le mapping des arrêts.")
                                stop_description_map = {}

                            # Traiter les données
                            st.subheader("Traitement des données...")
                            dfs_by_context = split_dataframe_by_contexte_service(df_voyages)
                            dfs_period_ligne = split_dataframe_by_ligne_from_dict(dfs_by_context)

                            # Liste pour stocker les DataFrames CSV
                            dfs = []

                            # Boucle de traitement
                            for period, dfs_by_ligne in dfs_period_ligne.items():
                                st.write(f"Traitement de la période : **{period}**")
                                for line_number, df_ligne in dfs_by_ligne.items():
                                    st.write(f"Traitement de la ligne : **{line_number}**")

                                    # Créer les DataFrames par direction et Js srv
                                    line_dfs_by_direction_js_srv = create_direction_js_srv_dfs(line_number, {line_number: df_ligne})
                                    if line_dfs_by_direction_js_srv:
                                        # Créer les DataFrames pour chaque voyage
                                        all_voyages_sorted_for_line = create_voyage_dataframes(line_dfs_by_direction_js_srv)

                                        # Générer les CSV
                                        for group_key in all_voyages_sorted_for_line.keys():
                                            direction, js_srv = group_key.split('_')
                                            merged_stops_list, _, _, _ = get_merged_stops_for_group(all_voyages_sorted_for_line, group_key)

                                            if merged_stops_list is not None:
                                                dfs.append(generate_timetable_csv_for_group(
                                                    line_number, period, direction, js_srv,
                                                    all_voyages_sorted_for_line, stop_description_map, merged_stops_list
                                                ))
                                            else:
                                                st.warning(f"Impossible de générer l'horaire pour le groupe {group_key} (arrêts manquants).")
                                    else:
                                        st.warning(f"Aucun DataFrame créé pour la ligne {line_number} (période {period}).")

                            # Générer le ZIP
                            if dfs:
                                buffer = BytesIO()
                                with zipfile.ZipFile(buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                                    for i, df_csv in enumerate(dfs):
                                        csv_buffer = BytesIO()
                                        df_csv.to_csv(csv_buffer, index=False)
                                        csv_buffer.seek(0)
                                        zip_file.writestr(f"horaire_{i}.csv", csv_buffer.getvalue())

                                buffer.seek(0)
                                st.success("Traitement terminé !")
                                st.download_button(
                                    label="Télécharger les horaires (ZIP)",
                                    data=buffer,
                                    file_name="horaires.zip",
                                    mime="application/zip"
                                )
                            else:
                                st.error("Aucun fichier CSV généré. Vérifiez les données et réessayez.")

        except FileNotFoundError:
            st.error("Le fichier n'a pas été trouvé. Vérifiez le lien Google Drive.")
        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")

if __name__ == "__main__":
    main()