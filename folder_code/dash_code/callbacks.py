import numpy as np
from dash import callback, Output, Input
from folder_code.dash_code.layout import *
from folder_code.processing_code.dash_functions import *
from folder_code.processing_code.useful_functions import *
from folder_code.processing_code.video_functions import *
from tqdm import tqdm


#parcourir les dossiers
data_path = "./data"
date_dic, match_dic, joueur_dic, df_files = get_path_select(data_path)

#récupérer le front
front = create_layout(date_dic, match_dic, joueur_dic)

#mettre à jour les selects en fonction des sélections en cours - GPS
@callback(
    [Output("select_date", "data"),
     Output("select_match", "data"),
     Output("select_joueur", "data")],
    [Input("select_date", "value"),
     Input("select_match", "value"),
     Input("select_joueur", "value")],
     prevent_initial_call=True)
def update_select(date, match, file):
    #filtrer les données
    filtered_data = filter_dataframe(df_files, selected_date=date, selected_match=match, selected_name=file)
    date_options = np.unique(filtered_data.date)
    match_options = np.unique(filtered_data.match)
    player_options = np.unique(filtered_data.nom)
    return date_options, match_options, player_options

#mettre à jour les selects en fonction des sélections en cours - VIDEO
@callback(
    [Output("select_date_video", "data"),
     Output("select_match_video", "data"),
     Output("select_joueur_video", "data")],
    [Input("select_date_video", "value"),
     Input("select_match_video", "value"),
     Input("select_joueur_video", "value")],
     prevent_initial_call=True)
def update_select(date, match, file):
    #filtrer les données
    filtered_data = filter_dataframe(df_files, selected_date=date, selected_match=match, selected_name=file)
    date_options = np.unique(filtered_data.date)
    match_options = np.unique(filtered_data.match)
    player_options = np.unique(filtered_data.nom)
    return date_options, match_options, player_options

#visualisation barplot distances parcourues par zone de vitesse, scatterplot vitesse/acceleration, nombre acceleration, note joueur
@callback([Output("barplot_dist", "data"),
           Output("barplot_dist", "dataKey"),
           Output("barplot_dist", "series"),
           Output("barplot_dist", "h"),
           Output("title_barplot", "style"),
           Output("barplot_dist", "style"),
           Output("scatter_vitesse_accel", "data"),
           Output("scatter_vitesse_accel", "style"),
           Output("title_scatterspeedaccel", "style"),
           Output("barplot_accel", "data"),
           Output("barplot_accel", "dataKey"),
           Output("barplot_accel", "series"),
           Output("title_nbaccel", "style"),
           Output("barplot_accel", "style"),
           Output("donut_vmax", "data"),
           Output("donut_vmax", "style"),
           Output("donut_amax", "data"),
           Output("donut_amax", "style"),
           Output("title_donut", "style")],
          [Input("select_date", "value"),
           Input("select_match", "value"),
           Input("select_joueur", "value")],
           prevent_initial_call=True)
