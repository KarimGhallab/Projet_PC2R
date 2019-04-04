# coding: utf-8

from player.Pair import Pair
from threading import RLock
from math import cos, sin, radians, degrees
import data as dat


class PlayerPod():
    """La classe PlayerPod. Représente un joueur."""
    def __init__(self, pseudo, initialPosition, initialAngle, canvasTagId, image, photoImage):
        """constructeur
        
        Arguments:
            pseudo -- Le pseudo du joueur.
            initialPosition  -- La position initiale du joueur.
            initialAngle -- L'angle initial du joueur.
            canvasTagId -- Le tag du joueur dans le canvas.
            image -- L'image du joueur.
        """
        self.pseudo = pseudo
        self.position = initialPosition
        self.angle = initialAngle
        self.canvasTagId = canvasTagId
        self.image = image
        self.photoImage = photoImage
        self.vector = Pair(0, 0)
        self.updateVector()
        self.lock = RLock()
        self.angleCommand = 0
        self.thrustCommand = 0
        self.immobilized = False
        self.immobilizedSince = 0

    def __str__(self):
        return "Position - " + str(self.position) + ", Vecteur - " + str(self.vector) + ", Angle - " + str(self.angle)

    def acquire(self, blocking=True, timeout=-1):
        """Tente d'obtenir le verrou du joueur.
        
        Keyword Arguments:
            blocking  -- La tentative doit-elle être bloquante ? (default: {True})
            timeout -- Le délai d'attente maximum pour obtenir le verrou (default: {-1})
        
        Returns:
            True si le verrou à été obtenu, False sinon.
        """
        return self.lock.acquire(blocking=blocking, timeout=timeout)


    def release(self):
        """Relâche le verrou du joueur."""
        self.lock.release()

    def getPseudo(self):
        """Getteur sur le pseudo du joueur.
        
        Returns:
            Le pseudo du joueur.
        """
        return self.pseudo

    def getPosition(self):
        """Getteur sur la position du joueur.
        
        Returns:
            La position du joueur.
        """
        return self.position

    def getPositionX(self):
        """Getteur sur la coordonnée X du joueur.
        
        Returns:
            La coordonnée X du joueur.
        """
        return self.position.getX()

    def setPositionX(self, newX):
        """Setteur de la coordonnée X du joueur.
        
        Arguments:
            newX -- La nouvelle coordonnée X du joueur.
        """
        self.position.setX(newX)

    def getPositionY(self):
        """Getteur sur la coordonnée Y du joueur.
        
        Returns:
            La coordonnée Y du joueur.
        """
        return self.position.getY()
    
    def setPositionY(self, newY):
        """Setteur de la coordonnée Y du joueur.
        
        Arguments:
            newY -- La nouvelle coordonnée Y du joueur.
        """
        self.position.setY(newY)

    def getVectorX(self):
        """Getteur sur le vecteur X du joueur.
        
        Returns:
            Le vecteur X du joueur.
        """
        return self.vector.getX()
    
    def setVectorX(self, newX):
        """Setteur sur le vecteur X du joueur.
        
        Arguments:
            newX -- Le vecteur X du joueur.
        """
        self.vector.setX(newX)

    def getVectorY(self):
        """Getteur sur le vecteur Y du joueur.
        
        Returns:
            Le vecteur Y du joueur.
        """
        return self.vector.getY()
    
    def setVectorY(self, newY):
        """Setteur sur le vecteur Y du joueur.
        
        Arguments:
            newY -- Le vecteur Y du joueur.
        """
        self.vector.setY(newY)

    def getAngle(self):
        """Getteur sur l'angle du joueur.
        
        Returns:
            L'angle du joueur.
        """
        return self.angle
    
    def setAngle(self, newAngle):
        """Setteur sur l'angle du joueur.
        
        Arguments:
            newAngle -- Le nouvel angle.
        """
        self.angle = newAngle

    def getCanvasTagId(self):
        """Getteur sur le tag du joueur pour le canvas de l'interface graphique.
        
        Returns:
            Le tag du joueur.
        """
        return self.canvasTagId
    
    def setCanvasTagId(self, newId):
        """Setteur sur le tag du joueur pour le canvas de l'interface graphique.
        
        Arguments:
            newId -- Le nouveau tag du joueur.
        """
        self.canvasTagId = newId

    def getImage(self):
        """Getteur sur l'image du joueur dans l'interface graphique.
        
        Returns:
            L'image du joueur.
        """
        return self.image

    def setImage(self, image):
        """Setteur sur l'image du joueur dans l'interface graphique.
        
        Arguments:
            image -- La nouvelle image du joueur.
        """
        self.image = image

    def setPhotoImage(self, photoImage):
        """Setteur sur la photoImage du joueur dans l'interface graphique.
        
        Arguments:
            photoImage -- La nouvelle photoImage du joueur.
        """
        self.photoImage = photoImage

    def getCommand(self):
        """Retourne les commandes sous forme d'une chaîne de caractère comme spécifié dans le protocole.
        
        Returns:
            Les commandes effectuées sur le pod.
        """
        return "A" + str(radians(self.angleCommand)) + "T" + str(self.thrustCommand)
    
    def resetCommand(self):
        """Reset des commandes du joueur."""
        self.thrustCommand = 0
        self.angleCommand = 0

    def updateVector(self):
        """Met à jour le vecteur du joueur en fonction de son angle."""
        # Met à jour vx
        newVX = self.getVectorX() * cos(radians(self.getAngle()))
        self.setVectorX(newVX)

        # Met à jour vy
        newVY = self.getVectorY() * -sin(radians(self.getAngle()))
        self.setVectorY(newVY)

    def fullyUpdate(self, newX, newY, newVX, newVY, newAngle):
        """Remet entièrement à jour un joueur.
        
        Arguments:
            newX  -- La nouvelle coordonnée X.
            newY -- La nouvelle coordonnée Y.
            newVX -- Le nouveau vecteur X.
            newVY -- Le nouveau vecteur Y.
            newAngle -- Le nouvel angle.
        """

        self.position.setX(newX)
        self.position.setY(newY)
        self.vector.setX(newVX)
        self.vector.setY(newVY)
        self.setAngle(round(degrees(newAngle)))

    def fullyUpdateFromScratch(self, newX, newY, newVX, newVY, newAngle):
        """Remet entièrement à jour un joueur jusque la sans position ni vecteur.
        
        Arguments:
            newX  -- La nouvelle coordonnée X.
            newY -- La nouvelle coordonnée Y.
            newVX -- Le nouveau vecteur X.
            newVY -- Le nouveau vecteur Y.
            newAngle -- Le nouvel angle.
        """
        self.position = Pair(newX, newY)
        self.vector = Pair(newVX, newVY)
        self.angle = round(degrees(newAngle))

    def thrust(self):
        """Applique une impulsion au joueur. Met à jour ses vecteurs."""
        # Met à jour vx.
        newVX = self.getVectorX()
        newVX += dat.THRUST_IT * cos(radians(self.getAngle()))
        self.setVectorX(newVX)

        # Met à jour VY
        newVY = self.getVectorY()
        newVY += dat.THRUST_IT * -sin(radians(self.getAngle()))
        self.setVectorY(newVY)
        
        self.thrustCommand += 1

    def antiClock(self):
        """Applique une rotation inverse sur le joueur. Met à jour son angle"""
        newAngle = self.getAngle() + dat.TURN_IT
        self.setAngle(newAngle % 360)
        self.angleCommand += dat.TURN_IT

    def clock(self):
        """Applique une rotation sur le joueur. Met à jour son angle"""
        newAngle = self.getAngle() - dat.TURN_IT
        self.setAngle(newAngle % 360)
        self.angleCommand -= dat.TURN_IT

    def reverseVectors(self):
        """Inverse les vecteurs du joueur."""
        self.setVectorX(-self.getVectorX())
        self.setVectorY(-self.getVectorY())

    def isImmobilized(self):
        """ Un joueur est-il actuellement immobilisé ?
        
        Returns:
            True si le joueur est immobilisé, False sinon.
        """
        return self.immobilized
    
    def immobilize(self):
        """Immobilise un joueur."""
        self.immobilized = True
        self.immobilizedSince = 0

    def stepImmobilize(self):
        """Met à jour le nombre de server_tickrate écoulé depuis que le jouer est immobilisé."""
        self.immobilizedSince += 1

    def unImmobilize(self):
        """Redonne la possibilité à un joueur de bouger."""
        self.immobilized = False
        self.immobilizedSince = 0
