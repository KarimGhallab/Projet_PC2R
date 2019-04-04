package game.game_objects;

import game.Data;
import game.Player;
import game.interfaces.IGameObject;

public class SpiritBomb extends Obstacle implements IGameObject{

	private Player player; 
	
	public SpiritBomb(int id, Player player, float x, float y) {
		super(id);
		this.player = player;
		this.x = x;
		this.y = y;
		this.side = Data.SPIRIT_BOMB_SIDE;
	}
	
	public Player getPlayer(){
		return this.player;
	}
	
}
