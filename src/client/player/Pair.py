# coding: utf-8

class Pair():
    """Une paire de valeur X,Y."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return str(self.x) + ":" + str(self.y)

    def setX(self, newX):
        """Setter de la valeur X.
        
        Arguments:
            newX -- La nouvelle valeur X.
        """
        self.x = newX
    
    def getX(self):
        """Getteur de la valeur X.
        
        Returns:
            La valeur X.
        """
        return self.x

    def setY(self, newY):
        """Setter de la valeur Y.
        
        Arguments:
            newY -- La nouvelle valeur Y.
        """
        self.y = newY
    
    def getY(self):
        """Getteur de la valeur Y.
        
        Returns:
            La valeur Y.
        """
        return self.y