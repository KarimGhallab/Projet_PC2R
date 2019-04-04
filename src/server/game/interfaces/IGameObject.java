package game.interfaces;

/**
 * Un objet de jeu de notre application.
 * Peut correspondre à un pod joueur, un obstacle ou à un objectif. 
 *
 */
public interface IGameObject {
	/**
	 * Getteur sur la coordonnée X de l'objet.
	 * @return La coordonnée X de l'objet.
	 */
	public float getX();
	
	/**
	 * Setteur de la coordonnée X de l'objet.
	 * @param newX La nouvelle coordonnée X.
	 */
	public void setX(float newX);
	
	/**
	 * Getteur sur la coordonnée Y de l'objet.
	 * @return La coordonnée Y de l'objet.
	 */
	public float getY();
	
	/**
	 * Setteur de la coordonnée Y de l'objet.
	 * @param newY La nouvelle coordonnée Y.
	 */
	public void setY(float newY);
	
	/**
	 * Getteur de la taille du coté de l'objet.
	 * @return La taille edu coté de l'objet.
	 */
	public int getSide();
	
	/**
	 * Vérifie si l'objet de jeu courant et celui passé en paramètre se touchent.
	 * @param go Le deuxième objet.
	 * @return True si les deux objets se touchent, false sinon.
	 */
	public boolean checkHit(IGameObject go);
}
