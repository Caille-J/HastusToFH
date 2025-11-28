def valider_colonnes_selectionnees(colonnes_selectionnees, colonnes_attendues):
    """
    Vérifie que les colonnes sélectionnées par l'utilisateur correspondent exactement
    à la liste des colonnes attendues.

    Args:
        colonnes_selectionnees (list): Liste des colonnes sélectionnées par l'utilisateur.
        colonnes_attendues (list): Liste des colonnes attendues (ex: ["Ligne", "Numéro interne -Voy", ...]).

    Returns:
        tuple: (bool, str)
            - bool: True si les colonnes sont valides, False sinon.
            - str: Message d'erreur ou de succès.
    """
    colonnes_attendues = set(colonnes_attendues)
    colonnes_selectionnees = set(colonnes_selectionnees)

    if colonnes_selectionnees == colonnes_attendues:
        return True, "Toutes les colonnes attendues sont présentes et aucune colonne supplémentaire n'est sélectionnée."

    # Colonnes manquantes
    colonnes_manquantes = colonnes_attendues - colonnes_selectionnees
    # Colonnes supplémentaires
    colonnes_supplementaires = colonnes_selectionnees - colonnes_attendues

    message = ""
    if colonnes_manquantes:
        message += f"Colonnes manquantes : {', '.join(colonnes_manquantes)}. "
    if colonnes_supplementaires:
        message += f"Colonnes supplémentaires sélectionnées : {', '.join(colonnes_supplementaires)}. "

    message += "Veuillez sélectionner exactement les colonnes attendues."

    return False, message