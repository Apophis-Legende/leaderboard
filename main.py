import discord
from discord.ext import commands
from flask import Flask, render_template, jsonify, request
import threading
import os
import json
import requests
import asyncio
from functools import wraps

# --- Configuration ---
SECRET_KEY = "votre_cle_secrete"
file_lock = threading.Lock()  # Verrou global pour l'accès aux fichiers JSON
giveaway_queue = asyncio.Queue()  # File d'attente pour les messages Discord

# Mapping des noms de serveurs aux fichiers JSON
server_file_mapping = {
    "Tiliwan1": "T1.json",
    "Tiliwan2": "T2.json",
    "Oshimo": "O1.json",
    "Herdegrize": "H1.json",
    "Euro": "E1.json"
}

# --- Utilitaires ---
def load_json(filename, default_data=None):
    """Charge un fichier JSON ou retourne les données par défaut si le fichier n'existe pas."""
    with file_lock:
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                print(f"⚠️ Fichier JSON corrompu : {filename}. Réinitialisation.")
                save_json(filename, default_data or {})
                return default_data or {}
        return default_data or {}

def save_json(filename, data):
    """Sauvegarde des données dans un fichier JSON."""
    with file_lock:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"✅ Fichier sauvegardé : {filename}")

# --- Flask Configuration ---
app = Flask(__name__)

@app.route('/')
def index():
    """Affiche la page principale."""
    return render_template('index.html')

@app.route('/api/leaderboard', methods=["GET"])
def get_leaderboard():
    """Retourne les données du leaderboard sous forme JSON."""
    server = request.args.get('server', 'Tiliwan1')  # Nom du serveur par défaut
    server_filename = server_file_mapping.get(server)  # Obtenir le nom du fichier correspondant

    if not server_filename:
        return jsonify({"error": f"Serveur inconnu : {server}"}), 404

    try:
        data = load_json(server_filename, default_data={})
        if not data:
            raise ValueError(f"Les données du fichier '{server_filename}' sont vides ou mal formatées.")
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"Une erreur est survenue : {e}"}), 500

# --- Discord Bot Configuration ---
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def send_data_to_flask(data):
    """Envoie des données à l'application Flask via l'API."""
    flask_url = "https://asdetrefle.replit.app/update_data"
    try:
        data["secret"] = SECRET_KEY
        response = requests.post(flask_url, json=data)
        if response.status_code == 200:
            print("✅ Données envoyées avec succès à Flask :", response.json())
        else:
            print(f"❌ Erreur lors de l'envoi des données : {response.status_code}, {response.text}")
    except Exception as e:
        print(f"❌ Une erreur s'est produite lors de l'envoi : {e}")

async def process_and_save_data(new_data):
    """Traite et sauvegarde les données reçues, puis les envoie à Flask."""
    try:
        existing_data = load_json("data.json", default_data={})
        existing_data.update(new_data)
        save_json("data.json", existing_data)
        await send_data_to_flask(existing_data)
    except Exception as e:
        print(f"❌ Une erreur s'est produite lors du traitement des données : {e}")

async def process_queue():
    """Traite les messages dans la file d'attente de manière séquentielle."""
    while True:
        new_data = await giveaway_queue.get()
        try:
            await process_and_save_data(new_data)
        except Exception as e:
            print(f"❌ Erreur lors du traitement des données de la file : {e}")
        finally:
            giveaway_queue.task_done()

@bot.tree.command(name="update_page", description="Met à jour les données du serveur.")
async def update_page(interaction: discord.Interaction):
    """Commande pour mettre à jour les données."""
    await interaction.response.send_message("🔄 Mise à jour des données en cours...")
    await send_data_to_flask(load_json("data.json", default_data={}))
    await interaction.followup.send("✅ Données mises à jour avec succès.")
    
@bot.tree.command(name="process_giveaway", description="Ajoute un giveaway à traiter grâce à l'ID du message.")
async def process_giveaway(interaction: discord.Interaction, message_id: str):
    """Traite un giveaway en utilisant l'ID du message."""
    try:
        channel = interaction.channel
        if not channel:
            await interaction.response.send_message("❌ Cette commande doit être exécutée dans un canal textuel.", ephemeral=True)
            return

        # Récupérer le message à partir de l'ID
        message = await channel.fetch_message(int(message_id))
        if message.author.id != 294882584201003009:  # ID du bot Giveaway
            await interaction.response.send_message("❌ Ce message ne provient pas du bot cible.", ephemeral=True)
            return

        if "won the" in message.content.lower():
            print(f"🎉 Giveaway détecté dans le message : {message.content}")
            await process_and_save_data({"giveaway_content": message.content})
            await interaction.response.send_message(f"✅ Giveaway traité avec succès pour le message ID {message_id}.")
        else:
            await interaction.response.send_message("❌ Ce message ne contient pas de giveaway valide.", ephemeral=True)

    except discord.NotFound:
        await interaction.response.send_message(f"❌ Aucun message trouvé avec l'ID {message_id}.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ Permissions insuffisantes pour récupérer ce message.", ephemeral=True)
    except Exception as e:
        print(f"❌ Erreur lors du traitement du giveaway : {e}")
        await interaction.response.send_message(f"❌ Une erreur est survenue : {e}", ephemeral=True)


@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que : {bot.user}")
    print(f"✅ ID du bot : {bot.user.id}")
    bot.loop.create_task(process_queue())  # Lancer le traitement de la file d'attente

@bot.event
async def on_message(message):
    if message.author.id == 294882584201003009 and "won the" in message.content.lower():
        print("🎉 Un gagnant détecté !")
        await giveaway_queue.put({"message_content": message.content})  # Ajouter à la file

# --- Flask Server ---
def run_flask():
    app.run(host='0.0.0.0', port=3000, debug=False)

# --- Lancer les serveurs ---
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()  # Lancer Flask dans un thread
    bot.run(os.getenv("TOKEN"))  # Lancer le bot Discord