def create_visualization(date, match, joueur):
    data_barplot_zd, data_scatterplot, data_barplot_nba, cpt_color = [], [], [], 0
    #pour tous les joueurs d'un match
    if (date and match) or joueur:
        #filtrer les données
        filtered_data = filter_dataframe(df_files, selected_date=date, selected_match=match, selected_name=joueur)
        #reconstituer les chemins et récupérer les données
        for i in tqdm(range(len(filtered_data)), "collecte data viz"):
            lst = filtered_data.loc[i, :].values.tolist()
            path = f"{data_path}/{lst[1]}/{lst[2]}/gps_data/{lst[3]}"
            #appliquer les fonctions de traitement gps
            _, _, _, array_data = apply_all_functions(path)
            #ajouter information nom dans l'array
            ref = f"{lst[2]}\n{lst[1]}" if joueur else lst[-1]
            array_data = np.column_stack((array_data, np.full((len(array_data),), ref)))

            #pour barplot distance zone  de vitesse
            #calcul des zones de vitesse
            dico_bar_plot = compute_speed_zone(array_data, [0, 30], 5)
            #ajouter dans une liste
            data_barplot_zd.append(dico_bar_plot)
            #trier par ordre décroissant
            data_barplot_zd = sorted(data_barplot_zd, key=lambda x: x["0-5 km/h"]+x["5-10 km/h"]+x["10-15 km/h"]+x["15-20 km/h"]+x["20-25 km/h"], reverse=True)
            #définir style
            lst_series = [{"name": "0-5 km/h", "color": "violet.6"}, {"name": "5-10 km/h", "color": "blue.6"}, {"name": "10-15 km/h", "color": "teal.6"}, 
                          {"name": "15-20 km/h", "color": "green.6"}, {"name": "20-25 km/h", "color": "yellow.6"}, {"name": "25-30 km/h", "color": "orange.6"}]
            hauteur_graphique = 400 if 40 * len(data_barplot_zd) < 400 else 40 * len(data_barplot_zd)

            #pour scatterplot vitesse/acceleration
            lst_color = ["red.5", "pink.5", "grape.5", "violet.5", "indigo.5", "blue.5", "cyan.5", "teal.5", "green.5", "lime.5", "yellow.5", "orange.5", "gray.5"]
            data_scatterplot.append({"color": lst_color[cpt_color], "name": ref, "data": [{"vitesse": max(array_data[:, 2].astype(float))*3.6, "acceleration": max(array_data[:, 3].astype(float))}]})
            cpt_color += 1

            #pour barplot nombre d'acceleration
            number_accel = count_nb_accel(array_data[:, 3].astype(float), array_data[:, 0].astype(float), 3, 8)
            data_barplot_nba.append({"nom": ref, "nombre d'accélération": number_accel})
            #classer par ordre croissant
            data_barplot_nba = sorted(data_barplot_nba, key=lambda x: x["nombre d'accélération"], reverse=True)
            lst_series_accel = [{"name": "nombre d'accélération", "color": "violet.6"}]

            #pour donutchart note des joueurs
            if joueur and not (date and match):
                #valeur de référence des vitesses et accélérations maximales
                ref_vmax = {(1,2,3): 8.16, (4,5): 7.98, (6,7,8): 8.27, (9,): 8.76, (10,12): 8.58, (11,13,14,15): 9.53}
                ref_amax = {(1,2,3): 5.02, (4,5): 4.77, (6,7,8): 4.83, (9,): 5.25, (10,12): 5.13, (11,13,14,15): 5.70}
                theorical_vmax = next((v for k, v in ref_vmax.items() if int(lst[3][:-5]) in k), None)
                theorical_amax = next((v for k, v in ref_amax.items() if int(lst[3][:-5]) in k), None)
                measured_vmax = max(array_data[:, 2].astype(float))
                measured_amax = max(array_data[:, 3].astype(float))
                #calculer un note sur 100
                note_100_vmax = round(measured_vmax * 100 / theorical_vmax, 1)
                note_100_amax = round(measured_amax * 100 / theorical_amax, 1)
                remainder_100_vmax = round(100 - note_100_vmax, 1)
                remainder_100_amax = round(100 - note_100_amax, 1)
                data_donut_vmax = [{"name": "vmax mesurée", "value": note_100_vmax, "color": "indigo.4"}, {"name": "vmax théorique", "value": remainder_100_vmax, "color": "gray.4"}]
                data_donut_amax = [{"name": "vmax mesurée", "value": note_100_amax, "color": "indigo.4"}, {"name": "vmax théorique", "value": remainder_100_amax, "color": "gray.4"}]
                style_donut_vmax, style_donut_amax, title_donut = {"display": "block"}, {"display": "block"}, {"display": "block"}
            else:
                data_donut_vmax, style_donut_vmax, data_donut_amax, style_donut_amax, title_donut = [], {"display": "none"}, [], {"display": "none"}, {"display": "none"}

        return data_barplot_zd, "nom", lst_series, hauteur_graphique, {"display": "block"}, {"display": "block"}, data_scatterplot, {"display": "block"}, {"display": "block"}, data_barplot_nba, "nom", lst_series_accel, {"display": "block"}, {"display": "block"}, data_donut_vmax, style_donut_vmax, data_donut_amax, style_donut_amax, title_donut
    else:
        return [], "", [], 0, {"display": "none"}, {"display": "none"}, [], {"display": "none"}, {"display": "none"}, [], "", [], {"display": "none"}, {"display": "none"}, [], {"display": "none"}, [], {"display": "none"}, {"display": "none"}

#générer et visualiser vidéo
@callback([Output("html_video", "src"),
           Output("html_video", "style")],
          [Input("select_date_video", "value"),
           Input("select_match_video", "value"),
           Input("select_joueur_video", "value"),
           Input("select_metrique_video", "value")],
           prevent_initial_call=True)
def create_video(date, match, joueur, metrique):
    if date and match and joueur and metrique:
        #filtrer les données
        filtered_data = filter_dataframe(df_files, selected_date=date, selected_match=match)
        #reconstituer les chemins et récupérer les données
        lst_path, lst_name = [], []
        for i in range(len(filtered_data)):
            lst = filtered_data.loc[i, :].values.tolist()
            lst_path.append(f"{data_path}/{lst[1]}/{lst[2]}/gps_data/{lst[3]}")
            lst_name.append(lst[-1])
        #créer le clip vidéo
        create_videoclip(lst_path, lst_name, joueur)
        return "./assets/videoPOC.mp4", {"display": "block"}
    else:
        return "", {"display": "none"}


