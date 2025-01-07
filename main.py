import discord
from discord.ext import commands
from flask import Flask, render_template, jsonify, request
import threading
import os
import json
import requests
from logique import process_giveaway_data, load_json
from data_manager import load_json, save_json, extract_user_data
from discord.ui import View, Select
from vip import load_server_json, get_player_vip_status, display_vip_status

# Configuration du bot avec intentions
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Configuration de Flask pour le serveur web
app = Flask(__name__)

@app.route('/update_data', methods=["POST"])
def update_data():
    """Endpoint pour recevoir des mises à jour depuis le bot Discord."""
    try:
        data = request.json  # Récupérer les données envoyées en JSON

        if not data:
            return jsonify({"error": "Aucune donnée reçue ou JSON invalide."}), 400

        if not isinstance(data, dict):
            return jsonify({"error": "Les données doivent être un objet JSON valide."}), 400

        save_json("data.json", data)  # Sauvegarder les données dans data.json
        return jsonify({"message": "Données mises à jour avec succès"}), 200

    except Exception as e:
        app.logger.error(f"Erreur dans /update_data : {e}")
        return jsonify({"error": f"Une erreur est survenue : {e}"}), 500

def load_json(filename, default_data=None):
    """Charge un fichier JSON ou retourne les données par défaut si le fichier n'existe pas."""
    filepath = os.path.join("json_files", filename)  # Dossier dédié pour les fichiers JSON
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    return default_data or {}

@app.route('/')
def index():
    """Route pour afficher la page HTML."""
    return render_template('index.html')

