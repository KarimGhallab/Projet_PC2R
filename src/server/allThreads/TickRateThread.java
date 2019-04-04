package allThreads;

import game.Data;

/**
 * Contenu à exécuter pour le thread envoyant régulièrement les messages TICK aux clients.
 *
 */
public class TickRateThread implements Runnable {

	/** L'ordonnanceur auquel est lié le thread.*/
	private SchedulerParty schedulerParty;

	/**
	 * Constructeur
	 * @param schedulerParty L'ordonnanceur auquel est lié le thread. 
	 */
	public TickRateThread(SchedulerParty schedulerParty) {
		this.schedulerParty = schedulerParty;
	}

	@Override
	public void run() {
		System.out.println("[TICK RATE THREAD]: Started");
		try {
			while (!Thread.currentThread().isInterrupted()) {
				schedulerParty.updateEveryClient();
				long sleepingTime = 1000 / Data.SERVER_TICKRATE;
				Thread.sleep(sleepingTime);
			}
		} catch (InterruptedException e) {
			System.out.println("[TICK RATE THREAD]: finished");
		}
	}
}
