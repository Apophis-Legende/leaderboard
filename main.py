import discord
from discord.ext import commands
from flask import Flask, render_template, jsonify, request
import threading
import os
import json
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

def load_json(filename, default_data=None):
    """Charge un fichier JSON ou retourne les données par défaut si le fichier n'existe pas."""
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
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
    server_filename = f"{server}.json"  # Par exemple, T1.json, T2.json, O1.json, etc.
    try:
        # Charger les données depuis le fichier JSON du serveur
        data = load_json(server_filename, default_data={})
        if not data:
            raise ValueError(f"Les données du fichier '{server_filename}' sont vides ou mal formatées.")
        return jsonify(data)  # Renvoyer les données JSON
    except Exception as e:
        return jsonify({"error": f"Une erreur est survenue : {e}"}), 500

def run_flask():
    # Assurez-vous que Flask écoute sur 0.0.0.0 pour permettre l'accès externe
    app.run(host='0.0.0.0', port=3000)


# Charger les données depuis le fichier JSON
data = load_json("data.json", default_data={})

# Extraire les données des utilisateurs
user_data = extract_user_data(data)
for user in user_data:
    print(user)

# ID du bot cible
TARGET_BOT_ID = 294882584201003009  # ID du GiveawayBot

class ServerSelect(View):
    def __init__(self):
        super().__init__()

        # Liste des options de serveur correspondant aux fichiers JSON
        self.add_item(Select(
            placeholder="Choisissez un serveur",
            options=[
                discord.SelectOption(label="Tiliwan1", value="T1"),
                discord.SelectOption(label="Tiliwan2", value="T2"),
                discord.SelectOption(label="Oshimo", value="O1"),
                discord.SelectOption(label="Herdegrize", value="H1"),
                discord.SelectOption(label="Euro", value="E1")
            ]
        ))

    async def interaction_check(self, interaction: discord.Interaction):
        server_value = interaction.data['values'][0]  # Récupérer la valeur (le fichier JSON associé)
        await self.update_page(interaction, server_value)

    async def update_page(self, interaction, server_value):
        """Commande pour traiter et mettre à jour les données du serveur sélectionné."""
        try:
            # Le fichier JSON à charger correspond à la valeur sélectionnée par l'utilisateur
            server_filename = f"{server_value}.json"  # Ex: T1.json, T2.json, etc.

            # Charger les données depuis le fichier JSON du serveur
            raw_data = load_json(server_filename, default_data={})

            if not raw_data:
                raise ValueError(f"Les données du fichier '{server_filename}' sont vides ou mal formatées.")

            # Envoi de la confirmation
            await interaction.response.send_message(f"🔄 Données du serveur {server_value} mises à jour avec succès ! Rechargez la page pour voir les modifications.", ephemeral=True)

        except ValueError as e:
            # Cas spécifique pour les erreurs de format de données
            await interaction.response.send_message(f"❌ Erreur de format des données : {str(e)}", ephemeral=True)
        except Exception as e:
            # Attraper toutes les autres erreurs et les afficher
            await interaction.response.send_message(f"❌ Une erreur est survenue : {str(e)}", ephemeral=True)

@bot.tree.command(name="update_page", description="Met à jour les données et la page HTML.")
async def update_page(interaction: discord.Interaction):
    """Commande pour traiter et mettre à jour les données du serveur sélectionné."""
    view = ServerSelect()  # Crée l'interface de sélection
    await interaction.response.send_message("Choisissez un serveur pour mettre à jour les données : ", view=view)

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que : {bot.user}")
    print(f"✅ ID du bot : {bot.user.id}")

async def download_json_from_summary(url, channel):
    print(f"🌐 Téléchargement du JSON depuis : {url}")
    api_url = url.replace("https://giveawaybot.party/summary#", "https://summary-api.giveawaybot.party/?")

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        raw_data = response.json()

        print(f"✅ JSON brut récupéré avec succès : {raw_data}")

        # Appeler le traitement des données
        process_giveaway_data(raw_data)

        await channel.send(f"🎉 Données du giveaway traitées et sauvegardées avec succès !")
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
                    if button.label.lower() == "giveaway summary":
                        await download_json_from_summary(button.url, channel)
                        return

# Lancer le bot Discord
def run_bot():
    bot.run(os.getenv("DISCORD_TOKEN"))

# Exécuter Flask et Discord en parallèle
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()  # Lancer Flask dans un thread
    run_bot()  # Lancer le bot Discord
