# coding: utf-8

import threading
import socket
import time
import data as dat


class CommandSenderThread(threading.Thread):
    """Le thread qui enverra tous les server_tickrate les nouvelles commandes du joueur."""

    def __init__(self, serverMessager, dispatcher):
        super().__init__()
        self.serverMessager = serverMessager
        self.dispatcher = dispatcher
        self.isInterrupted = False

    def run(self):
        print("[CommandSenderThread]: start of sending")
        while not self.isInterrupted:
            # Peut renvoyer None si l'on a pas obtenu le verrou sur le joueur avant le timeout
            # Évite un interblocage avec le thread graphique lors de la fermeture de l'application
            command = self.dispatcher.getPlayerCommand()
            if command is not None:
                self.serverMessager.sendMessage("NEWCOM/" + command + "/")
                self.dispatcher.resetPlayerCommand()
                time.sleep(1 / dat.SERVER_TICRATE)

    def stop(self):
        self.isInterrupted = True
