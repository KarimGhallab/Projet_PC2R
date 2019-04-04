package game;

import java.net.Socket;

import game.game_objects.Pod;

/**
 * Classe représentant un joueur.
 *
 */
public class Player {
	/** La socket de communication du joueur.*/
	private Socket socket;
	
	/** Le pod du joueur.*/
	private Pod pod;
	
	/** Les bombes que possède un joueur.*/
	private int nbSpiritBombs;
	
	/** Indique si le joueur est immobilisé par une bombe.*/
	private boolean isImobilized;
	
	/** Indique depuis combien de temps un joueur est immobilisé.*/
	private int imobilizedCpt;
	
	/**
	 * Constructeur d'un joueur.
	 * @param socket : 	Sa socket de communication.
	 * @param pod : 	Son pod.
	 * @param nbBombs : nombre de spirit bombs que possède le joueur au depart.
	 */
	public Player(Socket socket, Pod pod, int nbBombs) {
		this.socket = socket;
		this.pod = pod;
		this.nbSpiritBombs = nbBombs;
		isImobilized = false;
		imobilizedCpt = 0;
	}
	
	/**
	 * Getteur sur la socket du joueur.
	 * @return La socket du joueur.
	 */
	public Socket getSocket() {
		return socket;
	}
	
	/**
	 * Getteur sur le pod du joueur.
	 * @return Le pod du joueur.
	 */
	public Pod getPod() {
		return pod;
	}
	
	/**
	 * Met à jour les information du pod à partir des commandes données en paramètre.
	 * @param angleCmd L'ajout à l'angle.
	 * @param thrustCmd Le nombre de poussé effectuée.
	 */
	public void updateFromCommand(float angleCmd, int thrustCmd) {
		if (isImobilized) {
			imobilizedCpt++;
			// Le joueur pourra bouger au prochain tick serveur
			if (imobilizedCpt % Data.STUN_TIME == 0) {
				isImobilized = false;
				imobilizedCpt = 0;
			}
			System.out.println("Imobilisé");
				
		}
		else
			pod.updateFromCommand(angleCmd, thrustCmd);
	}
	
	/**
	 * Met à jour la position du joueur à partir de son vecteur et de son angle.
	 */
	public void updatePosition() {
		pod.updatePosition();
	}
	
	/**
	 * Ajoute une bombe au stock de bombes du joueur.
	 */
	public void addBomb() {
		this.nbSpiritBombs++;
	}
	
	/**
	 * Enlève une bombe au stock de bombes du joueur.
	 */
	public boolean removeBomb() {
		if(nbSpiritBombs == 0) {
			return false;
		}else {
			this.nbSpiritBombs--;
			return true;
		}
	}
	
	/**
	 * @return Le nombre de bombe que possede le joueur.
	 */
	public int nbBombes() {
		return nbSpiritBombs;
	}
	
	/**
	 * Immobilise un joueur.
	 */
	public void imobilize() {
		pod.imobilize();
		isImobilized = true;
		imobilizedCpt = 0;
	}
}
