package main;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;

import allThreads.SchedulerParty;
import allThreads.ThreadPlayer;

/**
 * Le serveur de notre application.
 *
 */
public class Server {

	/** Socket serveur pour la connexion.*/
	private ServerSocket server;
	
	/** Thread gérant l'ordonnanceur.*/
	private Thread threadSchedulerParty;
	
	/** Runnable de l'ordonnanceur.*/
	private SchedulerParty schedulerParty;
			
	public Server(int port) {

		try {
			server = new ServerSocket(port);
			System.out.println("[SERVER]: Started");

			// Le serveur est actif, on lance l'ordonnanceur
			this.schedulerParty = new SchedulerParty();
			this.threadSchedulerParty = new Thread(schedulerParty);
			this.threadSchedulerParty.start();
		
			// Boucle d'attente du serveur
			while (true) {
				System.out.println("[SERVER]: Waiting for new connections...");
				Socket socketClient = server.accept();
				System.out.println("[SERVER]: Connection received");

				// Creation d'un thread qui va gérer la partie d'un joueur
				Thread playeur = new Thread(new ThreadPlayer(schedulerParty, socketClient));

				// Puis on le lance
				playeur.start();
			}

		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			try {
				server.close();
				System.out.println("[SERVER] End of server");
			} catch (IOException e) {
				e.printStackTrace();
			}
		}

	}
}
