import discord
from discord import app_commands
from discord.ext import commands
import requests
import os
import json
from flask import Flask, render_template
import threading
from logique import process_giveaway_data

# Initialiser Flask
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Affiche votre page HTML principale

def run_flask():
    """Démarrer Flask dans un thread séparé."""
    app.run(host='0.0.0.0', port=5000)

# Configuration du bot Discord
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

TARGET_BOT_ID = 294882584201003009  # ID du GiveawayBot

@bot.event
async def on_ready():
    """Événement appelé lorsque le bot est prêt."""
    print(f"✅ Bot connecté en tant que : {bot.user}")
    print(f"✅ ID du bot : {bot.user.id}")
    await bot.tree.sync()
    print(f"✅ Commandes Slash synchronisées.")

@bot.event
async def on_message(message):
    """Suivre uniquement les messages du bot cible."""
    if message.author.id != TARGET_BOT_ID:
        return

    if "won the" in message.content.lower():
        print("🎉 Un gagnant détecté dans le message.")
        await retrieve_previous_message_with_summary(message.channel)

async def retrieve_previous_message_with_summary(channel):
    """Trouver et traiter le message 'Giveaway Summary'."""
    async for msg in channel.history(limit=50):
        if hasattr(msg, "components") and msg.components:
            for component in msg.components:
                for button in component.children:
                    if button.label.lower() == "giveaway summary":
                        await download_json_from_summary(button.url, channel)
                        return

async def download_json_from_summary(url, channel):
    """Télécharger et traiter le résumé du giveaway."""
    api_url = url.replace("https://giveawaybot.party/summary#", "https://summary-api.giveawaybot.party/?")
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        raw_data = response.json()

        print(f"✅ JSON brut récupéré : {raw_data}")
        process_giveaway_data(raw_data)

        await channel.send(f"🎉 Leaderboard mis à jour automatiquement !")
    except Exception as e:
        print(f"❌ Erreur lors du traitement : {e}")
        await channel.send(f"⚠️ Une erreur est survenue : {str(e)}")

def start_bot():
    """Démarrer le bot Discord."""
    bot.run(os.getenv("DISCORD_TOKEN"))

# Lancer Flask et le bot Discord en parallèle
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    start_bot()
