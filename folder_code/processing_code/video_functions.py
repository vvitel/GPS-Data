import cv2
import numpy as np
from tqdm import tqdm
from .useful_functions import *

#visualiser les données
def visualise_playerposition(path_to_video, f, lst_poste, lst_x, lst_y):
    """
    Visualisation de la vidéo du match avec les coordonnées gps
    in: chemin vers la video, index de la frame, coordonnées correspondantes
    out: image de la vidéo avec encart montrant les positions gps
    """
    #lire frame de la video
    video = cv2.VideoCapture(path_to_video)
    video.set(cv2.CAP_PROP_POS_FRAMES, f)
    _, frame = video.read()
    frame = cv2.resize(frame, (1920, 1080))
    #tracer le fond du terrain
    ratio_field = 6
    dim_long, dim_larg = 100, 60
    coord_start_field, coord_end_field = (0,0), (dim_long*ratio_field, dim_larg*ratio_field)
    overlay = frame.copy()
    frame = cv2.rectangle(frame, coord_start_field, coord_end_field, (255,255,255) , -1)
    #ajouter de la transparence sur le rectangle
    frame = cv2.addWeighted(overlay, 0.4, frame, 1-0.4, 0)
    #tracer ligne médiane
    coord_start_median = (coord_end_field[0]//2, 0)
    coord_end_median = (coord_end_field[0]//2, coord_end_field[1])
    frame = cv2.line(frame, coord_start_median, coord_end_median, (194,113,25), 2)
    #tracer lignes des 10
    coord_start_left10 = (coord_end_field[0]//2-10*ratio_field, 0)
    coord_end_left10 = (coord_end_field[0]//2-10*ratio_field, coord_end_field[1])
    frame = cv2.line(frame, coord_start_left10, coord_end_left10, (194,113,25), 2)
    coord_start_right10 = (coord_end_field[0]//2+10*ratio_field, 0)
    coord_end_right10 = (coord_end_field[0]//2+10*ratio_field, coord_end_field[1])
    frame = cv2.line(frame, coord_start_right10, coord_end_right10, (194,113,25), 2)
    #tracer lignes des 22
    coord_start_left22 = (0+22*ratio_field, 0)
    coord_end_left22 = (0+22*ratio_field, coord_end_field[1])
    frame = cv2.line(frame, coord_start_left22, coord_end_left22, (194,113,25), 2)
    coord_start_right22 = (coord_end_field[0]-22*ratio_field, 0)
    coord_end_right22 = (coord_end_field[0]-22*ratio_field, coord_end_field[1])
    frame = cv2.line(frame, coord_start_right22, coord_end_right22, (194,113,25), 2)
    #afficher position
    for i in range(len(lst_x)):
        poste, x, y = lst_poste[i], lst_x[i], lst_y[i]
        x = (x + dim_long) * ratio_field
        y = y * ratio_field
        #pour open cv obligation d'avoir des entiers
        x, y = int(x), int(y)
        #inverser axe des x
        x = dim_long * ratio_field - (x - 0)
        #représenter les joueurs
        frame = cv2.circle(frame, (x, y), 10, (194,113,25), -1)
        #ajouter le poste
        ccx, ccy = (5, 5) if len(poste) == 1 else (10, 5)
        frame = cv2.putText(frame, poste, (x-ccx, y+ccy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    #mettre en RGB
    frame = frame[:, :, [2, 1, 0]]
    return frame

#créer vidéo - répertoire
def create_video(path_to_save, fps, shape_image, array_images):
    """
    Génerer une vidéo
    in: path ou enregistrer la vidéo, frame rate, tuple dimension image, array contenant les images
    out: enregitre une vidéo
    """
    fourcc = cv2.VideoWriter_fourcc(*'avc1') 
    video = cv2.VideoWriter(path_to_save, fourcc, fps, shape_image)
    #parcourir les frames de la video
    for i in range(array_images.shape[0]):
        test = array_images[i]
        test_bgr = cv2.cvtColor(test, cv2.COLOR_RGB2BGR)
        video.write(test_bgr)
    cv2.destroyAllWindows()
    video.release()

#formater les données pour la visualisation
def format_data(dico, time):
    """
    Formater les données gps pour réaliser la visualisation des positions
    in: dictionnaire contenant coordonnées (x;y) et le temps; temps de référence
    out: listes avec les coordonnées x et y et liste avec les postes
    """
    lst_poste, lst_x, lst_y = [], [], []
    for i in dico.keys():
        array = dico[i]
        array = array[array[:, 2] == time]
        if len(array) == 0: continue
        lst_poste.append(i)
        lst_x.append(array[0, 0])
        lst_y.append(array[0, 1])
    return lst_poste, lst_x, lst_y

#créer la vidéo
def create_videoclip(path_2_data, list_name, player):
    """
    Créer le clip vidéo
    in: chemin vers les données GPS, liste contenant nom des joueurs, joueur d'intérêt
    out: clip vidéo enregistré
    """
    dico_data = {}
    #récupérer les données
    for i in tqdm(range(len(path_2_data)), "collecte data video"):
        #poste
        split_str = path_2_data[i].split("/")
        poste = split_str[-1][:-5]
        #ouvir les données
        x_data, y_data, temps_data, array_data = apply_all_functions(path_2_data[i])
        #convertir le temps des gps - ajout 4 heures
        temps_data = temps_data + 14400
        #convertir coordonnées dans repère terrain
        path_folder_video = f"./video/{split_str[2]}/{split_str[3]}"
        coord_terrain = np.load(f"{path_folder_video}/terrain_{split_str[3]}.npy")
        x, y, repere = transpose_data(x_data, y_data, coord_terrain, zone=18)
        #formater les données
        dico_data[poste] = np.column_stack((x, y, temps_data))
        #récupérer information pour le bon joueur
        if list_name[i] == player:
            #probleme de correspondance avec les temps entre données filtrées et brutes
            go_to = array_data[:, 0].astype(float)[np.argmax(array_data[:, 2].astype(float))]
            #convertir le temps des gps - ajout 4 heures
            go_to = go_to + 14400

    #récupérer fichier d'annotation
    annot = pd.read_csv(f"{path_folder_video}/annotation_{split_str[3]}.txt", header=None, sep=";")
    tps_kickoff = annot[0].round(1).values[0]
    #trouver frame correpondant au temps
    corresponding_frame = int(go_to - tps_kickoff) * 30
    corresponding_frame = corresponding_frame + 35 #MAGOUILLE !!!!!
    #parcourir le temps du match
    images = []
    for f, t in tqdm(zip(range(corresponding_frame-60,corresponding_frame+60), np.arange(go_to, go_to+4, 1/30)), "créer video"):
        t = round(t, 1)
        #récupérer les données en fonction de l'évenement
        liste_poste, liste_x, liste_y = format_data(dico_data, t)
        #créer la visualisation
        image = visualise_playerposition(f"{path_folder_video}/video_{split_str[3]}.avi", f, liste_poste, liste_x, liste_y)
        images.append(image)
    images_array = np.array(images)
    #créer la vidéo
    create_video("./assets/videoPOC.mp4", 15, (1920, 1080), images_array)