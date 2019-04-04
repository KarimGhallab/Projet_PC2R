package allThreads;

import java.io.BufferedWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.net.Socket;
import java.util.Map;

import game.Data;
import game.Player;
import game.Session;
import game.game_objects.Obstacle;
import game.game_objects.Pod;
import game.game_objects.SpiritBomb;
import game.interfaces.IGameObject;

/**
 * Ordonnanceur par lequel n'importe quelle thread doit passer pour modifier la
 * session.
 */
public class SchedulerParty implements Runnable {

	/** La session de la partie. */
	private Session session;

	/** Le thread envoyant régulièrement les positions aux clients. */
	private Thread tickRateThread;

	/**
	 * Constructeur de l'ordonnanceur. Construit une nouvelle session.
	 */
	public SchedulerParty() {
		this.session = new Session();
	}

	/**
	 * Récupère les scores de la session.
	 * 
	 * @return Les scores de la session sous la forme imposée par le protocole de
	 *         communication.
	 */
	public synchronized String getScores() {
		return session.getScores();
	}

	/**
	 * Récupère l'objectif de la session.
	 * 
	 * @return L'objectif de la session sous la forme imposée par le protocole de
	 *         communication.
	 */
	public synchronized String getObjectif() {
		return session.getObjectif();
	}

	/**
	 * Récupère les coordonnées des joueurs de la session.
	 * 
	 * @return L'objectif de la session sous la forme imposée par le protocole de
	 *         communication.
	 */
	public synchronized String getCoords() {
		return session.getCoords();
	}

	/**
	 * Récupère les vecteurs et les angles des joueurs de la session.
	 * 
	 * @return Récupère les vecteurs et les angles des joueurs de la session sous la
	 *         forme imposée par le protocole de communication.
	 */
	public synchronized String getVcoords() {
		return session.getVcoords();
	}

	/**
	 * Récupère les obstacles de la session.
	 * 
	 * @return Récupère les obstacles de la session sous la forme imposée par le
	 *         protocole de communication.
	 */
	public synchronized String getOcoords() {
		return session.getOcoords();
	}

	/**
	 * Récupère les bombes de la session.
	 * 
	 * @return Récupère les bombes de la session sous la forme imposée par le
	 *         protocole de communication.
	 */
	public synchronized String getBcoords() {
		return session.getBcoords();
	}

	/**
	 * Récupère les bombes disponibles de chaque joueur.
	 * 
	 * @return Récupère les bombes disponibles de chaque joueur sous la forme
	 *         imposée par le protocole de communication.
	 */
	public synchronized String getNbBombs() {
		return session.getNbBombs();
	}

