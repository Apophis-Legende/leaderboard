import discord
from discord import app_commands
from discord.ext import commands
import requests
import os
import json
import asyncio
from logique import process_giveaway_data
from utils.html_utils import generate_html_table
from PIL import Image, ImageDraw, ImageFont


# Configuration du bot avec intentions
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ID du bot cible que vous souhaitez suivre (par exemple, le bot de giveaway)
TARGET_BOT_ID = 294882584201003009  # ID du GiveawayBot

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

        await channel.send(f"🎉 Leaderboard mis à jour automatiquement !")
        print(f"✅ Leaderboard mis à jour.")
    except Exception as e:
        print(f"❌ Erreur lors du traitement : {e}")
        await channel.send(f"⚠️ Une erreur est survenue : {str(e)}")


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Commandes Slash synchronisées. Connecté en tant que {bot.user}.")
    print(f"📋 Commandes enregistrées : {[cmd.name for cmd in bot.tree.get_commands()]}")

        
# Lancer le bot
bot.run(os.getenv("DISCORD_TOKEN"))
