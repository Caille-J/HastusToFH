import pandas as pd
import io # Import io module for StringIO

def insert_list_at_position(main_list, list_to_insert, position):
  """Inserts a list into another list at a specified position.

  Args:
    main_list: The list to insert into.
    list_to_insert: The list to be inserted.
    position: The index at which to insert the list.

  Returns:
    A new list with the inserted elements.
  """
  if position < 0 or position > len(main_list):
    raise IndexError("Position out of bounds")
  return main_list[:position] + list_to_insert + main_list[position:]




def compare_and_merge_lists(list1, list2):
    """Compares two lists of strings, identifies differences, and merges.

    Args:
        list1: The first list of strings.
        list2: The second list of strings.

    Returns:
        A dictionary containing the comparison results and the merged list.
    """
    differences = []
    are_identical = True
    merged_list = [] # Create a copy to modify

    # indicateur pour savoir dans quel cas on se trouve,-1 pour avant, 0 pour dedans, sup à len listRef pour après
    ind = -1
    # on met la liste la plus longue en réf pour avoir le plus de chance de tout avoir
    listRef, listWork = list1, list2
    if len(list1) < len(list2) :
        listRef, listWork = list2, list1
    # indice de parcours
    j = 0

    # element manquant dans une liste à ajouter
    listLack = []
    merged_list = [] # Create a copy to modify

    #Boucle de travail
    while j < len(listWork):
      arretRef = listRef[0]  # récupere l'arret de la liste de référence
      arret = listWork[j]   # récupere l'arret de la liste de travail
      if arret in listRef :
        i = 0
        while i < len(listRef) and arretRef != arret :
          i = i + 1
          arretRef = listRef[i]
        listRef = insert_list_at_position(listRef,listLack,i)
        listLack = []
      else :
        are_identical = False
        listLack.append(arret)  # sinon ajout de l'arrêt manquant dans une liste des éléments manquants
      j = j + 1
    merged_list = insert_list_at_position(listRef,listLack,len(listRef))
    return merged_list



def select_columns_interactively(df):
    """Reads column headers from a DataFrame and prompts the user to select columns.

    Args:
        df: The input DataFrame.

    Returns:
        A list of column names selected by the user.
    """
    print("Available columns:")
    for i, col in enumerate(df.columns):
        print(f"{i}: {col}")

    selected_indices_str = "0,1,2,3,6,7,8,9,10,11" # input("Enter the numbers of the columns you want to keep, separated by commas (e.g., 0, 2, 5): ")
    selected_indices = [int(x.strip()) for x in selected_indices_str.split(',')]

    selected_columns = [df.columns[i] for i in selected_indices]
    return selected_columns


def split_dataframe_by_contexte_service(df):
    """Splits a DataFrame into multiple DataFrames based on unique values in 'Contexte service'.

    Args:
        df: The input DataFrame with a 'Contexte service' column.

    Returns:
        A dictionary where keys are the unique values from 'Contexte service'
        and values are the corresponding DataFrames.
    """
    if 'Contexte service' not in df.columns:
        print("Error: 'Contexte service' column not found in the DataFrame.")
        return {}

    dfs_by_contexte = {}
    unique_contextes = df['Contexte service'].unique()

    print("Creating DataFrames for each 'Contexte service':")
    for contexte in unique_contextes:
        df_name = f"dfs_{contexte}"
        dfs_by_contexte[contexte] = df[df['Contexte service'] == contexte].copy()
        print(f"  Created DataFrame: {df_name} with shape {dfs_by_contexte[contexte].shape}")

    print("\nAll DataFrames created:")
    for contexte in dfs_by_contexte.keys():
        print(f"- dfs_{contexte}")

    return dfs_by_contexte

def split_dataframe_by_ligne_from_dict(dfs_dict):
    """Splits DataFrames within a dictionary based on unique values in 'Ligne'.

    Args:
        dfs_dict: A dictionary where keys are identifiers and values are DataFrames
                  with a 'Ligne' column.

    Returns:
        A nested dictionary where the first level keys are the keys from the input
        dictionary, and the second level keys are the unique values from 'Ligne'
        in the corresponding DataFrame, and the values are the split DataFrames.
    """
    nested_dfs_by_ligne = {}

    for dict_key, df in dfs_dict.items():
        if 'Ligne' not in df.columns:
            print(f"Error: 'Ligne' column not found in the DataFrame for key '{dict_key}'. Skipping.")
            continue

        dfs_by_ligne = {}
        unique_lignes = df['Ligne'].unique()

        print(f"\n\nCreating DataFrames for each 'Ligne' within '{dict_key}':")
        for ligne in unique_lignes:
            # Create a unique name for the dataframe based on the original key and line number
            df_name = f"df_{dict_key}_ligne_{ligne}"
            dfs_by_ligne[ligne] = df[df['Ligne'] == ligne].copy()
            print(f"  Created DataFrame: {df_name} with shape {dfs_by_ligne[ligne].shape}")

        nested_dfs_by_ligne[dict_key] = dfs_by_ligne
        print(f"\nAll DataFrames created for '{dict_key}':")
        for ligne in dfs_by_ligne.keys():
            print(f"- df_{dict_key}_ligne_{ligne}")

    return nested_dfs_by_ligne

