import logging
import os

# Obtenez le chemin vers le dossier actuel du script
dossier_script = os.path.dirname(os.path.abspath(__file__))

# Construisez le chemin vers bot_logs.log dans src/logs
chemin_fichier_logs = os.path.join(dossier_script, 'logs', 'bot_logs.log')

# Configuration des journaux
logging.basicConfig(filename=chemin_fichier_logs, level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

# ID du canal Discord où vous souhaitez envoyer les logs
log_channel_id = 1178644347038740523

# Fonction pour envoyer un message de log à Discord
async def send_logs_to_channel(bot, log_message):
    log_channel = bot.get_channel(log_channel_id)
    if log_channel:
        await log_channel.send(log_message)

# Fonction pour obtenir le contenu des logs
def get_logs():
    try:
        with open(chemin_fichier_logs, 'r') as file:
            logs_content = file.read()
        return logs_content

    except FileNotFoundError:
        return "Aucun log trouvé."
