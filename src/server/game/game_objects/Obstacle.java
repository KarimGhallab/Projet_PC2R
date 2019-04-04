package game.game_objects;

import game.Data;
import game.interfaces.IGameObject;

/**
 * Un obstacle de notre jeu.
 *
 */
public class Obstacle extends AbstractGameObject implements IGameObject {

	/** L'id de l'obstacle.*/
	private int id;
	
	/**
	 * Constructeur d'un objectif, génére des coordonnées aléatoires et assigne la taille d'un objectif.
	 * @param id : L'id de l'obstacle.
	 */
	public Obstacle(int id) {
		super();
		side = Data.ASTEROID_SIDE;
		this.id = id;
	}
	
	/**
	 * Retourne les coordonnées de l'obstacle sous la forme d'une chaîne de caractère conforme au protocole.
	 * @return Les coordonnées de l'obstacle.
	 */
	public String getObstacleCoord() {
		return "obs"+id+":"+"X" + x + "Y" + y;
	}
	
	/**
	 * Getteur sur l'id de l'obstacle.
	 * @return L'id de l'obstacle.
	 */
	public int getId() {
		return id;
	}
}
