# coding: utf-8

"""Les constantes du jeu."""
import json

TURN_IT                 = -1 # la quantité de degré que l'on augmente/diminue lors d'une rotation
THRUST_IT               = -1 # La quantité de vitesse que l'on augmente lors d'une poussée
SERVER_TICRATE          = -1 # Le tick rate du serveur
REFRESH_TICRATE         = -1 # Le tick rate du client
ARENA_H                 = -1 # Le paramètre h de l'arène
ARENA_L                 = -1 # Le paramètre l de l'arène
POD_SIDE                = -1 # La taille du coté d'un POD (le joueur)
BALL_SIDE               = -1 # La taille du coté d'une dragon ball (un objectif)
ASTEROID_SIDE           = -1 # La taille du coté d'un astéroïde
GENKIDAMA_SIDE          = -1 # La taille d'un genkidama (une bombe)
INITIAL_BOMB_NUMBER     = -1 # Le nombre de bombe que possède un joueur au début de la partie
STUN_TIME               = -1 # Le nombre de server_tickrate où le joueur ne peut pas bougé après avoir touché une bombe


def setUpData():
    """Met en place toutes la variables constantes du jeu en lisant le fichier des constantes."""
    global TURN_IT, THRUST_IT, SERVER_TICRATE, REFRESH_TICRATE, ARENA_H, ARENA_L, POD_SIDE, BALL_SIDE, ASTEROID_SIDE, INITIAL_BOMB_NUMBER, STUN_TIME
    with open('../data.json') as json_file:  
        data = json.load(json_file)
        TURN_IT = data["turn_it"]
        THRUST_IT = data["thrust_it"]
        SERVER_TICRATE = data["server_tickrate"]
        REFRESH_TICRATE = data["refresh_tickrate"]
        ARENA_H = data["arena_h"]
        ARENA_L = data["arena_l"]
        POD_SIDE = data["pod_side"]
        BALL_SIDE = data["ball_side"]
        ASTEROID_SIDE = data["asteroid_side"]
        INITIAL_BOMB_NUMBER = data["nb_spirit_bombs"]
        STUN_TIME = data["stun_time"]
