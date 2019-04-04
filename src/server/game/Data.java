package game;

import java.io.FileReader;
import java.io.IOException;
import java.util.Random;

import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;
/**
 * Classe contenant les constantes du jeu.
 * Les constantes sont lues à partir d'un fichier json.
 *
 */
public abstract class Data {
	public static int 	ARENA_H 		 = -1;
	public static int 	ARENA_L 		 = -1;
	public static long	SERVER_TICKRATE  = -1;
	public static long	WAITING_TIME	 = -1;
	public static int	THRUST			 = -1;
	public static int 	WIN_CAP			 = -1;
	public static int	POD_SIDE		 = -1;
	public static int 	BALL_SIDE		 = -1;
	public static int	ASTEROID_SIDE	 = -1;
	public static int	NB_OBSTACLE		 = -1;
	public static int 	NB_SPIRIT_BOMBS  = -1;
	public static int 	SPIRIT_BOMB_SIDE = -1;
	public static int 	STUN_TIME		 = -1;
	
	private static Random rand = new Random();
	/**
	 * Initialise constantes du jeu.
	 */
	public static void initializeData() {
		JSONParser parser = new JSONParser();

        try {

            Object obj = parser.parse(new FileReader("src/data.json"));
            JSONObject jsonObject = (JSONObject) obj;
            
            ARENA_H = ((Long) jsonObject.get("arena_h")).intValue();
            ARENA_L = ((Long) jsonObject.get("arena_l")).intValue();
            SERVER_TICKRATE = (Long) jsonObject.get("server_tickrate");
            WAITING_TIME = (Long) jsonObject.get("waiting_time");
            THRUST = ((Long) jsonObject.get("thrust_it")).intValue();
            WIN_CAP = ((Long) jsonObject.get("win_cap")).intValue(); 
            POD_SIDE = ((Long) jsonObject.get("pod_side")).intValue();
            BALL_SIDE = ((Long) jsonObject.get("ball_side")).intValue();
            ASTEROID_SIDE = ((Long) jsonObject.get("asteroid_side")).intValue();
            NB_OBSTACLE = ((Long) jsonObject.get("nb_obstacle")).intValue();
            NB_SPIRIT_BOMBS = ((Long) jsonObject.get("nb_spirit_bombs")).intValue();
            SPIRIT_BOMB_SIDE = ((Long) jsonObject.get("spirit_bomb_side")).intValue();
            STUN_TIME = ((Long) jsonObject.get("stun_time")).intValue();
        }catch (IOException | ParseException e) {
            e.printStackTrace();
        }
	}
	
	/**
	 * Génére un entier aléaoire compris dans les limites de la longueur de l'arêne.
	 * @return Un entier aléatoire.
	 */
	public static float generateRandomX() {
		return -Data.ARENA_L + rand.nextFloat() * (Data.ARENA_L - -Data.ARENA_L);
	}
	
	/**
	 * Génére un entier aléaoire compris dans les limites de la hauteur de l'arène.
	 * @return Un entier aléatoire.
	 */
	public static float generateRandomY() {
		return -Data.ARENA_H + rand.nextFloat() * (Data.ARENA_H - -Data.ARENA_H);
	}
}