@app.route('/api/leaderboard', methods=["GET"])
def get_leaderboard():
    """API pour fournir les données JSON à la page."""
    # Correspondance entre les noms des serveurs et les fichiers JSON
    server_file_mapping = {
        "Tiliwan1": "T1.json",
        "Tiliwan2": "T2.json",
        "Oshimo": "O1.json",
        "Herdegrize": "H1.json",
        "Euro": "E1.json"
    }

    # Récupérer le nom du serveur depuis les paramètres de la requête
    server = request.args.get('server', '')
    if not server:
        return jsonify({"error": "Paramètre 'server' manquant dans la requête."}), 400

    # Vérifiez si le serveur existe dans le mapping
    file_name = server_file_mapping.get(server)
    if not file_name:
        return jsonify({"error": f"Serveur '{server}' non reconnu."}), 404

    print(f"🔍 Requête pour le fichier JSON : {file_name}")

    try:
        # Vérifiez si le fichier existe
        if not os.path.exists(file_name):
            print(f"❌ Fichier introuvable : {file_name}")
            return jsonify({"error": f"Fichier JSON '{file_name}' introuvable."}), 404

        # Charger les données depuis le fichier JSON
        with open(file_name, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not data:
            return jsonify({"error": f"Le fichier '{file_name}' est vide ou mal formaté."}), 404

        return jsonify(data), 200

    except Exception as e:
        print(f"❌ Erreur lors du traitement du fichier {file_name} : {e}")
        return jsonify({"error": f"Une erreur est survenue lors de la lecture du fichier {file_name} : {str(e)}"}), 500

def run_flask():
    # Assurez-vous que Flask écoute sur 0.0.0.0 pour permettre l'accès externe
    app.run(host='0.0.0.0', port=3000, debug=False)

# Charger les données depuis le fichier JSON
data = load_json("data.json", default_data={})

# Extraire les données des utilisateurs
user_data = extract_user_data(data)
for user in user_data:
    print(user)

# ID du bot cible
TARGET_BOT_ID = 294882584201003009  # ID du GiveawayBot
# Mapping entre les serveurs et leurs fichiers JSON

SERVER_FILE_MAPPING = {
    "Tiliwan1": "T1.json",
    "Tiliwan2": "T2.json",
    "Oshimo": "O1.json",
    "Herdegrize": "H1.json",
    "Euro": "E1.json"
}


def load_server_json(server):
    """Charge les données du fichier JSON correspondant au serveur."""
    file_name = SERVER_FILE_MAPPING.get(server)
    if not file_name:
        raise ValueError(f"Serveur '{server}' non reconnu.")

    if not os.path.exists(file_name):
        print(f"❌ Fichier JSON pour le serveur '{server}' introuvable : {file_name}")
        return {}  # Retourne un dictionnaire vide si le fichier n'existe pas

    with open(file_name, "r", encoding="utf-8") as f:
        return json.load(f)  # Charge les données JSON
        
async def send_data_to_flask(data):
    """Envoie des données JSON au serveur Flask."""
    try:
        url = "http://127.0.0.1:3000/update_data"  # Endpoint Flask
        headers = {'Content-Type': 'application/json'}

        # Envoyer une requête POST avec les données
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Lève une exception pour les erreurs HTTP

        print(f"✅ Données envoyées à Flask avec succès : {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de l'envoi des données à Flask : {e}")
        raise

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que : {bot.user}")
    print(f"✅ ID du bot : {bot.user.id}")


async def send_data_to_flask(data):
    """Envoie des données JSON au serveur Flask."""
    try:
        url = "http://127.0.0.1:3000/update_data"  # Endpoint Flask
        headers = {'Content-Type': 'application/json'}

        # Vérifiez que les données sont un dictionnaire
        if not isinstance(data, dict):
            raise ValueError("Les données à envoyer doivent être un dictionnaire JSON.")

        # Envoyer une requête POST avec les données
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Lève une exception pour les erreurs HTTP

        print(f"✅ Données envoyées à Flask avec succès : {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de l'envoi des données à Flask : {e}")
        raise
        
async def download_json_from_summary(url, channel):
    """
    Télécharge les données JSON d'un giveaway, traite les données et les envoie au serveur Flask.
    """
    print(f"🌐 Téléchargement du JSON depuis : {url}")
    api_url = url.replace("https://giveawaybot.party/summary#", "https://summary-api.giveawaybot.party/?")

    try:
        # Télécharger les données brutes depuis l'API
        response = requests.get(api_url)
        response.raise_for_status()
        raw_data = response.json()

        print(f"✅ JSON brut récupéré avec succès : {raw_data}")

        # Vérifiez que les données brutes sont valides
        if not raw_data or not isinstance(raw_data, dict):
            raise ValueError("Les données JSON brutes récupérées ne sont pas valides ou sont vides.")

        # Appeler le traitement des données
        processed_data = process_giveaway_data(raw_data)

        # Vérifiez que les données traitées sont un dictionnaire
        if not processed_data:
            raise ValueError("Les données traitées sont vides ou nulles.")
        if not isinstance(processed_data, dict):
            raise ValueError(f"Les données traitées ne sont pas un dictionnaire. Type actuel : {type(processed_data)}")

        # Envoyer les données traitées au serveur Flask
        print("🚀 Envoi des données au serveur Flask...")
        await send_data_to_flask(processed_data)

        # Confirmer l'envoi réussi au canal Discord
        await channel.send(f"🎉 Données du giveaway traitées et envoyées à Flask avec succès !")

    except requests.exceptions.RequestException as req_err:
        # Gestion des erreurs liées à la requête HTTP
        print(f"❌ Erreur HTTP lors de la récupération des données JSON : {req_err}")
        await channel.send("⚠️ Erreur lors de la récupération des données JSON.")

    except ValueError as val_err:
        # Gestion des erreurs liées au format des données
        print(f"❌ Erreur de format des données : {val_err}")
        await channel.send(f"⚠️ Erreur lors du traitement des données : {val_err}")

    except Exception as e:
        # Gestion générique des erreurs
        print(f"❌ Une erreur inattendue est survenue : {e}")
        await channel.send("⚠️ Une erreur inattendue est survenue lors du traitement des données JSON.")

# Gestion des messages : suivre uniquement ceux du bot cible
@bot.event
async def on_message(message):
    print(f"\n🚨 Nouveau message reçu 🚨")
    print(f"📨 Contenu du message : {message.content}")
    print(f"👤 Auteur : {message.author} (ID : {message.author.id})")

    # Ignorer tous les messages sauf ceux du bot cible
    if message.author.id != TARGET_BOT_ID:
        print("🔄 Ignoré : ce message ne provient pas du bot cible.")
        return

    print("🎯 Message suivi : ce message provient du bot cible !")

    # Vérifier si un gagnant a été annoncé
    if "won the" in message.content.lower():
        print("🎉 Un gagnant a été détecté dans le message.")
        await retrieve_previous_message_with_summary(message.channel)

    # Vérifier les VIP pour les utilisateurs après un giveaway
    raw_data = ...  # Récupérez les données JSON du giveaway
    await handle_giveaway(raw_data, message.channel)

async def retrieve_previous_message_with_summary(channel):
    """
    Parcourt les 50 derniers messages pour trouver un bouton "Giveaway Summary"
    et télécharge les données associées.
    """
    print("🔍 Recherche des messages récents avec un résumé de giveaway...")
    try:
        # Parcourt les 50 derniers messages dans le canal
        async for msg in channel.history(limit=50):
            if hasattr(msg, "components") and msg.components:
                print(f"📩 Analyse des composants du message ID {msg.id}")
                for component in msg.components:
                    for button in component.children:
                        # Vérifiez si le bouton a une étiquette valide
                        if button.label and button.label.lower() == "giveaway summary":
                            if button.url:
                                print(f"🌐 Bouton 'Giveaway Summary' trouvé : {button.url}")
                                await download_json_from_summary(button.url, channel)
                                return
                            else:
                                print("⚠️ Bouton 'Giveaway Summary' trouvé, mais l'URL est absente.")
            else:
                print(f"❌ Le message ID {msg.id} ne contient pas de composants.")

        # Si aucun bouton "Giveaway Summary" n'est trouvé
        print("❌ Aucun bouton 'Giveaway Summary' trouvé dans les 50 derniers messages.")
        await channel.send("⚠️ Aucun résumé de giveaway trouvé dans les messages récents.")

    except Exception as e:
        # Gestion générique des erreurs
        print(f"❌ Une erreur inattendue est survenue dans retrieve_previous_message_with_summary : {e}")
        await channel.send(f"⚠️ Une erreur inattendue est survenue lors de la recherche du résumé : {e}")

async def process_giveaway_event(player_id, server, bets_to_add):
    """
    Met à jour les mises VIP d'un joueur après un giveaway.
    """
    # Mise à jour du statut VIP
    update_player_vip(player_id, server, bets_to_add)

    # Affichage dans les logs
    display_vip_status(player_id, server)

async def display_server_data(server, channel):
    """
    Lit les données d'un serveur depuis son fichier JSON et les affiche dans Discord.
    """
    try:
        # Lire les données du serveur
        data = load_server_json(server)

        if not data:
            await channel.send(f"⚠️ Aucune donnée trouvée pour le serveur {server}.")
            return

        # Formatage des données pour Discord
        formatted_data = json.dumps(data, indent=4, ensure_ascii=False)
        await channel.send(f"📊 Données du serveur **{server}** :\n```json\n{formatted_data}\n```")

    except ValueError as e:
        await channel.send(f"❌ Erreur : {e}")
    except Exception as e:
        await channel.send(f"❌ Une erreur inattendue est survenue : {e}")

async def handle_giveaway(raw_data, channel):
    """
    Exemple : Traite les données d'un giveaway et vérifie les statuts VIP.
    """
    try:
        # Extraction des informations du giveaway
        prize = raw_data["giveaway"]["prize"]
        server = prize.split(" ")[0]  # Exemple : "T1"
        entries = raw_data["entries"]  # Liste des participants

        for entry in entries:
            player_id = entry["id"]  # ID du joueur
            # Vérification et notification du VIP
            await check_and_notify_vip(player_id, server, channel)

    except Exception as e:
        print(f"❌ Erreur dans handle_giveaway : {e}")
        await channel.send("⚠️ Une erreur est survenue lors du traitement des données du giveaway.")


# Lancer le bot Discord
def run_bot():
    bot.run(os.getenv("TOKEN"))

# Exécuter Flask et Discord en parallèle
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()  # Lancer Flask dans un thread
    run_bot()  # Lancer le bot Discord
