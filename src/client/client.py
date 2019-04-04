# coding: utf-8
"""Main de l'application cliente."""
import signal
import sys
import json
import data as dat
from GraphicalApp import GraphicalApp
from dispatcher.Dispatcher import Dispatcher
from communication.ServerMessager import ServerMessager

dat.setUpData()

disp = Dispatcher()

def signal_handler(signal, frame):
        disp.onExitClicked()

# Ferme proprement l'application en cas de réception d'un signal CTRL-C
signal.signal(signal.SIGINT, signal_handler)

serverMessager = ServerMessager("localhost", 1234, disp)
disp.setServerMessager(serverMessager)

gApp = GraphicalApp(disp)
