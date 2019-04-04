package game.game_objects;

import game.Data;
import game.interfaces.IGameObject;

/**
 * Un véhicule du jeu.
 *
 */
public class Pod extends AbstractGameObject implements IGameObject {
	
	/** Compteur static de pod.*/
	protected static int count = 1;
	
	/** Le vecteur X du pod.*/
	protected float vectorX;
	
	/** Le vecteur Y du pod.*/
	protected float vectorY;
	
	/** L'angle du pod.*/
	protected float angle;
	
	/** L'id du pod.*/
	protected int id;
	
	/**
	 * Constructeur d'un pod.
	 * @param x La coordonnée X du pod.
	 * @param y La coordonnée Y du pod.
	 */
	public Pod(float x, float y) {
		this.x = x;
		this.y = y;
		this.vectorX = 0;
		this.vectorY = 0;
		this.angle = 0;
		this.id = count;
		count++;
		side = Data.POD_SIDE;
	}
	
	/**
	 * Retourne les coordonnées du pod sous la forme d'une chaîne de caractère non-conforme au protocole.
	 * @return Les coordonnées de l'obstacle.
	 */
	public String getCoordonnees() {
		return "[POD N°"+id+"] : x:"+x+" y:"+y;
	}
	
	/**
	 * Retourne les coordonnées du pod sous la forme d'une chaîne de caractère conforme au protocole.
	 * @return Les coordonnées de l'obstacle.
	 */
	public String getCoord() {
		return "X" + x + "Y" + y;
	}
	
	/**
	 * Retourne le vecteur du pod et son angle sous la forme d'une chaîne de caractère conforme au protocole.
	 * @return Le vecteur du pod et son angle. 
	 */
	public String getVcoord() {
		return getCoord()+"VX" + vectorX + "VY" + vectorY + "T" + Math.toRadians(angle);
	}
	
	/**
	 * Met à jour les information du pod à partir des commandes données en paramètre.
	 * @param angleCmd :  L'ajout à l'angle.
	 * @param thrustCmd : Le nombre de poussé effectuée.
	 */
	public void updateFromCommand(float angleCmd, int thrustCmd) {
		// Mise à jour de l'angle
		this.angle += Math.round(Math.toDegrees(angleCmd) % 360);
		
		double radianAngle = Math.toRadians(this.angle);
		// Mise à jour des vecteurs
		float newVX = this.vectorX;
		newVX += (Data.THRUST * thrustCmd) * Math.cos(radianAngle);
		this.vectorX = newVX;
		
		float newVY = this.vectorY;
		newVY += (Data.THRUST * thrustCmd) * -Math.sin(radianAngle);
		this.vectorY = newVY;
		
		this.x += vectorX;
		this.y += vectorY;
		
		// Le pod quitte l'arène part la droite
		if (this.x > Data.ARENA_L)
			this.x = -Data.ARENA_L + (this.x - Data.ARENA_L);
		// Le pod quitte l'arène part la gauche
		else if (this.x < -Data.ARENA_L)
			this.x = Data.ARENA_L - (this.x + Data.ARENA_L);
		// Le pod quitte l'arène part le haut
		if (this.y > Data.ARENA_H)
			this.y = -Data.ARENA_H + (this.y - Data.ARENA_H);
		// Le pod quitte l'arène part le bas
		else if (this.y < -Data.ARENA_H)
			this.y = Data.ARENA_H - (this.y + Data.ARENA_H);
	}
	
	/**
	 * Met à jour la position du joueur à partir de son vecteur et de son angle.
	 */
	public void updatePosition() {
		this.x += vectorX;
		this.y += vectorY;
		
		// Le pod quitte l'arène part la droite
		if (this.x > Data.ARENA_L)
			this.x = -Data.ARENA_L + (this.x - Data.ARENA_L);
		// Le pod quitte l'arène part la gauche
		else if (this.x < -Data.ARENA_L)
			this.x = Data.ARENA_L - (this.x + Data.ARENA_L);
		// Le pod quitte l'arène part le haut
		if (this.y > Data.ARENA_H)
			this.y = -Data.ARENA_H + (this.y - Data.ARENA_H);
		// Le pod quitte l'arène part le bas
		else if (this.y < -Data.ARENA_H)
			this.y = Data.ARENA_H - (this.y + Data.ARENA_H);
	}

	/**
	 * Getteur sur le vecteur X du pod.
	 * @return Le vecteur X du pod.
	 */
	public float getVectorX() {
		return vectorX;
	}
	
	/**
	 * Setteur du vecteur X du pod.
	 * @param vectorX Le nouveau vecteur X du pod.
	 */
	public void setVectorX(float vectorX) {
		this.vectorX = vectorX;
	}

	/**
	 * Getteur sur le vecteur Y du pod.
	 * @return Le vecteur Y du pod.
	 */
	public float getVectorY() {
		return vectorY;
	}

	/**
	 * Setteur du vecteur Y du pod.
	 * @param vectorY Le nouveau vecteur Y du pod.
	 */
	public void setVectorY(float vectorY) {
		this.vectorY = vectorY;
	}
	
	/**
	 * Immobilise le pod.
	 */
	public void imobilize() {
		this.vectorX = 0;
		this.vectorY = 0;
	}
}
