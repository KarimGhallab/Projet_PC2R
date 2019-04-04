# coding: utf-8

import socket
from communication.threads.ServerReaderThread import ServerReaderThread
from communication.threads.UpdatePlayerThread import  UpdatePlayerThread
from communication.threads.CommandSenderThread import CommandSenderThread

class ServerMessager():
    """Gère les communications avec le serveur."""
    def __init__(self, host, port, dispatcher):
        """Constructor.
        
        Arguments:
            host -- Le nom d'host du serveur.
            port -- Le numéro de port du serveur.
            dispatcher -- Le dispatcher de l'application.
        """
        self.host = host
        self.port = port
        self.sock = None
        self.serverReaderThread = None
        self.updatePlayerThread = None
        self.commandSenderThread = None
        self.dispatcher = dispatcher

    def connect(self, pseudo):
        """Établie une connexion avec le serveur.
        
        Arguments:
            pseudo -- Le pseudo que l'utilisateur veut.
        
        Returns:
            True si la connection s'est bien déroulée, False sinon.
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # On place un timeout afin de ne pas bloquer la lecture
        # Cela permet au thread lecteur de vérifier régulièrement s'il doit se terminer
        self.sock.settimeout(0.5)
        print("[ServerMessager] : Connection to the server...")
        try:
            self.sock.connect((self.host, self.port))
        except socket.error:
            print("[ServerMessager] : Connection failed")
            return False

        print("[ServerMessager] : Connection success")
        self.serverReaderThread = ServerReaderThread(self, self.dispatcher)
        self.serverReaderThread.start()

        connectMsg = "CONNECT/"+pseudo+"/"
        self.sendMessage(connectMsg)

        return True

    def sendMessage(self, message):
        """Envoi un message au serveur.
        
        Arguments:
            message -- Le message à envoyer.
        """
        if self.sock is not None:
            message += "\n"
            # On ne peut qu'envoyer des tableau de byte, il faut donc encoder le message
            self.sock.send(message.encode())
    
    def readMessage(self):
        """Lit un message.
        
        Returns:
            Un message envoyé par le serveur.
        """
        if self.sock is not None:
            try:
                message = self.sock.recv(1024)
                if not message:
                    return None
                else:
                    # Décode le message (tableau de byte --> string)
                    return message.decode()
            # On a dépassé le timeout
            except socket.timeout:
                return "Timeout-exception"
        else:
            return None

    def sendExitMessage(self, pseudo):
        """Envoie au serveur le message indiquant que le joueur quitte la session.
        
        Arguments:
            pseudo -- Le pseudo du joueur.
        """
        message = "EXIT/" + str(pseudo) + "/"
        self.sendMessage(message)

    def closeConnection(self, playerPseudo):
        """Ferme la connexion avec le serveur et envoie l'ordre d'interruption aux différents thread de communication.
        
        Arguments:
            playerPseudo -- La pseudo du joueur.
        """
        if self.serverReaderThread is not None:
            self.serverReaderThread.stop()
        if self.updatePlayerThread is not None:
            self.updatePlayerThread.stop()
        if self.commandSenderThread is not None:
            self.commandSenderThread.stop()
        
        # On attend la fin de tous les threads
        if self.serverReaderThread is not None:
            print("Waiting for ServerReaderThread to finish...", end="", flush=True)
            self.serverReaderThread.join()
            print("done")
        if self.updatePlayerThread is not None:
            print("Waiting for UpdatePlayerThread to finish...", end="", flush=True)
            self.updatePlayerThread.join()
            print("done")
        if self.commandSenderThread is not None:
            print("Waiting for CommandSenderThread to finish...", end="", flush=True)
            self.commandSenderThread.join()
            print("done")

        # Tous les thread sont terminés, on envoie au serveur le message EXIT
        self.sendExitMessage(playerPseudo)
        if self.sock is not None:
            self.sock.close()

    def startUpdating(self):
        """ Lance deux threads gérant les mises à jour des données des joueurs.
            Le premier mettant à jour régulièrement les positions du joueur et de ses adversaires,
            Et le second envoyant régulièrement les commandes du joueur au serveur.
        """
        self.updatePlayerThread = UpdatePlayerThread(self.dispatcher)
        self.updatePlayerThread.start()

        self.commandSenderThread = CommandSenderThread(self, self.dispatcher)
        self.commandSenderThread.start()

    def finishUpdating(self):
        """Interrompt et attend la fin des deux threads créé avec par la methode "startUpdating(self)."""

        self.updatePlayerThread.stop()
        self.commandSenderThread.stop()

        print("Waiting for UpdatePlayerThread to finish...", end="", flush=True)
        self.updatePlayerThread.join()
        self.updatePlayerThread = None
        print("done")
        
        print("Waiting for CommandSenderThread to finish...", end="", flush=True)
        self.commandSenderThread.join()
        self.commandSenderThread = None
        print("done")