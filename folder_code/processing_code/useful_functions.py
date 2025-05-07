import gzip
import json
import numpy as np
import pandas as pd
from pyproj import Proj
from scipy.signal import medfilt
from sklearn.cluster import DBSCAN

#récupérer les données
def get_data(source):
    """
    Lire le fichier contenant les données brutes 
    in: chemin du fichier contenant les données
    out: 4 arrays contenant latitude, longitude, vitesse et temps
    """
    #ouvrir le fichier
    data = gzip.open(source, "rb").read()
    data = json.loads(data)
    #récupérer latitude, longitude et temps
    lst_time, lst_lat, lst_lon = [], [], []
    for i in range(len(data["gpss"])):
        lst_time.append(data["gpss"][i]["stamp"])
        lst_lat.append(data["gpss"][i]["lat"])
        lst_lon.append(data["gpss"][i]["lon"])
    #convertir en array numpy
    time, lat, lon = np.array(lst_time), np.array(lst_lat), np.array(lst_lon)
    return time, lat, lon

#convertir en utm
def convert_utm(lat, lon, zone=18):
    """
    Convertir les données latitude et longitude en utm
    in: arrays contenant latitude, longitude et zone utm
    out: arrays contenant coordonnées (x;y) en utm
    """
    pp = Proj(proj="utm", zone=zone, ellps="WGS84", preserve_units=False)
    x_utm, y_utm = pp(lon, lat)
    return x_utm, y_utm

#interpoler les données manquantes
def manage_missing_data(x_utm, y_utm, time):
    """
    Gérer les données manquantes en les interpolant 
    in: arrays contenant coordonnées (x;y) en utm, array temps
    out: arrays contenant coordonnées (x;y) en utm, array temps sans valeurs manquantes
    """
    #trouver séquences sans données
    missing_value = np.isnan(x_utm)
    #identifier la première séquence manquantes
    cpt = 0
    while missing_value[cpt] != 0:
        cpt += 1
    #retirer la première séquence
    x_utm, y_utm= x_utm[cpt:], y_utm[cpt:]
    time = time[cpt:]
    #interpolation linéaire des valeurs manquantes
    x, y = pd.Series(x_utm), pd.Series(y_utm)
    x_interp, y_interp = x.interpolate().values, y.interpolate().values
    return x_interp, y_interp, time

#calculer distances parcourues
def compute_distance(x_utm, y_utm):
    """
    Calculer distance entre les mesures GPS
    in: arrays contenant coordonnées (x;y) en utm
    out: array contenant les distances entre deux mesures GPS
    """
    diff_x = np.diff(x_utm)
    diff_y = np.diff(y_utm)
    #en mètre
    dist = np.sqrt(diff_x**2 + diff_y**2)
    return dist

#calculer vitesse et accélération
def compute_speed(dist, time):
    """
    Calculer vitesse et accélération entre les mesures GPS
    in: array contenant les distances entre deux mesures GPS, fréquence GPS en Hz
    out: array contenant les vitesses et accélération entre deux mesures GPS
    """
    #intervalle de temps
    time_interval = np.diff(time)
    #calcul vitesse en m/s
    speed = dist / time_interval
    #acceleration en m/s²
    accel = np.diff(speed) / time_interval[1:]
    return speed, accel

#calculer distances parcourues par zone de vitesse
def compute_speed_zone(array, max_min_speed, step_speed):
    """
    Calculer distance parcourue par zone de vitesse
    in: array contenant les métriques, zone de vitesse et step, condition pour la légende
    out: dictionnaire des zones de vitesse
    """
    dico_zone_vitesse = {}
    for i in range(max_min_speed[0], max_min_speed[1], step_speed):
        #convertir en km/h
        mask = (array[:, 2].astype(float) * 3.6 >= i) & (array[:, 2].astype(float) * 3.6 <= i + step_speed)
        #distance parcourue
        distance_zone_vitesse = np.sum(array[mask, 1].astype(float))
        #ajouter au dictionnaire
        dico_zone_vitesse[f"{i}-{i + step_speed} km/h"] = distance_zone_vitesse
    #renseigner le nom
    dico_zone_vitesse["nom"] = array[0, -1]
    return dico_zone_vitesse