def create_direction_js_srv_dfs(line_number, dfs_ligne):
    """
    Creates a nested dictionary of DataFrames for a given line number,
    organized by direction and Js srv.

    Args:
        line_number: The line number to process.
        dfs_by_ligne: A dictionary containing DataFrames grouped by line number.

    Returns:
        A nested dictionary where the first level keys are 'Direction'
        ('Aller', 'Retour'), the second level keys are 'Js srv', and the
        values are DataFrames for that specific direction and Js srv.
    """
    if line_number not in dfs_ligne:
        print(f"Line number {line_number} not found in dfs_by_ligne.")
        return None

    df_ligne = dfs_ligne[line_number]

    dfs_by_direction_js_srv = {}

    # Filter the DataFrame by "Direction"
    df_aller = df_ligne[df_ligne['Direction'] == 'Aller'].copy()
    df_retour = df_ligne[df_ligne['Direction'] == 'Retour'].copy()

    dfs_by_direction_js_srv['Aller'] = {}
    dfs_by_direction_js_srv['Retour'] = {}

    # Get unique 'Js srv' values for "Aller" and "Retour"
    unique_js_srv_aller = df_aller['Js srv'].unique()
    unique_js_srv_retour = df_retour['Js srv'].unique()

    # Create DataFrames for each 'Js srv' within the "Aller" dictionary
    for js_srv in unique_js_srv_aller:
      dfs_by_direction_js_srv['Aller'][js_srv] = df_aller[df_aller['Js srv'] == js_srv].copy()

    # Create DataFrames for each 'Js srv' within the "Retour" dictionary
    for js_srv in unique_js_srv_retour:
      dfs_by_direction_js_srv['Retour'][js_srv] = df_retour[df_retour['Js srv'] == js_srv].copy()

    print(f"DataFrames created for Ligne {line_number}:")
    for direction, dfs_by_js_srv in dfs_by_direction_js_srv.items():
        print(f"  Direction: {direction}")
        for js_srv, df in dfs_by_js_srv.items():
            print(f"    Js srv: {js_srv}, shape: {df.shape}")

    return dfs_by_direction_js_srv

def create_voyage_dataframes(direction_js_srv_dfs):
    """
    Creates a dictionary of DataFrames for each voyage, sorted by Position -ArV.

    Args:
        direction_js_srv_dfs: A nested dictionary where the first level keys
                              are 'Direction', the second level keys are 'Js srv',
                              and the values are DataFrames for that specific
                              direction and Js srv.

    Returns:
        A dictionary where keys are a concatenation of 'Direction' and 'Js srv',
        and values are dictionaries containing DataFrames for each voyage,
        sorted by 'Position -ArV' croissante. Also prints the total number of voyage DataFrames created.
    """
    all_voyage_dataframes = {}
    total_dataframes_count = 0

    for direction, dfs_by_js_srv in direction_js_srv_dfs.items():
        for js_srv, df_js in dfs_by_js_srv.items():
            # Create a combined key for the new dictionary
            combined_key = f"{direction}_{js_srv}"
            all_voyage_dataframes[combined_key] = {}

            # Group by 'Numéro interne -Voy' and sort each group by 'Position -ArV'
            for voyage_num, voyage_df in df_js.groupby('Numéro interne -Voy'):
                all_voyage_dataframes[combined_key][voyage_num] = voyage_df.sort_values('Position -ArV').copy()
                total_dataframes_count += 1

    print(f"Total number of voyage DataFrames created: {total_dataframes_count}")
    return all_voyage_dataframes