	/**
	 * Envoie un message de mises à jour à chaque client (TICK/coords/)
	 */
	public synchronized void updateEveryClient() {
		try {
			Player current;
			BufferedWriter bw;
			String message;
			String vcoords = getVcoords();
			Map<String, Player> players = session.getPlayers();
			for (String playerName : players.keySet()) {
				current = players.get(playerName);

				if (current.getSocket().isClosed())
					continue;

				message = "TICK/" + vcoords + "/\n";
				bw = new BufferedWriter(new OutputStreamWriter(current.getSocket().getOutputStream()));
				bw.write(message);
				bw.flush();
			}

		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	/**
	 * Applique les nouvelles commandes envoyées par le client et vérifie les
	 * collisions.
	 * Vérifie aussi si un joueur a touché un objectif.
	 * Envoie un message NEWOBJ ou WINNER en conséquence.
	 * 
	 * @param playerName Le nom du joueur ayant envoyé les commandes.
	 * @param angle      L'ajout des angles.
	 * @param thrust     Le nombre d'impulsion effectuée.
	 */
	public void onNewCommandReceived(String playerName, float angle, int thrust) {
		synchronized (this) {
			boolean hasAlreadyChanged = false;
			Player p = session.getPlayer(playerName);
			checkPosition(p, angle, thrust);

			Map<String, Player> players = session.getPlayers();

			// Verifie s'il y a une collision entre le joueur courant et un autre joueur
			Pod playerPod = p.getPod();
			Pod otherPod = session.checkHitPlayers(playerPod);
			// Collision !
			if (otherPod != null) {
				System.out.println("Player collision");
				hasAlreadyChanged = true;

				collisionsSameMass(playerPod, otherPod);

				// Tant que les deux pods se touchent, on éloigne le joueur courant en mettant à
				// jour sa position
				while (playerPod.checkHit(otherPod))
					p.updatePosition();
			}

			Obstacle o = session.checkHitObstacle(p.getPod());
			if ((!hasAlreadyChanged) && (o != null)) {
				System.out.println("Obstacle !");
				collisionsInfiniteMass(p.getPod(), o);
			}

			SpiritBomb sb = (SpiritBomb) session.checkHitBombs(p.getPod());
			if ((!hasAlreadyChanged) && (sb != null) && sb.getPlayer() != p) {
				System.out.println("Bombe !");
				p.imobilize();
				hitBomb(playerName, sb.getId());
			}

			try {
				// Verifie si le joueur courant a touche l'objectif et s'il a gagne
				if (session.checkHitObjectif(p.getPod())) {

					System.out.println("Collision objectif");

					// L'objectif est atteint, on en genere un autre
					String newObjectifCoord = session.newObjectif();

					// On modifie le score du joueur qui a touche l'objectif
					session.increaseScore(playerName);

					// On recupere le nouveau score a communiquer au joueur
					String newScores = session.getScores();
					String message;

					if (session.win(playerName)) {
						message = "WINNER/" + newScores + "/\n";
						session.finishSession();
					} else
						message = "NEWOBJ/" + newObjectifCoord + "/" + newScores + "/\n";

					// On envoie le message à tous les joueurs
					for (String player : players.keySet()) {
						Socket sock = players.get(player).getSocket();
						if (sock.isClosed())
							continue;
						BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(sock.getOutputStream()));
						bw.write(message);
						bw.flush();
					}
				}
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
		// On doit executer se bloc en dehors du synchronized car on va attendre la fin
		// d'un thread
		if (session.win(playerName))
			finishCurrentSession();
	}

	/**
	 * Calcule les coordonnées clientes en comparant les coordonnées calculées sur le
	 * serveur et celle envoyées par le client.
	 * Affecte la nouvelle position du joueur en fonction de cette comparaison.
	 * 
	 * @param player    Le joueur dont on souhaite calculer les nouvelles
	 *                  coordonnées.
	 * @param angleCmd  La commande d'angle
	 * @param thrustCmd La commande d'impulsion.
	 */
	private void checkPosition(Player player, float angleCmd, int thrustCmd) {
		player.updateFromCommand(angleCmd, thrustCmd);
	}

	/**
	 * Attendra la fin du thread tickRateThread avant de mettre en place une
	 * nouvelle session.
	 */
	private void finishCurrentSession() {
		try {
			System.out.println("[SCHEDULER PARTY]: Interrupting tickRateThread...");
			tickRateThread.interrupt();
			tickRateThread.join();
			System.out.println("[SCHEDULER PARTY]: tickRateThread interrupted");
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		// On doit de nouveau être en session critique
		synchronized (this) {
			session.resetSession();
			new Thread(this).start();
		}
	}

	/**
	 * Gère les mises à jour des vecteurs et des positions dans le cadre d'une
	 * collisions entre deux joueurs de même masse.
	 * 
	 * @param pod1 Le joueur1.
	 * @param pod2 Le joueur2.
	 */
	private void collisionsSameMass(Pod pod1, Pod pod2) {
		float x1 = pod1.getX();
		float x2 = pod2.getX();
		float y1 = pod1.getY();
		float y2 = pod2.getY();
		float r1 = pod1.getSide() / 2;
		float r2 = pod2.getSide() / 2;

		float nx = (x2 - x1) / (r1 + r2);
		float ny = (y2 - y1) / (r1 + r2);
		float gx = -ny;
		float gy = nx;
		float v1n = nx * pod1.getVectorX() + ny * pod1.getVectorY();
		float v1g = gx * pod1.getVectorX() + gy * pod1.getVectorY();
		float v2n = nx * pod2.getVectorX() + ny * pod2.getVectorY();
		float v2g = gx * pod2.getVectorX() + gy * pod2.getVectorY();
		float d = (float) Math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2));

		pod1.setVectorX(nx * v2n + gx * v1g);
		pod1.setVectorY(ny * v2n + gy * v1g);

		pod2.setVectorX(nx * v1n + gx * v2g);
		pod2.setVectorY(ny * v1n + gy * v2g);

		pod2.setX(x1 + (r1 + r2) * (x2 - x1) / d);
		pod2.setY(y1 + (r1 + r2) * (y2 - y1) / d);
	}

	/**
	 * Gère les mises à jour de vecteur et de position dans le cadre d'une collision
	 * entre un joueur et un objet de masse infinie.
	 * 
	 * @param pod    Le joueur.
	 * @param object L'objet de masse infinie.
	 */
	private void collisionsInfiniteMass(Pod pod, IGameObject object) {
		float podX = pod.getX();
		float objectX = object.getX();
		float podY = pod.getY();
		float objectY = object.getY();
		float podR = pod.getSide() / 2;
		float objectR = object.getSide() / 2;

		float nx = (podX - objectX) / (objectR + podR);
		float ny = (podY - objectY) / (objectR + podR);
		float pPod = pod.getVectorX() * nx + pod.getVectorY() * ny;
		float d = (float) Math.sqrt((objectX - podX) * (objectX - podX) + (objectY - podY) * (objectY - podY));

		pod.setVectorX(pod.getVectorX() - 2 * pPod * nx);
		pod.setVectorY(pod.getVectorY() - 2 * pPod * ny);

		pod.setX(objectX + (objectR + podR) * (podX - objectX) / d);
		pod.setY(objectY + (objectR + podR) * (podY - objectY) / d);
	}

	/**
	 * Envoi un message sur le chat public de tous les joueurs (sauf le client
	 * source).
	 * 
	 * @param src     La source du message.
	 * @param message Le message a envoyé.
	 */
	public synchronized void sendMessageToPublic(String src, String message) {
		BufferedWriter bw;
		Map<String, Player> players = session.getPlayers();
		Socket sock;
		String toSend = "RECEPTION/" + message + "/\n";
		try {
			for (String playerName : players.keySet()) {
				if (playerName.equals(src))
					continue;
				sock = players.get(playerName).getSocket();

				if (sock.isClosed())
					continue;

				bw = new BufferedWriter(new OutputStreamWriter(sock.getOutputStream()));
				bw.write(toSend);
				bw.flush();
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	/**
	 * Envoie un message privé à la destination.
	 * 
	 * @param dst     Le destinataire du message.
	 * @param src     La source du message.
	 * @param message Le message à envoyer.
	 */
	public synchronized void sendPrivateMessage(String dst, String src, String message) {
		String toSend = "PRECEPTION/" + message + "/" + src + "/\n";
		Socket sock = session.getPlayer(dst).getSocket();
		if (sock.isClosed())
			return;

		BufferedWriter bw;
		try {
			bw = new BufferedWriter(new OutputStreamWriter(sock.getOutputStream()));
			bw.write(toSend);
			bw.flush();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	/**
	 * Cette fonction permet a l'ordonnanceur, de mettre en place le mécanisme
	 * d'attente au debut d'une partie. Elle notifiera tous les joueurs lors du
	 * debut de la partie.
	 */
	public synchronized void waitBeginParty() {
		System.out.println("[SCHEDULER PARTY]: Waiting for party to begin...");
		try {
			// Au lancement du thread, il attend un certain nombre de secondes
			// avant de lancer le début de la partie
			// Wait est utilisé car contrairement à Thread.sleep(), il lachera le verrou
			// et evitera de bloquer d'autres threads
			this.wait(Data.WAITING_TIME);

			// La partie peut commencer, on previent tout les participants.
			System.out.println("[SCHEDULER PARTY]: Notify all players");
			this.notifyAll();

			session.startSession();
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
	}

	/**
	 * Permet au thread joueur, de s'ajouter à la liste des joueurs de la partie et
	 * de notifier les autres joueurs de sa présence.
	 * 
	 * @param name         : Le nom du nouveau joueur.
	 * @param socketClient : La socket de communication du nouveau joueur.
	 */
	public synchronized void addNewPlayer(String name, Socket socketClient) {
		synchronized (session) {
			BufferedWriter bw;
			Map<String, Player> players = session.getPlayers();
			try {
				String message = "NEWPLAYER/" + name + "/\n";
				// Signalement de la connexion de ’name’ aux autres joueur
				for (String player : players.keySet()) {
					Socket sock = players.get(player).getSocket();
					if (sock.isClosed())
						continue;
					System.out.println("[SCHEDULER PARTY]: Sending \"" + message + "\" to " + player);

					bw = new BufferedWriter(new OutputStreamWriter(sock.getOutputStream()));
					bw.write(message);
					bw.flush();
				}
			} catch (IOException e) {
				e.printStackTrace();
			}

			// Ajout du nouveau jouer à la session
			session.addPlayer(name, session.generateNewPlayer(socketClient));

			// Le premier joueur est arrive, il reveil l'ordonnanceur
			if (session.numberOfPlayers() == 1)
				session.notify();
		}
	}

	/**
	 * Permet au thread joueur de s'enlever de la partie et de notifier les autres
	 * joueurs.
	 * 
	 * @param name : Le nom du joueur quittant la partie.
	 */
	public void removePlayer(String name) {
		synchronized (this) {
			System.out.print("[SCHEDULER PARTY]: Removing " + name + "...");
			session.removePlayer(name);

			BufferedWriter bw;
			Map<String, Player> players = session.getPlayers();
			try {
				// Signalement de la deconnexion de 'name' aux autres joueurs.
				for (String player : players.keySet()) {
					Socket sock = players.get(player).getSocket();
					if (sock.isClosed())
						continue;
					bw = new BufferedWriter(new OutputStreamWriter(sock.getOutputStream()));
					bw.write("PLAYERLEFT/" + name + "/\n");
					bw.flush();
				}
			} catch (IOException e) {
				e.printStackTrace();
			}
			System.out.println("Done");
		} // synchronized

		// Il se peut que tous les joueurs soient parti, dans ce cas là, on créé un
		// nouvel ordonnanceur qui attendra la premier connexion
		if (session.hasNoPlayer())
			finishCurrentSession();
	}

	/**
	 * Permet d'indiquer à tous les joueurs qu'une bombe a ete deposée.
	 * 
	 * @param name : Le nom du joueur qui depose la bombe.
	 */
	public synchronized void putBomb(String name, float x, float y) {
		System.out.println("Put bomb");
		Map<String, Player> players = session.getPlayers();
		Player currentPlayer = players.get(name);

		// Si le joueur possede des spirit bomb en stock
		if (currentPlayer.removeBomb()) {
			BufferedWriter bw;
			session.addBombs(currentPlayer, x, y);

			try {
				String message = "PUT/" + name + "/" + "bomb" + "X" + x + "Y" + y + "/\n";
				// Signalement aux autres joueurs, que ’name’ a pose une spirit bombs.
				for (String player : players.keySet()) {
					if (!player.equals(name)) {
						Socket sock = players.get(player).getSocket();
						if (sock.isClosed())
							continue;
						System.out.println("[SCHEDULER PARTY]: Sending \"" + message + "\" to " + player);

						bw = new BufferedWriter(new OutputStreamWriter(sock.getOutputStream()));
						bw.write(message);
						bw.flush();
					}
				}
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
	}

	/**
	 * Permet d'indiquer à tous les joueurs qu'une bombe a été touchée.
	 * 
	 * @param name : Le nom du joueur qui touche la bombe.
	 */
	public synchronized void hitBomb(String name, int idBomb) {
		// On diminue le score du joueur
		session.decreaseScore(name);

		Map<String, Player> players = session.getPlayers();

		// Si le joueur possede des spirit bombs en stock
		BufferedWriter bw;

		// Elle a ete touchee, donc on enleve la bombe de la liste des bombes presentes
		// en jeu
		Obstacle bomb = session.removeBomb(idBomb);

		if (bomb != null) {
			try {
				String message = "HIT/" + name + "/" + bomb.getObstacleCoord() + "/" + session.getScores() + "/\n";
				// Signalement aux joueurs, que ’name’ a touche une spirit bomb.
				for (String player : players.keySet()) {

					Socket sock = players.get(player).getSocket();

					if (sock.isClosed())
						continue;
					System.out.println("[SCHEDULER PARTY]: Sending \"" + message + "\" to " + player);

					bw = new BufferedWriter(new OutputStreamWriter(sock.getOutputStream()));
					bw.write(message);
					bw.flush();
				}
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
	}

	/**
	 * Indique si un nom de joueur a déjà été pris.
	 * 
	 * @param name : le nom dont on veut verifier l'existance.
	 * @return true si le nom existe déjà, false sinon.
	 */
	public synchronized boolean playerNameAlreadyExist(String name) {
		return session.containsPseudo(name);
	}

	/**
	 * Indique si la partie a commencé.
	 * 
	 * @return true si la partie a commencé, false sinon.
	 */
	public synchronized boolean partyHasStart() {
		return session.sessionHasStart();
	}

	@Override
	public void run() {
		try {
			// Aucun joueur, on attends son arrivée
			if (session.getPlayers().size() == 0) {
				synchronized (session) {
					session.wait();
				}
			}

			// On est debloque c'est qu'il y a un joueur present, on peut lancer le timer du
			// depart.
			waitBeginParty();

			// La session a commencé, on lance un thread qui enverra periodiquement les
			// données aux clients
			tickRateThread = new Thread(new TickRateThread(this));
			tickRateThread.start();
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
	}
}