#filtrer les données gps incohérentes
def clean_outliers(array_speed, array_accel, array_time):
    """
    Supprimer les points gps incohérents - Implementation de la méthode Miguens
    in: arrays contenant les vitesses, les accélérations et les temps
    out: arrays contenant les vitesses, les accélérations et les temps sans les points incohérents
    note: basé sur les articles https://doi.org/10.1186/s40798-023-00672-7 et https://doi.org/10.1080/02640414.2021.1993656
    """
    #filtrer vitesse et accélération
    array_accel = medfilt(array_accel, kernel_size=9)
    array_accel = medfilt(array_accel, kernel_size=9)
    #valeurs théoriques
    x1, y1 = 8.547 + 3 * 0.51, 0 #vitesse
    x2, y2 = 0, 5.629 + 3 * 0.26 #accélération
    #calculer équation droite vitesse accélération
    a = (y2 - y1) / (x2 - x1)
    b = y1 - a * x1
    array_filter = a * array_speed + b
    #filtrer les arrays vitesse et accélération
    vitesse_clean = array_speed[array_filter > array_accel]
    acceleration_clean = array_accel[array_filter > array_accel]
    time_clean = array_time[2:][array_filter > array_accel]
    #appliquer clustering dbscan pour supprimer les points isolés
    X = np.column_stack((vitesse_clean, acceleration_clean))
    db = DBSCAN(eps=0.2, min_samples=1).fit(X)
    unique, counts = np.unique(db.labels_, return_counts=True)
    isolated_clusters = unique[counts < 5]
    vitesse_clean2 = vitesse_clean[~np.isin(db.labels_, isolated_clusters)]
    acceleration_clean2 = acceleration_clean[~np.isin(db.labels_, isolated_clusters)]
    time_clean2 = time_clean[~np.isin(db.labels_, isolated_clusters)]
    return vitesse_clean2, acceleration_clean2, time_clean2

#appliquer toutes ces fonctions pour avoir les données traitées
def apply_all_functions(path_to_data):
    """
    Appliquer toutes les fonctions pour obtenir les informations 
    in: chemin vers les données
    out: indicateurs de distances
    """
    #récupérer les données
    temps, latitude, longitude = get_data(path_to_data)
    #convertir en utm
    x, y = convert_utm(latitude, longitude, zone=18)
    #interpoller les valeurs manquantes
    x, y, temps = manage_missing_data(x, y, temps)
    #calculer distance, vitesse, accélération
    distance = compute_distance(x, y)
    vitesse_calcul, acceleration_calcul = compute_speed(distance, temps)
    #supprimer outliers
    vitesse_propre, acceleration_propre, temps_propre = clean_outliers(vitesse_calcul[1:], acceleration_calcul, temps)
    #recalculer distance
    distance_propre = vitesse_propre[1:] * np.diff(temps_propre)
    #formater les donnnées
    data_format = np.column_stack((temps_propre[1:], distance_propre, vitesse_propre[1:], acceleration_propre[1:]))
    return x, y, temps, data_format

#compter le nombre d'accélération
def count_nb_accel(array_accel, array_time, threshold_ms, threshold_time):
    """
    Compter le nombre d'accélération au-delà d'un seuil
    in: chemin vers les données
    out: indicateurs de distances
    """
    indices = np.where(array_accel > threshold_ms)[0]
    data = array_time[indices]
    #parcourir les temps et sélectionner si écart suffisant
    lst_complete, lst_temp = [], []
    for i in range(1, len(data)):
        if data[i] - data[i-1] < threshold_time:
            lst_temp.append(data[i-1])
        else:
            lst_complete.append(lst_temp)
            lst_temp = []
    #filtrer la liste
    lst_complete = [l for l in lst_complete if l and len(l) > 5]
    #compter nombre d'acceleration
    nb_accel = len(lst_complete)
    return nb_accel

#convertir coordonnées dans repère terrain
def transpose_data(x_utm, y_utm, coord_field, zone=18):
    """
    Transposer les coordonnées utm dans un repère du terrain
    in: arrays contenant coordonnées (x;y), array contenant les coordonnées terrain
    out: conversion des arrays dans le repère du terrain
    """
    #convertir coord_field en UTM
    pp = Proj(proj="utm", zone=zone, ellps="WGS84", preserve_units=False)
    x_coord_utm, y_coord_utm = pp(coord_field[:, 1], coord_field[:, 0])
    #calcul angle de rotation
    hypothenuse = np.sqrt((x_coord_utm[2] - x_coord_utm[1])**2 + (y_coord_utm[2] - y_coord_utm[1])**2)
    oppose = np.sqrt((x_coord_utm[2] - x_coord_utm[2])**2 + (y_coord_utm[2] - y_coord_utm[1])**2)
    teta = np.arcsin(oppose / hypothenuse)
    #translation
    x_repere, y_repere = x_coord_utm - x_coord_utm[1], y_coord_utm - y_coord_utm[1]
    x_trans, y_trans = x_utm - x_coord_utm[1], y_utm - y_coord_utm[1]
    #appliquer la rotation
    x_repere_rot = x_repere * np.cos(teta) - y_repere * np.sin(teta)
    y_repere_rot = x_repere * np.sin(teta) + y_repere * np.cos(teta)
    x = x_trans * np.cos(teta) - y_trans * np.sin(teta)
    y = x_trans * np.sin(teta) + y_trans * np.cos(teta)
    coord = np.array([x_repere_rot, y_repere_rot]).T
    return x, y, coord