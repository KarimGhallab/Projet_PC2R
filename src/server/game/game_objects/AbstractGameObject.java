package game.game_objects;

import game.Data;
import game.interfaces.IGameObject;

/**
 * Abstraction d'un objet de jeu.
 *
 */
public abstract class AbstractGameObject implements IGameObject {
	protected float x;
	protected float y;
	protected int side;
	
	/**
	 * Constructeur d'un objet de jeu.
	 * Génére des coordonnées aléatoire.
	 */
	public AbstractGameObject() {
		x = Data.generateRandomX();
		y = Data.generateRandomY();
	}
	
	@Override
	public float getX() {
		return x;
	}

	@Override
	public void setX(float newX) {
		x = newX;
	}

	@Override
	public float getY() {
		return y;
	}

	@Override
	public void setY(float newY) {
		y = newY;
	}

	@Override
	public int getSide() {
		return side;
	}
	
	@Override
	public boolean checkHit(IGameObject go) {
		float distance = (((go.getX() - x) * (go.getX() - x)) + ((go.getY() - y) * (go.getY() - y)));
		
		return distance <= ((side/2 + go.getSide()/2) * (side/2 + go.getSide()/2));
	}
}