def get_merged_stops_for_group(voyage_dataframes_dict, group_key):
    """
    Merges the stop lists for all voyages within a specific group (Direction_Js srv).

    Args:
        voyage_dataframes_dict: A dictionary where keys are a concatenation
                                of 'Direction' and 'Js srv', and values are
                                dictionaries containing DataFrames for each voyage.
        group_key: The key (e.g., 'Aller_lamjv') for the group to process.

    Returns:
        A tuple containing:
        - merged_stops_list: A list of unique stops merged from all voyages in the group.
        - direction: The direction of the group.
        - js_srv: The Js srv of the group.
        - voyage_numbers: A list of voyage numbers included in the merge.
    """
    if group_key not in voyage_dataframes_dict:
        print(f"Group key '{group_key}' not found in the dictionary.")
        return None, None, None, None

    voyages_in_group = voyage_dataframes_dict[group_key]
    voyage_numbers = list(voyages_in_group.keys())

    # Extract stop lists for each voyage in the group
    voyage_stops = {}
    for voyage_num, voyage_df in voyages_in_group.items():
         voyage_stops[voyage_num] = voyage_df['Arrêt'].tolist()

    # Initialize the merged list with the first list of stops
    merged_stops_list = []

    if voyage_stops:
        # Get the first voyage number and its stop list
        first_voyage_num = list(voyage_stops.keys())[0]
        merged_stops_list = voyage_stops[first_voyage_num]

        # Iterate through the rest of the stop lists and merge them
        for voyage_num, stop_list in list(voyage_stops.items())[1:]:
            merged_stops_list = compare_and_merge_lists(merged_stops_list, stop_list)

    # Extract direction and js_srv from the group_key
    direction, js_srv = group_key.split('_')

    print(f"Merged stop list created for group: {group_key}")
    print(f"Direction: {direction}, Js srv: {js_srv}")
    print(f"Voyage Numbers included: {voyage_numbers}")
    print(f"Merged Stop List: {merged_stops_list}")

    return merged_stops_list, direction, js_srv, voyage_numbers

def generate_timetable_csv_for_group(line_number, period, direction, js_srv, all_voyages_dataframes, stop_description_map, merged_stops_list):
    """
    Generates a CSV timetable content for a specific group (Direction_Js srv) within a line and period.

    Args:
        line_number: The line number.
        period: The context service (period) of the line.
        direction: The direction ('Aller' or 'Retour').
        js_srv: The Js srv (service days).
        all_voyages_dataframes: A dictionary where keys are a concatenation
                                of 'Direction' and 'Js srv', and values are
                                dictionaries containing DataFrames for each voyage
                                (output of create_voyage_dataframes).
        stop_description_map: A dictionary mapping stop IDs to their descriptions.
        merged_stops_list: A list of unique stops in the desired order for the timetable.

    Returns:
        A string containing the CSV content.
    """
    group_key = f"{direction}_{js_srv}"

    if group_key not in all_voyages_dataframes:
        print(f"Group key '{group_key}' not found in all_voyages_dataframes.")
        return ""

    voyages_in_group = all_voyages_dataframes[group_key]

    if merged_stops_list is None:
        print(f"merged_stops_list is None for group: {group_key}")
        return ""

    # Get voyage numbers and sort them by the 'Heure' of the first stop
    voyage_numbers_with_first_stop_time = []
    for voyage_num, voyage_df in voyages_in_group.items():
        if not voyage_df.empty:
            # Assuming the first stop is the one with the minimum 'Position -ArV'
            first_stop_row = voyage_df.loc[voyage_df['Position -ArV'].idxmin()]
            first_stop_time = first_stop_row['Heure']
            voyage_numbers_with_first_stop_time.append((voyage_num, first_stop_time))

    # Sort voyage numbers based on the first stop time
    # Using a lambda function to specify the sorting key
    sorted_voyage_numbers = [voyage_num for voyage_num, _ in sorted(voyage_numbers_with_first_stop_time, key=lambda item: item[1])]


    # Create the base DataFrame with stops and descriptions
    timetable_data = {'Arrêt': merged_stops_list}
    timetable_data['Description'] = [stop_description_map.get(stop_id, stop_id) for stop_id in merged_stops_list]

    # Add a column for each voyage number (now sorted) with their arrival times
    for voyage_num in sorted_voyage_numbers:
        if voyage_num not in voyages_in_group:
            print(f"Voyage number {voyage_num} not found in the group.")
            # Add a column of empty strings for this missing voyage
            timetable_data[voyage_num] = [''] * len(merged_stops_list)
            continue

        voyage_df = voyages_in_group[voyage_num]

        # Create a mapping of stop ID to arrival time for the current voyage
        # Use 'Arrêt' as the key for the arrival times
        arrival_times = voyage_df.set_index('Arrêt')['Heure'].to_dict()


        # Create the column for the current voyage with arrival times
        voyage_times = [arrival_times.get(stop_id, '') for stop_id in merged_stops_list]
        timetable_data[voyage_num] = voyage_times


    df_timetable = pd.DataFrame(timetable_data)

    # Create the header rows
    header_row1 = [f"Direction: {direction}", f"Js srv: {js_srv}"] + [''] * (len(df_timetable.columns) - 2)
    header_row2 = df_timetable.columns.tolist()

    # Combine header rows and data rows
    all_rows = [header_row1, header_row2] + df_timetable.values.tolist()

    # Create a DataFrame from all rows and save to CSV
    df_to_save = pd.DataFrame(all_rows)

    # Use StringIO to capture CSV content as a string
    csv_buffer = io.StringIO()
    df_to_save.to_csv(csv_buffer, index=False, header=False)
    csv_content = csv_buffer.getvalue()

    print(f"Timetable CSV content generated for Ligne{line_number}_Period{period}_{group_key}")
    return csv_content
