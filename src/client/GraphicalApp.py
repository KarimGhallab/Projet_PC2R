# coding: utf-8

from tkinter import messagebox
from tkinter.ttk import Progressbar, Treeview, Notebook
from PIL import Image, ImageTk
from threading import Lock, Thread
from time import gmtime, strftime
import tkinter as tk
import random
import data as dat


class GraphicalApp(tk.Frame):
    """Interface graphique du jeu."""
    
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.master = None
        self.treeview = None
        self.chats = {}     # contient des listes [id, treeview, entry, bouton, messageCpt]
        self.progress = None
        self.previousAngles = {}
        self.initializeGraphicalApp()

        self.dispatcher.setGraphicalApp(self)
        self.mainloop()

    def initializeGraphicalApp(self):
        """Initialise l'interface graphique."""
        self.master = tk.Tk()
        self.master.title("To the conquest of the dragon balls !")
        super().__init__(self.master)
        self.master.resizable(False, False)
        
        self.createWidgets()
        self.setUpBindingEvent()
        self.master.protocol("WM_DELETE_WINDOW", self.closeWindow)
        msg = "Welcome space travelers !\n\n"
        msg += "A brand new race has been created. "
        msg += "You may ask yourself : \"Why should i participate ?\" "
        msg += "Well because the reward is worth it, it's nothing more than the seven dragon balls !\n"
        msg += "Suddenly fell more excited right ?!\n"
        msg += "But watch out, you are not the only one interested...\n\n"
        msg += "In order to move your vehicle, use your keyboard's directional arrows.\n"
        msg += "You can also drop a bomb with the \"B\" button.\n\n"
        msg += "Good luck !"
        messagebox.showinfo(title="Welcome !", message=msg)

    def createWidgets(self):
        """Crée tous les widgets de l'interface."""
        tk.Label(self.master, text="Your pseudo", font="-weight bold").grid(row=0, column=0, sticky=tk.W)
        self.pseudoEntry = tk.Entry(self.master)
        self.pseudoEntry.grid(row=0, column=1, sticky=tk.EW)

        self.pseudoEntry.focus_set()

        tk.Label(self.master, text="Status : ", font="-weight bold").grid(row=1, column=0, sticky=tk.W)
        self.statusLabel = tk.Label(self.master, text="Not yet connected...")
        self.statusLabel.grid(row=1, column=1, sticky=tk.W)
        self.progress = Progressbar(self.master, orient=tk.HORIZONTAL, mode='indeterminate')
        self.progress.grid(row=1, column=2)

        self.exitButton = tk.Button(self.master)
        self.exitButton["text"] = "Exit"
        self.exitButton["state"] = tk.DISABLED
        self.exitButton["bg"] = "#FF0A2D"
        self.exitButton["activebackground"] = "#FF415C"
        self.exitButton["fg"] = "#FFFFFF"
        self.exitButton["activeforeground"] = "#FFFFFF"
        self.exitButton["relief"] = tk.FLAT
        self.exitButton["bd"] = 0
        self.exitButton["command"] = lambda: self.dispatcher.onExitClicked()
        self.exitButton.grid(row=2, column=1, sticky=tk.EW)
        
        self.connectionButton = tk.Button(self.master)
        self.connectionButton["text"] = "Connect to the server"
        self.connectionButton["bg"] = "#1296EC"
        self.connectionButton["activebackground"] = "#33A5EF"
        self.connectionButton["fg"] = "#FFFFFF"
        self.connectionButton["activeforeground"] = "#FFFFFF"
        self.connectionButton["relief"] = tk.FLAT
        self.connectionButton["bd"] = 0
        self.connectionButton["command"] = lambda: self.onConnectionClicked(self.connectionButton)
        self.connectionButton.grid(row=2, column=0, sticky=tk.EW)

        self.createScoreTable()
        self.createSpaceEnvironment()

        self.notebook = Notebook(self.master)
        self.notebook.grid(row=5, column=3, columnspan=2, rowspan=3, sticky=tk.NSEW)
        self.createChat("Public", enable=False)

    def setUpBindingEvent(self):
        """Met en place tous les événement permettant eu joueur de contrôler son pod."""
        # Les code de mise à jour du joueur doivent être exécutés dans un autre thread.
        # Dans le cas contraire, il y a un interblocage entre le thread de
        # l'interface graphique (celui-ci), et celui qui met à jour périodiquement les position des joueurs.
        self.master.bind('<Left>', self.dispatcher.antiClockEvent)
        self.master.bind('<Right>', self.dispatcher.clockEvent)
        self.master.bind('<Up>', self.dispatcher.thrustEvent)
        self.master.bind('b', self.dispatcher.putBomb)

    def createSpaceEnvironment(self):
        """Crée un décor spatial."""
        self.canvasLock = Lock()
        self.canvas = tk.Canvas(self.master, width=dat.ARENA_L*2, height=dat.ARENA_H*2, bg="black")
        self.canvas.grid(row=5, column=0, columnspan=3, rowspan=5, pady=(10, 0))

        # Ajoute 200 étoiles
        for __ in range(0, 200):
            self.drawRandomStar()

    def drawRandomStar(self):
        """Dessine une étoile à une position aléatoire."""
        maxX = int(self.canvas["width"])
        maxY = int(self.canvas["height"])

        x = random.randint(0, maxX)
        y = random.randint(0, maxY)
        self.canvas.create_oval(x, y, x+5, y+5, fill="white")

    def createScoreTable(self):
        """Crée le tableau des scores."""
        tk.Label(self.master, text="Scores", font="-weight bold").grid(row=3, column=0, columnspan=2)
        tv = Treeview(self.master, height=3)
        tv['columns'] = ('Score', "Bomb")
        tv.heading("#0", text='User', anchor=tk.W)
        tv.heading('Bomb', text='Bombs available', anchor=tk.W)
        tv.column('Bomb', anchor=tk.W, width=100)
        tv.heading('Score', text='Score', anchor=tk.W)
        tv.column('Score', anchor=tk.W, width=100)
        tv.grid(row=4, column=0, columnspan=3, sticky=tk.EW)
        self.treeview = tv

    def increaseBombOf(self, player):
        """Incrémente le nombre de bombe que possède un joueur dans le tableau d'affichage.
        
        Arguments:
            player - Le pseudo du joueur pour lequel on doit incrémenter son nombre de bombe.
        """
        for i in self.treeview.get_children():
            item = self.treeview.item(i)
            # Nous sommes bien sur l'item du joueur qui nous interesse
            if item["text"] == player:
                oldValue = item['values']
                oldValue[1] += 1
                self.treeview.item(i, values=oldValue)
                break
    
    def decreaseBombOf(self, player):
        """Décrémente le nombre de bombe que possède un joueur dans le tableau d'affichage.
        
        Arguments:
            player - Le pseudo du joueur pour lequel on doit décrémenter son nombre de bombe.
        """
        for i in self.treeview.get_children():
            item = self.treeview.item(i)
            # Nous sommes bien sur l'item du joueur qui nous interesse
            if item["text"] == player:
                oldValue = item['values']
                oldValue[1] -= 1
                self.treeview.item(i, values=oldValue)
                break

    def setBombOf(self, player, nbBomb):
        """Met à jour le nombre de bombe que possède un joueur dans le tableau d'affichage.
        
        Arguments:
            player - Le pseudo du joueur pour lequel on doit mettre à jour son nombre de bombe.
            nbBomb - Le nouveau nombre de bombe du joueur.
        """
        for i in self.treeview.get_children():
            item = self.treeview.item(i)
            # Nous sommes bien sur l'item du joueur qui nous interesse
            if item["text"] == player:
                oldValue = item['values']
                oldValue[1] = nbBomb
                self.treeview.item(i, values=oldValue)
                break

    def createChat(self, nom, enable=True):
        """Créer un nouveau chat pour un joueur donné.
        
        Arguments:
            nom - Le nom du joueur avec lequel l'utilisateur pourra parler avec ce chat
        
        Keyword Arguments:
            enable -- Est-ce que le chat doit être activer par défaut. (default: {True})
        """
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text=nom)
        chat = Treeview(frame, height=15)
        chat['columns'] = ('Date')
        chat.heading("#0", text='Messages', anchor=tk.W)
        chat.heading('Date', text='Date', anchor=tk.W)
        chat.column('Date', anchor=tk.W, width=150)
        chat.grid(row=0, column=0, columnspan=2, rowspan=3, sticky=tk.NSEW)
        chat.tag_configure('even', background='#DAE5F4')
        chat.tag_configure('odd', background='#B8D1F3')
        chat.tag_configure('from_me', font=("Helvetica", 10, "bold"))
        chat.tag_configure('not_from_me', font=("Helvetica", 10))
        messageEntry = tk.Entry(frame)
        messageEntry.grid(row=4, column=0, sticky=tk.S)

        messageButton = tk.Button(frame)
        messageButton["text"] = "Envoyer"
        if not enable:
            messageButton["state"] = tk.DISABLED
        messageButton["bg"] = "#1296EC"
        messageButton["activebackground"] = "#33A5EF"
        messageButton["fg"] = "#FFFFFF"
        messageButton["activeforeground"] = "#FFFFFF"
        messageButton["relief"] = tk.FLAT
        messageButton["bd"] = 0
        messageButton["command"] = lambda: self.sendMessage(nom, messageEntry)
        messageButton.grid(row=4, column=1, sticky=tk.S)

        self.chats[nom] = [frame, chat, messageEntry, messageButton, 0]

    def deleteChat(self, name):
        """Supprime un chat permmetant de communiquer avec un joueur donnée.
        
        Arguments:
            name -- Le nom du joueur pour lequel on doit supprimer le chat.
        """
        self.notebook.forget(self.chats[name][0])

    def sendMessage(self, target, entry):
        """Signale au dispatcher la volonté de l'utilisateur d'envoyer un message.
        
        Arguments:
            target -- La cible à laquelle le joueur souhaite envoyer le message.
            entry -- L'entry source sur laquelle l'utilisateur a saisi son message.
        """
        message = entry.get()
        if message == "":
            messagebox.showerror(title="Empty message", message="You cannot send an empty message")
        else:
            self.dispatcher.sendMessage(target, message)
            entry.delete(0, tk.END)
    
    def addMessage(self, chatName, message, fromMe=False):
        """Ajout un message à un chat.
        
        Arguments:
            chatName -- Le nom du chat.
            message -- Le message.
        
        Keyword Arguments:
            fromMe -- Indique si le message vient de l'utilisateur de l'application cliente. (default: {False})
        """
        currentDate = strftime("%d/%m/%Y-%H:%M:%S", gmtime())
        fromMeTag = 'from_me' if fromMe else 'not_from_me'
        odd_even_tag = 'even' if (self.chats[chatName][4] % 2) == 0 else 'odd'
        
        self.chats[chatName][1].insert('', 'end', text=message, values=currentDate, tags=(odd_even_tag, fromMeTag))
        self.chats[chatName][4] += 1

    def addScoreToTable(self, user, score):
        """ Ajoute un nouveau score au tableau des scores.
            Si le joueur est déjà présent, met à jour sa ligne.
        
        Arguments:
            user  -- Un pseudo.
            score -- Un score.
        """
        edited = False
        for i in self.treeview.get_children():
            item = self.treeview.item(i)
            # Nous sommes bien sur l'item du joueur qui nous interesse
            if item["text"] == user:
                oldValue = item['values']
                oldValue[0] = score
                self.treeview.item(i, values=oldValue)
                edited = True
                break
        
        if not edited:
            self.treeview.insert('', 'end', text=str(user), values=(str(score), "0"))
    
    def createGraphicalPlayer(self, playerX, playerY):
        """Crée un joueur à une position spécifique.
        
        Arguments:
            playerX -- La coordonnée X du joueur.
            playerY -- La coordonnée Y du joueur.
        
        Returns:
            tuple -- Un tuple contenant le tag du joueur dans le canvas et ses images.
        """
        convertedPos = self.convertPosition(playerX, playerY)
        playerImage = Image.open('images/pod_sprite_50.png')
        podPicture = ImageTk.PhotoImage(playerImage)
        
        self.canvasLock.acquire()
        tagPlayer = self.canvas.create_image(convertedPos[0], convertedPos[1], image=podPicture)
        self.canvasLock.release()

        return (tagPlayer, playerImage, podPicture)

    def createGraphicalOpponent(self, playerX, playerY):
        """Crée un adversaire à une position spécifique.
        
        Arguments:
            playerX -- La coordonnée X de l'adversaire.
            playerY -- La coordonnée Y de l'adversaire.
        
        Returns:
            tuple -- Un tuple contenant le tag de l'adversaire dans le canvas et ses images.
        """
        convertedPos = self.convertPosition(playerX, playerY)
        opponentImage = Image.open('images/pod2_sprite_50.png')
        podPicture = ImageTk.PhotoImage(opponentImage)
        
        self.canvasLock.acquire()
        tagOpponent = self.canvas.create_image(convertedPos[0], convertedPos[1], image=podPicture)
        self.canvasLock.release()

        return (tagOpponent, opponentImage, podPicture)

    def createGraphicalObstacle(self, obstacleX, obstacleY):
        """Crée un obstacle à une position spécifique.
        
        Arguments:
            obstacleX -- La coordonnée X de l'obstacle.
            obstacleY -- La coordonnée Y de l'obstacle.
        
        Returns:
            tuple -- Un tuple contenant le tag de l'obstacle dans le canvas et sa photoImage.
        """
        convertedPos = self.convertPosition(obstacleX, obstacleY)
        obstacleImage = Image.open('images/obstacles/asteroid_sprite_55.png')
        obstaclePicture = ImageTk.PhotoImage(obstacleImage)
        
        self.canvasLock.acquire()
        tagOstacle = self.canvas.create_image(convertedPos[0], convertedPos[1], image=obstaclePicture)
        self.canvasLock.release()

        return (tagOstacle, obstaclePicture)

    def createGraphicalGenkidma(self, genkidamaX, genkidamaY):
        """Crée un genkidama à une position spécifique.
        
        Arguments:
            genkidamaX -- La coordonnée X du genkidama.
            genkidamaY -- La coordonnée Y du genkidama.
        
        Returns:
            tuple -- Un tuple contenant le tag du genkidama dans le canvas et sa photoImage.
        """
        convertedPos = self.convertPosition(genkidamaX, genkidamaY)
        genkidamaImage = Image.open('images/bombs/spirit_bomb_35.png')
        genkidamaPicture = ImageTk.PhotoImage(genkidamaImage)
        
        self.canvasLock.acquire()
        tagGenkidama = self.canvas.create_image(convertedPos[0], convertedPos[1], image=genkidamaPicture)
        self.canvasLock.release()

        return (tagGenkidama, genkidamaPicture)

    def deleteGraphicalGenkidma(self, genkidamaX, genkidamaY):
        """Enlève un genkidama situé à une position spécifique.
        
        Arguments:
            genkidamaX -- La coordonnée X du genkidama.
            genkidamaY -- La coordonnée Y du genkidama.
        
        Returns:
            tuple -- Un tuple contenant le tag du genkidama dans le canvas et sa photoImage.
        """
        convertedPos = self.convertPosition(genkidamaX, genkidamaY)
        
        self.canvasLock.acquire()
        tagGenki = self.canvas.find_closest(convertedPos[0], convertedPos[1])
        self.canvas.delete(tagGenki)
        self.canvasLock.release()

    def onConnectionClicked(self, button):
        """Handler du clique sur le bouton de connexion
        
        Arguments:
            button -- Le bouton source.
        """
        pseudo = self.pseudoEntry.get()
        if pseudo == "":
            msg = "No pseudo given. You have to give a pseudo in order to connect to the server."
            messagebox.showerror(title="No pseudo", message=msg)
        else:
            success = self.dispatcher.onConnectionClicked(pseudo)
            if success:
                button["state"] = tk.DISABLED
                self.exitButton["state"] = tk.NORMAL
                self.chats["Public"][3]["state"] = tk.NORMAL
                self.statusLabel["text"] = "Connection succeed !"
                self.pseudoEntry.delete(0, tk.END)
            else:
                msg = "Connection to the server failed.\nMake sure the server is running."
                messagebox.showerror(title="Connection failed", message=msg)

    def closeWindow(self):
        """Handler de la fermeture de la fenêtre.
           Signale au dispatcher que l'utilisateur souhaite quitter l'application et ferme l'interface.
        """
        self.dispatcher.onCloseWindow()
        # Il se peut qu'un thread soit bloqué en attente d'une réponse du thread de l'interface
        # En exécutant un update, on va le débloquer
        self.master.update()
        self.master.destroy()

    def updateUIPlayer(self, player):
        """Met à jour la position et l'angle de rotation d'un joueur.
        
        Arguments:
            player -- Le joueur.
        """
        self.canvasLock.acquire()
        if player.getPseudo() not in self.previousAngles or self.previousAngles[player.getPseudo()] != player.getAngle():
            self.rotatePlayer(player)
        self.updatePlayer(player)
        self.canvasLock.release()

    def updatePlayer(self, player):
        """Met à jour la position d'un joueur.
        
        Arguments:
            player -- Le joueur.
        """
        convertedPos = self.convertPosition(player.getPositionX(), player.getPositionY())
        self.canvas.coords(player.getCanvasTagId(), (convertedPos[0], convertedPos[1]))
    
    def rotatePlayer(self, player):
        """Met à jour l'angle de rotation d'un joueur.
        
        Arguments:
            player -- Le joueur.
        """
        self.previousAngles[player.getPseudo()] = player.getAngle()
        self.canvas.delete(player.getCanvasTagId())
        podPicture = ImageTk.PhotoImage(player.getImage().rotate(player.getAngle()))
        convertedPos = self.convertPosition(player.getPositionX(), player.getPositionY())
        newId = self.canvas.create_image(convertedPos[0], convertedPos[1], image=podPicture)
        player.setCanvasTagId(newId)
        player.setPhotoImage(podPicture)

    def convertPosition(self, x, y):
        """Convertie des coordonnées pour qu'elle soit utilisable par le canvas.
        
        Arguments:
            x -- La coordonnée X.
            y -- La coordonnée Y.
        
        Returns:
            tuple(x, y) -- Un tuple contenant les positions converties.
        """
        newX = x + dat.ARENA_L
        newY = y + dat.ARENA_H
        
        return (newX, newY)

    def showDeniedMessage(self):
        """Affiche un message indiquant à l'utilisateur que sa tentative de connexion à été refusée."""
        msg = "The server refused the connection.\nYou may try again with an other pseudo"
        messagebox.showerror(title="Connection refused", message=msg)
        self.statusLabel["text"] = "Pseudo already used..."
        self.connectionButton["state"] = tk.NORMAL

    def showWaitingMessage(self):
        """Met à jour le label de status pour indiquer à l'utilisateur d'attendre le début de la partie."""
        print("Waiting")
        self.statusLabel["text"] = "Waiting for game to start..."
        self.progress.start(10)

    def showStartMessage(self):
        """Met à jour le label de status pour indiquer à l'utilisateur que la partie à commencé."""
        print("Good game")
        self.statusLabel["text"] = "Good game !"
        self.progress.stop()

    def showWinner(self, winnerName, iWin):
        """Affiche une fenêtre avec le nom du gagnant.
        
        Arguments:
            winnerName  -- Le nom du gagnant.
            iWin  -- Indique si le gagnant est le joueur actuel.
        """
        msg = ""
        if iWin:
            msg = "Congratulation you have won !"
        else:
            msg = winnerName + " has won !"
        messagebox.showinfo(title="We have a winner !", message=msg)

    def showObjectif(self, objectifX, objectifY, objectifNumber):
        """Ajoute un objectif (une dragon ball).
        
        Arguments:
            objectifX  -- La coordonnée X de l'objectif.
            objectifY  -- La coordonnée Y de l'objectif.
            objectifNumber  -- Le numéro de l'objectif (utiliser pour choisir quelle dragon ball utiliser).
        
        Returns:
            tuple(idTag, photoImage) -- Un tuple contenant le tag de l'objectif et son image.
        """
        converted = self.convertPosition(objectifX, objectifY)
        newImage = Image.open('images/dragon_ball/ball_'+str(objectifNumber)+".png")
        newPhotoImage = ImageTk.PhotoImage(newImage)
        
        self.canvasLock.acquire()
        tagImage = self.canvas.create_image(converted[0], converted[1], image=newPhotoImage)
        self.canvasLock.release()
        
        return (tagImage, newPhotoImage)

    def reset(self):
        """Remet à zéro l'application graphique."""
        self.resetScores()
        for(_, chat) in self.chats.items():
            self.notebook.forget(chat[0])
        
        self.chats = {}
        # On ajoute de nouveau le chat public
        self.createChat("Public", enable=True)
        

    def resetScores(self):
        """Remet à zéro le tableau des scores."""
        self.progress.stop()
        for i in self.treeview.get_children():
            self.treeview.delete(i)
    
    def removeOpponent(self, opponentName):
        """Supprime un adversaire dde l'interface graphique.
        
        Arguments:
            opponentName -- Le nom de l'adversaire.
        """
        for child in self.treeview.get_children():
            item = self.treeview.item(child)
            if (item["text"]) == opponentName:
                self.treeview.delete(child)

        if opponentName in self.chats:
            del self.chats[opponentName]

    def deleteFromCanvas(self, tag):
        """Supprime un élément du canavas identifié par son tag.
        
        Arguments:
            tag  -- Le tag de l'élément à supprimer.
        """
        self.canvas.delete(tag)

    def showElement(self, tag):
        self.canvas.itemconfigure(tag, state='normal')
    
    def hideElement(self, tag):
        self.canvas.itemconfigure(tag, state='hidden')