package allThreads;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.Socket;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Contenu du travail à exécuter par un thread gérant un joueur. 
 *
 */
public class ThreadPlayer implements Runnable {
	
	/** La socket du thread pour communiquer avec son client. */
	private Socket socketClient;
	
	/** Permet d'écrire un message dans la socket cliente.*/
	private BufferedWriter bw;
	
	/** Permet de lire un message dans la socket cliente.*/
	private BufferedReader br;
	
	/** Le compteur statique du nombre de ThreadPlayer.*/
	private static int count = 1;
	
	/** L'id du thread.*/
	private int idThread;
	
	/** Le pseudo de l'utilisateur dont s'occupe le thread.*/
	private String user;
	
	/** L'ordonnanceur associé au thread.*/
	private SchedulerParty schedulerParty;

	/**
	 * Constructeur
	 * @param scheduParty L'ordonnanceur auquel est lié le thread.
	 * @param socket : La socket du client.
	 */
	public ThreadPlayer(SchedulerParty scheduParty, Socket socket) {

		this.idThread = count;
		this.socketClient = socket;
		this.schedulerParty = scheduParty;
		count++;

		try {
			this.socketClient.setSoTimeout(500);
			br = new BufferedReader(new InputStreamReader(socketClient.getInputStream()));
			bw = new BufferedWriter(new OutputStreamWriter(socketClient.getOutputStream()));
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	/**
	 * Lance le déroulement d'une partie.
	 * 
	 * @return Un booléen indiquant si le thread doit continuer à vivre ou non.
	 */
	private boolean beginParty() {
		// On doit vérifier si on a recu un message DENIED/ pendant l'attente
		try {
			String received = br.readLine();

			// Le joueur a fermé la socket, on le supprime de la liste des joueurs
			if (received == null) {
				endParty();
				return false;
			}
			String command = received.split("/")[0];
			if (command.equals("EXIT")) {
				endParty();
				return false;
			}
		} catch (java.net.SocketTimeoutException timout) {

		}
		catch (IOException e2) {
			e2.printStackTrace();
			return false;
		}
		boolean mustDie = false;
		System.out.println("[THREAD PLAYEUR " + idThread + "]: Party begins !");

		while ((!mustDie) && (schedulerParty.partyHasStart())) {
			try {
				String received = br.readLine();
				// Le joueur a fermé la socket, on le supprime de la liste des joueurs
				if (received == null) {
					endParty();
					mustDie = true;
					break;
				}
				// Il est possible que l'on aie reçu plusieurs messages en un seul
				String[] splitted = received.split("/");
				for (int i = 0; i < splitted.length; i++) {
					String command = splitted[i];
					if (!command.equals("NEWCOM") || !command.equals("\nNEWCOM"))
						System.out.println("[THREAD PLAYEUR " + idThread + "]: Received " + received);

					// Fin de la partie pour ce joueur
					if (command.equals("EXIT") || command.equals("\nEXIT")) {
						endParty();
						mustDie = true;
						break;	// On sort du for
						// Réception de nouvelle commande
					} else if (command.equals("NEWCOM") || command.equals("\nNEWCOM")) {
						treatNewCommand(splitted[i + 1]);
						i += 1;
					} else if (command.equals("ENVOI") || command.equals("\nENVOI")) {
						System.out.println("Envoi du message public " + splitted[i + 1]);
						schedulerParty.sendMessageToPublic(user, splitted[i + 1]);
						i += 1;
					} else if (command.equals("PENVOI") || command.equals("\nPENVOI")) {
						System.out.println("Envoi du message privé " + splitted[i + 2] + " à " + splitted[i + 1]);
						schedulerParty.sendPrivateMessage(splitted[1], user, splitted[i + 2]);
						i += 2;
					} else if (command.equals("PUT") || command.equals("\nPUT")) {
						treatCommandPut(splitted[i + 1]);
						i += 2;
					}
				}
			// Timeout !
			} catch (java.net.SocketTimeoutException timout) {

			}
			catch (IOException e2) {
				e2.printStackTrace();
				return false;
			}
		}

		return !mustDie;
	}

	/**
	 * Signal à l'ordonnanceur que le joueur a quitté la partie. 
	 */
	private void endParty() {
		// Signaler à l'ordonanceur que le joueur quitte la partie
		schedulerParty.removePlayer(user);
	}

	/**
	 * Traite les commandes envoyées par le client.
	 * @param commandMsg : Le message contenant les commandes du client.
	 */
	private void treatNewCommand(String commandMsg) {
		String exp = "A(-?[0-9]+\\.[0-9]+)T([0-9])+";
		Matcher m = Pattern.compile(exp).matcher(commandMsg);
		if (m.matches()) {
			float angle = Float.parseFloat(m.group(1));
			int thrust = Integer.parseInt(m.group(2));
			schedulerParty.onNewCommandReceived(user, angle, thrust);
		}
	}

	/**
	 * Traite les dépôts de bombe par le joueur
	 * @param pos : La position de la bombe déposée.
	 */
	private void treatCommandPut(String pos) {
		String exp = "X(-?[0-9]+\\.?[0-9]+E?-?[0-9]*)Y(-?[0-9]+\\.?[0-9]+E?-?[0-9]*)";
		Matcher m = Pattern.compile(exp).matcher(pos);
		if (m.matches()) {
			float x = Float.parseFloat(m.group(1));
			float y = Float.parseFloat(m.group(2));
			schedulerParty.putBomb(user, x, y);
		}
	}
	
	@Override
	public void run() {
		System.out.println("[THREAD PLAYEUR " + idThread + "]: Created");

		String user = manageClientConnection();
		if (user == null) {
			System.out.println("[THREAD PLAYEUR " + idThread + "]: Connection refused");
			return;
		}

		System.out.println(
				"[THREAD PLAYEUR " + idThread + "]: Connection of user : " + user + ", waiting to begin the party");
		boolean mustContinue = true;
		while (mustContinue) {
			// Le joueur est pret, on attend que la partie commence.
			this.waitForSessionToStart();
			// On peut commencer la partie.
			mustContinue = beginParty();
		}
		try {
			bw.close();
			br.close();
			socketClient.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
		System.out.println("[THREAD PLAYEUR " + idThread + "]: End of Thread");
	}

	/**
	 * Attend qu'une session débute (bloquant).
	 */
	private void waitForSessionToStart() {
		try {
			String message;
			// La session a déjà commencé, le joueur peut jouer dés maintenant
			if (schedulerParty.partyHasStart()) {
				message = "WELCOME/play/" + schedulerParty.getScores() + "/" + schedulerParty.getObjectif() + "/" + schedulerParty.getOcoords() + "/" + schedulerParty.getNbBombs() + "/" + schedulerParty.getBcoords() + "/\n";
				bw.write(message);
				bw.flush();
			}
			// Le joueur doit attendre avant de pouvoir jouer
			else {
				message = "WELCOME/wait/" + schedulerParty.getScores() + "/" + schedulerParty.getObjectif() + "/" + schedulerParty.getOcoords() + "/" + schedulerParty.getNbBombs() + "/" + schedulerParty.getBcoords() + "/\n";
				bw.write(message);
				bw.flush();
				System.out.println("[THREAD PLAYEUR " + idThread + "]: Waiting for party to begin...");
				// Attente du début de la partie...
				synchronized (schedulerParty) {
					schedulerParty.wait();
				}
				// Le joueur peut jouer !
				message = "SESSION/" + schedulerParty.getCoords() + "/" + schedulerParty.getObjectif() + "/"
						+ schedulerParty.getOcoords() + "/\n";
				bw.write(message);
				bw.flush();
			}
		} catch (InterruptedException | IOException e) {
			e.printStackTrace();
		}
	}

	/**
	 * Gére la connexion d'un client au serveur.
	 * @return Le pseudo du joueur.
	 */
	private String manageClientConnection() {
		String user = null;
		try {
			System.out.println("[THREAD PLAYEUR " + idThread + "]: Wainting for a connection message...");
			String received = br.readLine();
			if (received == null)
				return null;
			String[] splitted = received.split("/");
			System.out.println("[THREAD PLAYEUR " + idThread + "]: Received " + received);
			user = splitted[1];
			if (schedulerParty.playerNameAlreadyExist(user)) {
				bw.write("DENIED/\n");
				bw.flush();
				return null;
			} else {
				this.user = user;
				// Enregistrer le nouveau joueur auprès de l'ordonnanceur
				schedulerParty.addNewPlayer(user, socketClient);
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
		return user;
	}
}
