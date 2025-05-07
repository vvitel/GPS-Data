import os
import pandas as pd

#récupérer les données
def get_path_select(initial_path):
    """
    Parcourir les dossiers contenant les fichiers
    in: chemin racine contenant les fichiers
    out: dictionnaires contenant les dates, les matchs, les fichiers, les joueurs
    """
    listdir = []
    for d in os.listdir(initial_path):
        for m in os.listdir(f"{initial_path}/{d}"):
            for j in os.listdir(f"{initial_path}/{d}/{m}/gps_data"):
                df_compo = pd.read_csv(f"{initial_path}/{d}/{m}/compo.txt", sep=";", header=None)
                nom = df_compo[df_compo[0] == int(j[:-5])][1]
                listdir.append([d, m, j, nom.values[0]])
    df_path = pd.DataFrame(listdir, columns=["date", "match", "file", "nom"])
    dic_date = [{"value": i, "label": i} for i in pd.unique(df_path["date"])]
    dic_match = [{"value": i, "label": i} for i in pd.unique(df_path["match"])]
    dic_joueur = [{"value": i, "label": i} for i in pd.unique(df_path["nom"])]
    #classer nom par ordre alphabétique
    dic_joueur.sort(key=lambda x: x["label"])
    return dic_date, dic_match, dic_joueur, df_path

#filtrer les données en fonction des sélections
def filter_dataframe(df, selected_date=None, selected_match=None, selected_name=None):
    #filtrer selon la date
    if selected_date:
        df = df[df["date"] == selected_date]
    #filtrer selon le match
    if selected_match:
        df = df[df["match"] == selected_match]
    #filtrer selon le nom
    if selected_name:
        df = df[df["nom"] == selected_name]
    #réinitialiser index
    df = df.reset_index()
    return df