# coding: utf-8

import threading
import time
import data as dat


class UpdatePlayerThread(threading.Thread):
    """Le thread qui mettra à jour les positions des différents joueurs.."""
    def __init__(self, dispatcher):
        super().__init__()
        self.dispatcher = dispatcher
        self.isInterrupted = False

    def run(self):
        print("[UpdatePlayerThread]: start updating")
        while not self.isInterrupted:
            # Évite un interblocage avec le thread graphique lors de la terminaison de l'application
            threading.Thread(target=self.dispatcher.updateEveryPlayerPosition).start()
            time.sleep(1 / dat.REFRESH_TICRATE)

    def stop(self):
        self.isInterrupted = True