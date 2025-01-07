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
    server = request.args.get('server', 'T1')  # Valeur par défaut T1
    server_filename = f"{server}.json"  # Exemple : T1.json, T2.json, etc.
    try:
        # Vérifiez si le fichier existe avant de le charger
        if not os.path.exists(server_filename):
            return jsonify({"error": f"Fichier JSON '{server_filename}' introuvable."}), 404

        # Charger les données depuis le fichier JSON du serveur
        data = load_json(server_filename, default_data={})

        if not data:
            return jsonify({"error": f"Le fichier '{server_filename}' est vide ou mal formaté."}), 404

        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Erreur dans /api/leaderboard : {e}")
        return jsonify({"error": f"Une erreur est survenue : {e}"}), 500

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
    print(f"🌐 Téléchargement du JSON depuis : {url}")
    api_url = url.replace("https://giveawaybot.party/summary#", "https://summary-api.giveawaybot.party/?")

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        raw_data = response.json()

        print(f"✅ JSON brut récupéré avec succès : {raw_data}")

        # Appeler le traitement des données
        processed_data = process_giveaway_data(raw_data)

        # Envoyer les données traitées à Flask
        await send_data_to_flask(processed_data)

        await channel.send(f"🎉 Données du giveaway traitées et envoyées à Flask avec succès !")
    except Exception as e:
        print(f"❌ Erreur lors du traitement : {e}")
        await channel.send("⚠️ Erreur lors du traitement des données JSON.")


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

async def retrieve_previous_message_with_summary(channel):
    async for msg in channel.history(limit=50):
        if hasattr(msg, "components") and msg.components:
            for component in msg.components:
                for button in component.children:
                    if isinstance(button.label, str) and "summary" in button.label.lower():
                        await download_json_from_summary(button.url, channel)
                        return

# Lancer le bot Discord
def run_bot():
    bot.run(os.getenv("TOKEN"))

# Exécuter Flask et Discord en parallèle
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()  # Lancer Flask dans un thread
    run_bot()  # Lancer le bot Discord
