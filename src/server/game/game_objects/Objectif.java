package game.game_objects;

import game.Data;
import game.interfaces.IGameObject;

/**
 * Un objectif du jeu. 
 *
 */
public class Objectif extends AbstractGameObject implements IGameObject{
	
	/**
	 * Constructeur d'un objectif, génére des coordonnées aléatoires et assigne la taille d'un objectif.
	 */
	public Objectif() {
		super();
		side = Data.BALL_SIDE;
	}

	/**
	 * Genere de nouvelles coordonnees pour l'objectif.
	 */
	public void newCoord() {
		x = Data.generateRandomX();
		y = Data.generateRandomY();
	}
	
	/**
	 * Retourne les coordonnées de l'objectif sous la forme d'une chaîne de caractère conforme au protocole.
	 * @return Les coordonnées de l'objectif.
	 */
	public String getObjectifCoord() {
		return "X" + x + "Y" + y;
	}
}
