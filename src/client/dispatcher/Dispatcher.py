# coding: utf-8

from tkinter import Event
from threading import Thread, RLock
from player.Pair import Pair
from player.PlayerPod import PlayerPod
from math import sqrt, cos, sin, radians

import data as dat
import re as regexp

WAITING_FOR_FIRST_TICK = -1

class Dispatcher():
    """Le dispatcher de l'application.
        Le dispatcher agira comme un intermédiaire entre les différents composants de notre application.
        Il garantira aussi les accès en session critiques au resources de l'application lorsque cela est nécessaire.
    """
    def __init__(self):
        self.serverMessager = None
        self.graphicalApp = None
        self.playerPseudo = None
        self.player = None
        self.userCanPlay = False
        self.opponentsLock = RLock()
        self.opponents = {}     # Un dictionnaire d'adversaire
        self.objectif = ()      # Un tuple représentant l'objectif : (x, y, canvasTag, photoImage)
        self.obstaclesLock = RLock()
        self.obstacles = []   # Une liste de tuple représentant un obstacle : (x, y, canvasTag, photoImage)
        self.bombsLock = RLock()
        self.bombs = []   # Une liste de tuple représentant une bombe : (x, y, canvasTag, photoImage)
        self.nbBomb = 0
        self.objectifCpt = 0

    def setServerMessager(self, serverMessager):
        """Setteur du serverMessager du dispatcher.
        
        Arguments:
            serverMessager -- Le serverMessager.
        """
        self.serverMessager = serverMessager

    def setGraphicalApp(self, gApp):
        """Setteur de l'application graphique du dispatcher.
        
        Arguments:
            gApp -- L'application graphique.
        """
        self.graphicalApp = gApp

    def onConnectionClicked(self, pseudo):
        """ Handler du clique sur le bouton de connexion.
        
        Arguments:
            pseudo -- Le pseudo que le joueur veut.
        
        Returns:
            True si la connexion est un succès, False sinon.
        """
        res = self.serverMessager.connect(pseudo)
        if res:
            self.playerPseudo = pseudo
        return res

    def onExitClicked(self):
        """Handler du clique sur le bouton exit."""
        self.graphicalApp.closeWindow()

    def onCloseWindow(self):
        """Handler de l'événement de fermeture de la fenêtre."""
        self.serverMessager.closeConnection(self.playerPseudo)

    def clockEvent(self, Event):
        """ Handler d'un événement demandant une rotation.
            Déléguera le traitement de la tâche à un autre thread pour ne pas bloquer le thread de l'interface graphique.
        """
        Thread(target=self.clockEventForNonGUIThread).start()

    def clockEventForNonGUIThread(self):
        """Applique une rotation au joueur."""
        if self.userCanPlay:
            self.player.acquire()
            self.player.clock()
            self.player.release()

    def antiClockEvent(self, Event):
        """ Handler d'un événement demandant une rotation inverse.
            Déléguera le traitement de la tâche à un autre thread pour ne pas bloquer le thread de l'interface graphique.
        """
        Thread(target=self.antiClockEventForNonGUIThread).start()

    def antiClockEventForNonGUIThread(self):
        """Applique une rotation inverse au joueur."""
        if self.userCanPlay:
            self.player.acquire()
            self.player.antiClock()
            self.player.release()

    def thrustEvent(self, Event):
        """ Handler d'un événement demandant une impulsion.
            Déléguera le traitement de la tâche à un autre thread pour ne pas bloquer le thread de l'interface graphique.
        """
        Thread(target=self.thrustEventFromNonGUIThread).start()
    
    def thrustEventFromNonGUIThread(self):
        """Applique au poussée au joueur."""
        if self.userCanPlay:
            self.player.acquire()
            self.player.thrust()
            self.player.release()

    def putBomb(self, Event):
        """ Handler d'un événement demandant la pose d'une bombe.
            Déléguera le traitement de la tâche à un autre thread pour ne pas bloquer le thread de l'interface graphique.
        """
        Thread(target=self.putBombFromNonGUIThread).start()
    
    def putBombFromNonGUIThread(self):
        """Le joueur pause une bombe s'il lui en reste."""
        self.player.acquire()
        self.bombsLock.acquire()
        if self.userCanPlay and self.nbBomb > 0:
            self.nbBomb -= 1
            self.graphicalApp.decreaseBombOf(self.playerPseudo)
            # On va placer la bombe derrière le joueur
            angle = radians(self.player.getAngle() - 180)
            bombX = self.player.getPositionX() + dat.POD_SIDE * cos(angle)
            bombY = self.player.getPositionY() + dat.POD_SIDE * -sin(angle)
            
            tupleRes = self.graphicalApp.createGraphicalGenkidma(bombX, bombY)
            tupleRes = (bombX, bombY) + tupleRes
            self.bombs.append(tupleRes)
            self.serverMessager.sendMessage("PUT/X" + str(bombX) + "Y" + str(bombY) + "/")
        self.bombsLock.release()
        self.player.release()

    def onBombHit(self, pseudo, bombCoord):
        """ Réagit au message indiquant qu'un joueur a touché une bombe.
            Enlève la bombe de l'interface et applique l'animation d'immobilisation au joueur concerné.
        
        Arguments:
            pseudo -- Le pseudo du joueur qui à touché la bombe.
            bombCoord -- Les coordonnées de la bombe.
        """

        pattern = "(-?[0-9]+\\.?[0-9]+E?-?[0-9]*)"
        extractedCoord = regexp.findall(pattern, bombCoord)
        bombX = float(extractedCoord[0])
        bombY = float(extractedCoord[1])
        print("[EVENT]: " + str(pseudo) + " hit the bomb at" + str(bombX) + ":" + str(bombY))
        self.bombsLock.acquire()
        for bomb in self.bombs:
            # C'est la bonne bombe !
            # On convertie en int afin de ne pas avoir d'erreur de comparaison entre flottant
            if int(bomb[0]) == int(bombX) and int(bomb[1]) == int(bombY):
                self.graphicalApp.deleteFromCanvas(bomb[2])
                self.bombs.remove(bomb)
                break

        if pseudo == self.playerPseudo:
            self.player.acquire()
            self.player.immobilize()
            self.player.release()
        else:
            self.opponentsLock.acquire()
            opponent = self.opponents[pseudo]
            opponent.immobilize()
            self.opponentsLock.release()

        self.bombsLock.release()

    def onBombPut(self, pseudo, bombCoord):
        """ Réagit au message indiquant qu'un joueur à posé une bombe.
        
        Arguments:
            pseudo -- Le pseudo du joueur.
            bombCoord -- Les coordonnées de la bombe posée.
        """

        pattern = "(-?[0-9]+\\.?[0-9]+E?-?[0-9]*)"
        extractedCoord = regexp.findall(pattern, bombCoord)
        bombX = float(extractedCoord[0])
        bombY = float(extractedCoord[1])
        print("[EVENT]: " + str(pseudo) + " put a bomb at" + str(bombX) + ":" + str(bombY))
        self.bombsLock.acquire()
        tupleRes = self.graphicalApp.createGraphicalGenkidma(bombX, bombY)
        tupleRes = (bombX, bombY) + tupleRes
        self.graphicalApp.decreaseBombOf(pseudo)
        self.bombs.append(tupleRes)
        self.bombsLock.release()
    
    def createPlayer(self, pseudo, x, y):
        """Crée un joueur.
        
        Arguments:
            pseudo -- Le pseudo du joueur.
            x -- La coordonnée X du joueur.
            y -- La coordonnée Y du joueur.
        """
        print("Création du joueur")
        pos = Pair(x, y)
        tupleRes = self.graphicalApp.createGraphicalPlayer(pos.getX(), pos.getY())
        self.player = PlayerPod(pseudo, pos, 0, tupleRes[0], tupleRes[1], tupleRes[2])
    
    def createOpponent(self, pseudo, x, y):
        """Crée un adversaire et l'ajoute à notre dictionnaire d'adversaire.
        
        Arguments:
            pseudo -- Le pseudo de l'adversaire.
            x -- La coordonnée X de l'adversaire.
            y -- La coordonnée Y de l'adversaire.
        """
        self.graphicalApp.createChat(pseudo)
        pos = None
        if x != None and y != None:
            pos = Pair(x, y)
            tupleRes = self.graphicalApp.createGraphicalOpponent(pos.getX(), pos.getY())
            self.opponents[pseudo] = PlayerPod(pseudo, pos, 0, tupleRes[0], tupleRes[1], tupleRes[2])
        else:
            self.opponents[pseudo] = PlayerPod(pseudo, None, 0, None, None, None)
        
        self.graphicalApp.addScoreToTable(pseudo, 0)
        self.graphicalApp.setBombOf(pseudo, dat.INITIAL_BOMB_NUMBER)
        self.opponentsLock.acquire()
        self.opponentsLock.release()

    def getPlayer(self):
        """Getteur sur le joueur du dispatcher.
        
        Returns:
            Le joueur du dispatcher.
        """
        return self.player

    def getPlayerCommand(self):
        """ Récupère les commandes du joueurs.
        
        Returns:
            Les commandes du joueur, None si le verrou du joueur n'a pas pu être pris en 0.5 seconde
        """
        command = None
        if self.player is not None and self.player != WAITING_FOR_FIRST_TICK:
            res = self.player.acquire(timeout=0.5)
            # On a obtenu le lock
            if res:
                command = self.player.getCommand()
                self.player.release()    
        return command
    
    def resetPlayerCommand(self):
        """Reset les commandes du joueur."""
        self.player.acquire()
        self.player.resetCommand()
        self.player.release()

    def updateEveryPlayerPosition(self):
        """Met à jour les positions de tous les joueurs et demande à l'interfaces graphiques de se mettre à jour en conséquence."""
        
        # On met à jour la position du joueur si le joueur est bien initialisé
        if self.player is None or self.player == WAITING_FOR_FIRST_TICK:
            return
        self.player.acquire()
        if not self.player.isImmobilized():
            self.updatePlayerPosition(self.player)
            self.graphicalApp.updateUIPlayer(self.player)
        self.player.release()

        # On met à jour la position des adversaires
        self.opponentsLock.acquire()
        for _, opponent in self.opponents.items():
            if opponent is None:
                continue
            opponent.acquire()
            # Il se peut que l'on aie pas encore reçu la position de l'adversaire
            if opponent.getPosition() is not None and not opponent.isImmobilized():
                self.updatePlayerPosition(opponent)
                self.graphicalApp.updateUIPlayer(opponent)
            opponent.release()
        self.opponentsLock.release()

    def updatePlayerPosition(self, player):
        """Met à jour la position d'un joueur en fonction de son vecteur et de son angle.
        
        Arguments:
            player -- Le joueur que l'on souhaite mettre à jour.
        """
        newX = player.getPositionX()
        newX += player.getVectorX()
        
        newY = player.getPositionY()
        newY += player.getVectorY()

        # Le pod quitte le canvas par la droite
        if newX > dat.ARENA_L:
            newX = -dat.ARENA_L + (newX - dat.ARENA_L)
        # Le pod quitte le canvas par la gauche
        if newX < -dat.ARENA_L:
            newX = dat.ARENA_L - (newX + dat.ARENA_L)

        # Le pod quitte le canvas par le haut
        if newY > dat.ARENA_H:
            newY = -dat.ARENA_H + (newY - dat.ARENA_H)
        # Le pod quitte le canvas par le bas
        if newY < -dat.ARENA_H:
            newY = dat.ARENA_H - (newY + dat.ARENA_H)
        
        player.setPositionX(newX)
        player.setPositionY(newY)

        self.checkCollisions(self.player)

    def showDeniedMessage(self):
        """Demande à l'interface graphique d'afficher un message indiquant un refus de connexion."""
        self.graphicalApp.showDeniedMessage()

    def onScoresReceived(self, scores):
        """ Réagit à la réception de scores.
            Demandera à l'interface graphique d'afficher les nouveaux scores.
        
        Arguments:
            scores -- Les scores reçus.
        """
        scores = scores.split("|")
        for score in scores:
            elt = score.split(":")
            self.graphicalApp.addScoreToTable(elt[0], elt[1])

    def onObjectifReceived(self, objectif, fromWelcomeWait=False):
        """ Réagit à la réception d'un objectif.
            Enlèvera l'ancien objectif s'il existe et affichera le nouveau.
        
        Arguments:
            objectif -- L'objectif reçu.
        
        Keyword Arguments:
            fromWelcomeWait -- Est-ce que l'on vient d'un message welcome de type wait (default: {False})
        """
        
        # On enlève le dernier objectif s'il existe
        if self.objectif:
            self.graphicalApp.deleteFromCanvas(self.objectif[2])
        
        print(fromWelcomeWait)

        pattern = "(-?[0-9]+\\.?[0-9]+E?-?[0-9]*)"
        extractedCoord = regexp.findall(pattern, objectif)
        objectifX = float(extractedCoord[0])
        objectifY = float(extractedCoord[1])

        # On n'affiche l'objectif qu'au démarrage de la partie.
        if not fromWelcomeWait:
            self.objectifCpt += 1
            # On a seulement 7 dragon ball...
            if self.objectifCpt > 7:
                self.objectifCpt = 1

            tupleRes = self.graphicalApp.showObjectif(objectifX, objectifY, self.objectifCpt)
            tupleRes = (objectifX, objectifY) + tupleRes
            self.objectif = tupleRes

    def onStatusReceived(self, status):
        """Réagit à la réception d'un statut et demande à l'interface d'afficher un message en fonction du statut."""
        if status == "wait":
            self.graphicalApp.showWaitingMessage()
        # On peut jouer directement
        else:
            self.player = WAITING_FOR_FIRST_TICK
            self.graphicalApp.showStartMessage()
            self.startGame()
    
    def onPlayersCoordsReceived(self, coords):
        """ Réagit à la réception des coordonnées des joueurs.
            Ajoute l'ensemble des joueurs à l'application.
        
        Arguments:
            coords  -- Les coordonnées des joueurs.
        """
        players = coords.split("|")
        print("Positions of players : ")
        pattern = "(-?[0-9]+\\.?[0-9]+E?-?[0-9]*)"        
        # Création des joueurs avec leurs coordonnées
        for p in players:
            splitted = p.split(":")
            print("\t", splitted[0], "->", splitted[1])
            extractedCoord = regexp.findall(pattern, splitted[1])
            playerX = float(extractedCoord[0])
            playerY = float(extractedCoord[1])
            # Notre joueur
            if splitted[0] == self.playerPseudo:
                self.createPlayer(splitted[0], playerX, playerY)
            # Un adversaire
            else:
                self.createOpponent(splitted[0], playerX, playerY)

    def onSessionReceived(self):
        """Réagit au message indiquant que la session a commencé."""
        self.startGame()

    def onNewPlayerReceived(self, newOpponentName):
        """ Réagit à la réception d'un nouveau joueur.
            Ajoute l'adversaire dans l'application.
        
        Arguments:
            newOpponentName  -- Le pseudo du nouveau joueur.
        """
        print("[EVENT]: " + str(newOpponentName) + " has joined the session !" )
        self.opponentsLock.acquire()
        self.createOpponent(newOpponentName, None, None)
        
        self.opponentsLock.release()
    
    def onPlayerLeftReceived(self, opponentName):
        """ Réagit à la réception du message indiquant qu'un joueur est parti.
            Supprime l'adversaire dans l'application.
        
        Arguments:
            opponentName  -- Le pseudo du joueur qui est parti.
        """
        
        # Supprime l'adversaire du dictionnaire et du canvas
        self.opponentsLock.acquire()
        print("[EVENT]: " + str(opponentName) + " has left the session" )
        self.graphicalApp.deleteChat(opponentName)
        self.opponents.__delitem__(opponentName)
        self.opponentsLock.release()

        self.graphicalApp.removeOpponent(opponentName)
    
    def onObstaclesReceived(self, obstacles):
        """ Réagit à la réception d'obstacles.
            Ajouter les obstacles à l'application.
        
        Arguments:
            obstacles  -- Les nouveaux obstacles.
        """
        pattern = "(-?[0-9]+\\.?[0-9]+E?-?[0-9]*)"
        obstacles = obstacles.split("|")
        # Creation des obstacles
        self.obstaclesLock.acquire()
        for o in obstacles:
            splitted = o.split(":")
            extractedCoord = regexp.findall(pattern, splitted[1])
            obstacleX = float(extractedCoord[0])
            obstacleY =float(extractedCoord[1])
            tupleRes = self.graphicalApp.createGraphicalObstacle(obstacleX, obstacleY)
            tupleRes = (obstacleX, obstacleY) + tupleRes
            self.obstacles.append(tupleRes)
        self.obstaclesLock.release()

    def onNbBombsReceived(self, bombs):
        """ Réagit à la réception du nombre de bombe par joueur.
        
        Arguments:
            bombs  -- Les bombes dont disposent chaque joueur.
        """
        bombs = bombs.split("|")
        # Mise à jour du nombre de bombes que possède les joueurs dans la tableau des scores.
        for b in bombs:
            if b != '':
                splitted = b.split(":")
                nbBomb = int(splitted[1].split("B")[1])
                if splitted[0] == self.playerPseudo:
                    self.nbBomb = nbBomb
                self.graphicalApp.setBombOf(splitted[0], nbBomb)

    def onBombsReceived(self, bombsCoord):
        """ Réagit à la réception du placement des bombes dans la session courante.
        
        Arguments:
            bombsCoord  -- Les coordonnées des bombes.
        """
        pattern = "(-?[0-9]+\\.?[0-9]+E?-?[0-9]*)"
        bombsCoord = bombsCoord.split("|")
        # Creation des bombes
        self.bombsLock.acquire()
        for b in bombsCoord:
            if b != '':
                splitted = b.split(":")
                extractedCoord = regexp.findall(pattern, splitted[1])
                bombX = float(extractedCoord[0])
                bombY =float(extractedCoord[1])
                tupleRes = self.graphicalApp.createGraphicalGenkidma(bombX, bombY)
                tupleRes = (bombX, bombY) + tupleRes
                self.bombs.append(tupleRes)
        self.bombsLock.release()

    def onWinnerReceived(self, scores):
        """ Réagit à la reception d'un message indiquant qu'un joueur à gagné.
            Affiche un message à l'utilisateur et reset l'ensemble de la session afin de se préparer au début d'une nouvelle.
        
        Arguments:
            scores -- Les scores finaux.
        """
        scoreMax = -1
        winnerName = ""
        scores = scores.split("|")
        for score in scores:
            elt = score.split(":")
            if int(elt[1]) > scoreMax:
                scoreMax = int(elt[1])
                winnerName = elt[0]
        
        self.serverMessager.finishUpdating()
        self.graphicalApp.reset()
        self.resetGame()
        self.graphicalApp.showWinner(winnerName, winnerName == self.playerPseudo)

    def onTickReceived(self, vcoords):
        """ Réagit à la réception d'un message de type TICK
            Mettra à jour l'ensemble des joueurs.
        
        Arguments:
            vcoords -- Les nouvelles informations des joueurs de la session.
        """
        pattern = "(-?[0-9]+\\.?[0-9]+E?-?[0-9]*)"
        players = vcoords.split("|")
        # Création des joueurs avec leurs coordonnées
        for p in players:
            splitted = p.split(":")
            extractedCoord = regexp.findall(pattern, splitted[1])
            playerX = float(extractedCoord[0])
            playerY = float(extractedCoord[1])
            playerVX = float(extractedCoord[2])
            playerVY = float(extractedCoord[3])
            playerAngle = float(extractedCoord[4])
            if splitted[0] == self.playerPseudo:
                # On a pas encore reçu la première position du joueur
                # On crée donc le joueur en conséquence
                if self.player == WAITING_FOR_FIRST_TICK:
                    self.createPlayer(splitted[0], playerX, playerY)
                self.player.acquire()
                self.player.fullyUpdate(playerX, playerY, playerVX, playerVY, playerAngle)
                if self.player.isImmobilized():
                    self.stepImmobilizeSituation(self.player)
                self.player.release()
            else:
                self.opponentsLock.acquire()
                if splitted[0] not in self.opponents:
                    self.createOpponent(splitted[0], playerX, playerY)
                opponent = self.opponents[splitted[0]]
                opponent.acquire()
                # On reçoit le tick d'un adversaire n'ayant pas encore de position
                if opponent.getPosition() is None:
                    opponent.fullyUpdateFromScratch(playerX, playerY, playerVX, playerVY, playerAngle)
                    tupleRes = self.graphicalApp.createGraphicalOpponent(playerX, playerY)
                    self.opponents[splitted[0]] = PlayerPod(splitted[0], Pair(playerX, playerY), playerAngle, tupleRes[0], tupleRes[1], tupleRes[2])
                else:
                    opponent.fullyUpdate(playerX, playerY, playerVX, playerVY, playerAngle)

                if opponent.isImmobilized():
                    self.stepImmobilizeSituation(opponent)
                opponent.release()

                self.opponentsLock.release()

    def startGame(self):
        """ Débute une session."""
        self.userCanPlay = True
        self.graphicalApp.showStartMessage()
        self.serverMessager.startUpdating()
    
    def resetGame(self):
        """ Reset une session."""
        # Enlève le joueur
        self.player.acquire()
        self.graphicalApp.deleteFromCanvas(self.player.getCanvasTagId())
        self.player = None
        self.userCanPlay = False
        
        # Enlève les adversaires
        self.opponentsLock.acquire()
        for _, opponent in self.opponents.items():
            opponent.acquire()
            self.graphicalApp.deleteFromCanvas(opponent.getCanvasTagId())
            opponent.release()
        self.opponents = {}
        self.opponentsLock.release()
        
        # Enlève l'objectif courant
        self.graphicalApp.deleteFromCanvas(self.objectif[2])
        self.objectif = ()
        self.objectifCpt = 0
        
        # Enlève les obstacles
        self.obstaclesLock.acquire()
        for obstacle in self.obstacles:
            self.graphicalApp.deleteFromCanvas(obstacle[2])
        self.obstacles = []
        self.obstaclesLock.release()

        # Enlève les bombes
        self.bombsLock.acquire()
        for bomb in self.bombs:
            self.graphicalApp.deleteFromCanvas(bomb[2])
        self.bombs = []
        self.bombsLock.release()
        
        # self.player vaut None, pas besoin de relâcher son lock
        # self.player.release()

    def checkCollisions(self, player):
        """ Vérifie s'il y a une collision entre un joueur et les autres objets de l'application.
            Met à jour le vecteur et la position du joueur en conséquence.
        
        Arguments:
            player -- Le joueur pour lequel on souhaite vérifier s'il entre en collision avec quelque chose.
        """

        pX = player.getPositionX()
        pY = player.getPositionY()
        # On doit tester les collisions avec les adversaires
        if player.getPseudo() == self.player.getPseudo():
            self.opponentsLock.acquire()
            for _, opponent in self.opponents.items():
                opponent.acquire()
                if opponent.getPosition() is not None:
                    oX = opponent.getPositionX()
                    oY = opponent.getPositionY()
                    if self.checkHit(pX, pY, dat.POD_SIDE, oX, oY, dat.ASTEROID_SIDE):
                        self.collisionsJoueurs(player, opponent)
                opponent.release()
            self.opponentsLock.release()
        # On doit tester les collisions avec le joueur principal, et les autres adversaires
        else:
            # Teste avec le joueur principal
            self.player.acquire()
            oX = self.player.getPositionX()
            oY = self.player.getPositionY()
            if self.checkHit(pX, pY, dat.POD_SIDE, oX, oY, dat.ASTEROID_SIDE):
                self.collisionsJoueurs(player, self.player)
            self.player.release()
            # Teste avec les autres adversaires
            self.opponentsLock.acquire()
            for _, opponent in self.opponents.items():
                opponent.acquire()
                if opponent.getPosition() is not None:
                    oX = opponent.getPositionX()
                    oY = opponent.getPositionY()
                    # On ne teste pas la collision avec soi-même
                    if player.getPseudo() != opponent.getPseudo():
                        if self.checkHit(pX, pY, dat.POD_SIDE, oX, oY, dat.ASTEROID_SIDE):
                            self.collisionsJoueurs(player, opponent)
                opponent.release()
            self.opponentsLock.release()

        # Vérifie s'il y a collision avec les obstacles
        self.obstaclesLock.acquire()
        for obstacle in self.obstacles:
            oX = obstacle[0]
            oY = obstacle[1]
            if self.checkHit(pX, pY, dat.POD_SIDE, oX, oY, dat.ASTEROID_SIDE):
                self.collisionsObstacle(player, oX, oY)
        self.obstaclesLock.release()

        # Vérifie s'il y a collision avec les bombes
        """self.bombsLock.acquire()
        for bomb in self.bombs:
            oX = bomb[0]
            oY = bomb[1]
            if self.checkHit(pX, pY, dat.POD_SIDE, oX, oY, dat.GENKIDAMA_SIDE):
                player.immobilize()
        self.bombsLock.release()"""
    
    def checkHit(self, object1X, object1Y, object1Side, object2X, object2Y, object2Side):
        """ Vérifie si deux objets se touchent.
        
        Arguments:
            object1X -- La coordonnée X de l'objet 1.
            object1Y -- La coordonnée Y de l'objet 1.
            object1Side -- La taille de l'objet 1.
            object2X -- La coordonnée X de l'objet 2.
            object2Y -- La coordonnée Y de l'objet 2.
            object2Side -- La taille de l'objet 2.
        
        Returns:
            True s'il y a collision, False sinon.
        """

        object1X -= object1Side
        object1Y -= object1Side

        object2X -= object2Side
        object2Y -= object2Side
        
        distance = ((object1X - object2X) * (object1X - object2X)) + ((object1Y - object2Y) * (object1Y - object2Y))
        # Vérifie si l'objet 1 et l'objet 2 se touchent
        return distance <= ((object1Side/2 + object2Side/2) * (object1Side/2 + object2Side/2))

    def collisionsJoueurs(self, player1, player2):
        """ Gère les mises à jour de vecteur et de position dans le cadre d'une collision
	        entre deux joueurs.
        
        Arguments:
            player1 -- Le premier joueur.
            player2 -- Le premier joueur.
        """

        x1 = player1.getPositionX()
        y1 = player1.getPositionY()
        r1 = dat.POD_SIDE / 2

        x2 = player2.getPositionX()
        y2 = player2.getPositionY()
        r2 = dat.POD_SIDE / 2

        nx = (x2 - x1) / (r1 + r2)
        ny = (y2 - y1) / (r1 + r2)
        gx = -ny
        gy = nx
        v1n = nx * player1.getVectorX() + ny * player1.getVectorY()
        v1g = gx * player1.getVectorX() + gy * player1.getVectorY()
        v2n = nx * player2.getVectorX() + ny * player2.getVectorY()
        v2g = gx * player2.getVectorX() + gy * player2.getVectorY()
        d = sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))

        player1.setVectorX(nx * v2n + gx * v1g)
        player1.setVectorY(ny * v2n + gy * v1g)

        player2.setVectorX(nx * v1n + gx * v2g)
        player2.setVectorY(ny * v1n + gy * v2g)

        player2.setPositionX(x1 + (r1 + r2) * (x2 - x1) / d)
        player2.setPositionY(y1 + (r1 + r2) * (y2 - y1) / d)

    def collisionsObstacle(self, player, obstacleX, obstacleY):
        """ Gère les mises à jour de vecteur et de position dans le cadre d'une collision
	        entre un joueur et un obstacle.
        
        Arguments:
            player -- Le joueur.
            obstacleX -- La coordonnée X de l'obstacle.
            obstacleY -- La coordonnée Y de l'obstacle.
        """
        playerX = player.getPositionX()
        playerY = player.getPositionY()
        playerR = dat.POD_SIDE / 2
        obstacleR = dat.ASTEROID_SIDE / 2

        nx = (playerX - obstacleX) / (obstacleR + playerR)
        ny = (playerY - obstacleY) / (obstacleR + playerR)
        playerPosition = player.getVectorX() * nx + player.getVectorY() * ny
        d = sqrt((obstacleX - playerX) * (obstacleX - playerX) + (obstacleY - playerY) * (obstacleY - playerY))

        player.setVectorX(player.getVectorX() - 2 * playerPosition * nx)
        player.setVectorY(player.getVectorY() - 2 * playerPosition * ny)

        player.setPositionX(obstacleX + (obstacleR + playerR) * (playerX - obstacleX) / d)
        player.setPositionY(obstacleY + (obstacleR + playerR) * (playerY - obstacleY) / d)

    def sendMessage(self, target, message):
        """ Envoie un message du chat.
            Ajoute le message au chat avant de l'envoyer depuis un autre thread (pour ne pas bloquer le thread UI)
        
        Arguments:
            target - Le destinataire du message.
            message -- Le message à envoyer.
        """
        self.graphicalApp.addMessage(target, message, fromMe=True)
        Thread(target=self.sendMessageFromNonGUIThread, args=(target, message)).start()

    def sendMessageFromNonGUIThread(self, target, message):
        """ Envoie un message du chat.
        
        Arguments:
            target - Le destinataire du message.
            message -- Le message à envoyer.
        """
        toSend = ""
        if target == "Public":
            toSend = "ENVOI/"+message+"/"
        else:
            toSend = "PENVOI/"+target+"/"+message+"/"
        self.serverMessager.sendMessage(toSend)

    def onPublicMessageReceived(self, message):
        """Réagit à la réception d'un message publique.
            Affiche le message dans le chat publique.
        
        Arguments:
            message -- Le message reçu.
        """
        self.graphicalApp.addMessage("Public", message)

    def onPrivateMessageReceived(self, src, message):
        """ Réagit à la réception d'un message privé.
            Affiche le message dans le chat correspondant.
        
        Arguments:
            src -- La source du message.
            message -- Le message reçu.
        """
        self.graphicalApp.addMessage(src, message)

    def stepImmobilizeSituation(self, player):
        """Met à jour le statut d'immobilité d'un joueur.
            
            Arguments:
                player -- Le joueur en question.
        """
        player.immobilizedSince += 1
        if player.immobilizedSince % dat.STUN_TIME == 0:
            player.unImmobilize()
            self.graphicalApp.showElement(player.getCanvasTagId())
        elif player.immobilizedSince % 10 == 0:
            self.graphicalApp.showElement(player.getCanvasTagId())
        elif player.immobilizedSince % 5 == 0:
            self.graphicalApp.hideElement(player.getCanvasTagId())