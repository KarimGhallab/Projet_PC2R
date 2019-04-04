# coding: utf-8

import threading
import socket
import time


class ServerReaderThread(threading.Thread):
    """Le thread qui recevra tous les messages du serveur."""

    def __init__(self, serverMessager, dispatcher):
        super().__init__()
        self.serverMessager = serverMessager
        self.dispatcher = dispatcher
        self.isInterrupted = False
        # Champ utilisé pour éviter de faire des affichages inutiles
        self.displayNext = True
        self.lock = threading.Lock()

    def run(self):
        print("[ServerReaderThread]: start of reading")
        while not self.isInterrupted:
            if self.displayNext:
                print("[ServerReaderThread]: Wainting for a message from the server...")
            message = self.serverMessager.readMessage()
            self.displayNext = False
            # Le serveur a fermé la socket
            if not message:
                break
            else:
                # La lecture à été interrompue par le timeout
                if message != "Timeout-exception":
                    # La tâche peut être très longue
                    # On délègue donc son traitement à un autre thread
                    threading.Thread(target=self.treatMessage, args=(message,)).start()

    def treatMessage(self, message):
        """Traite un message reçu.
        
        Arguments:
            message -- Le message reçu.
        """
        # On ne souhaite traiter qu'un seul message à la fois
        self.lock.acquire()
        splitted = message.split("/")

        # On affiche pas ce message car on le reçoit beaucoup trop souvent
        if splitted[0] != "TICK":
            print("Message received : " + str(splitted))
            self.displayNext = True
        else:
            self.displayNext = False

        # Il se peut qu'on aie reçu plusieurs messages en un, donc on boucle afin traiter l'ensemble
        # des messages si necessaire
        for i in range(0, len(splitted)):
            if splitted[i] == "WELCOME" or splitted[i] == "\nWELCOME":
                phase = splitted[i+1]
                scores = splitted[i+2]
                coord = splitted[i+3]
                obstacles = splitted[i+4]
                bombs = splitted[i+5]
                bombsCoord = splitted[i+6]

                self.dispatcher.onStatusReceived(phase)
                self.dispatcher.onScoresReceived(scores)
                self.dispatcher.onNbBombsReceived(bombs)
                # On a beaucoup de chose à afficher, on parallelise l'ensemble
                tObstacles = threading.Thread(target=self.dispatcher.onObstaclesReceived, args=(obstacles,))
                tBombs = threading.Thread(target=self.dispatcher.onBombsReceived, args=(bombsCoord,))
                tObjectif = threading.Thread(target=self.dispatcher.onObjectifReceived, args=(coord, phase == "wait"))
                
                tObstacles.start()
                tBombs.start()
                tObjectif.start()

                tObstacles.join()
                tBombs.join()
                tObjectif.join()
                i += 6
            elif splitted[i] == "DENIED" or splitted[i] == "\nDENIED":
                # Le thread doit se terminer
                self.isInterrupted = True
                self.dispatcher.showDeniedMessage()
            elif splitted[i] == "NEWPLAYER" or splitted[i] == "\nNEWPLAYER":
                self.dispatcher.onNewPlayerReceived(splitted[i+1])
                i += 1
            elif splitted[i] == "PLAYERLEFT" or splitted[i] == "\nPLAYERLEFT":
                self.dispatcher.onPlayerLeftReceived(splitted[i+1])
                i += 1
            elif splitted[i] == "SESSION" or splitted[i] == "\nSESSION":
                coords = splitted[i+1]
                coord = splitted[i+2]
                obstacles = splitted[i+3]
                self.dispatcher.onPlayersCoordsReceived(coords)
                self.dispatcher.onObjectifReceived(coord)
                self.dispatcher.onObstaclesReceived(obstacles)
                self.dispatcher.onSessionReceived()
                i += 3
            elif splitted[i] == "WINNER" or splitted[i] == "\nWINNER":
                self.dispatcher.onWinnerReceived(splitted[i+1])
                i += 1
            elif splitted[i] == "TICK" or splitted[i] == "\nTICK":
                # Il se peut que l'on reçoive un TICK avant de recevoir un message de type WELCOME
                if self.dispatcher.player is not None:
                    vcoords = splitted[i+1]
                    self.dispatcher.onTickReceived(vcoords)
                i += 1
            elif splitted[i] == "NEWOBJ" or splitted[i] == "\nNEWOBJ":
                coord = splitted[i+1]
                scores = splitted[i+2]
                self.dispatcher.onObjectifReceived(coord)
                self.dispatcher.onScoresReceived(scores)
                i += 2
            elif splitted[i] == "RECEPTION" or splitted[i] == "\nRECEPTION":
                message = splitted[i+1]
                self.dispatcher.onPublicMessageReceived(message)
                i += 1
            elif splitted[i] == "PRECEPTION" or splitted[i] == "\nPRECEPTION":
                message = splitted[i+1]
                src = splitted[i+2]
                self.dispatcher.onPrivateMessageReceived(src, message)
                i += 2
            elif splitted[i] == "HIT" or splitted[i] == "\nHIT":
                pseudo = splitted[i+1]
                bombCoord = splitted[i+2]
                scores = splitted[i+3]
                self.dispatcher.onBombHit(pseudo, bombCoord)
                self.dispatcher.onScoresReceived(scores)
                i += 3
            elif splitted[i] == "PUT" or splitted[i] == "\nPUT":
                pseudo = splitted[i+1]
                bombCoord = splitted[i+2]
                self.dispatcher.onBombPut(pseudo, bombCoord)
                i += 2
        
        self.lock.release()

    def stop(self):
        self.isInterrupted = True
