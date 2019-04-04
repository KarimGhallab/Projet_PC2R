package main;

import game.Data;

/**
 * Classe main.
 *
 */
public class MainServer {

	public static void main(String[] args) {
		Data.initializeData();
		new Server(1234);
	}

}
