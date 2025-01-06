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

def create_table_image(data, serveur, guild):
    """
    Crée une image avec un tableau représentant le leaderboard.
    """
    # Taille de l'image (largeur, hauteur)
    width, height = 600, 400
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)

    # Utiliser la police par défaut de Pillow (pas besoin de fichier .ttf)
    font = ImageFont.load_default()

    # Définir les en-têtes du tableau
    headers = ["Nom d'utilisateur", "Gains Totaux", "Pertes Totales", "Mises Totales", "Participation"]
    data_rows = []

    # Récupérer les pseudos des utilisateurs depuis le serveur
    for user_id, user_data in data["utilisateurs"].items():
        # Récupérer l'utilisateur du serveur par son ID
        member = guild.get_member(int(user_id))  # Convertir user_id en int

        # Vérifier si le membre existe
        if member:
            nickname = member.nick if member.nick else member.name  # Utiliser le pseudo ou le nom d'utilisateur
        else:
            nickname = user_data["username"]  # Si l'utilisateur n'est plus membre, utiliser le nom d'utilisateur global

        # Ajouter les données de l'utilisateur dans le tableau
        data_rows.append([
            nickname,  # Utiliser le pseudo spécifique au serveur ou le nom d'utilisateur global
            f"{user_data['total_wins']} jetons", 
            f"{user_data['total_losses']} jetons", 
            f"{user_data['total_bets']} jetons", 
            user_data["participation"]
        ])

    # Position du tableau sur l'image
    x_offset = 10
    y_offset = 10
    row_height = 30
    col_width = 120  # Largeur des colonnes

    # Dessiner l'en-tête avec un fond coloré
    header_bg_color = (30, 144, 255)  # Bleu clair
    draw.rectangle([x_offset, y_offset, width, y_offset + row_height], fill=header_bg_color)

    # Dessiner les textes des en-têtes et les bordures des colonnes
    for i, header in enumerate(headers):
        # Calculer la position pour centrer le texte
        bbox = draw.textbbox((0, 0), header, font=font)  # Récupérer la boîte englobante du texte
        text_width = bbox[2] - bbox[0]  # largeur du texte
        text_height = bbox[3] - bbox[1]  # hauteur du texte
        x_position = x_offset + i * col_width + (col_width - text_width) / 2
        y_position = y_offset + (row_height - text_height) / 2  # Centrer verticalement
        draw.text((x_position, y_position), header, font=font, fill="white")
        # Dessiner la ligne de séparation entre les colonnes
        draw.line([(x_offset + (i + 1) * col_width, y_offset), 
                   (x_offset + (i + 1) * col_width, y_offset + row_height)], fill="black", width=2)

    # Dessiner les lignes du tableau
    y_offset += row_height
    for row in data_rows:
        for i, col in enumerate(row):
            # Calculer la position pour centrer le texte
            bbox = draw.textbbox((0, 0), str(col), font=font)  # Récupérer la boîte englobante du texte
            text_width = bbox[2] - bbox[0]  # largeur du texte
            text_height = bbox[3] - bbox[1]  # hauteur du texte
            x_position = x_offset + i * col_width + (col_width - text_width) / 2
            y_position = y_offset + (row_height - text_height) / 2  # Centrer verticalement
            draw.text((x_position, y_position), str(col), font=font, fill="black")
            # Dessiner la ligne de séparation entre les colonnes
            draw.line([(x_offset + (i + 1) * col_width, y_offset), 
                       (x_offset + (i + 1) * col_width, y_offset + row_height)], fill="black", width=1)
        y_offset += row_height
        # Dessiner une ligne de séparation horizontale
        draw.line([(x_offset, y_offset), (width, y_offset)], fill="black", width=2)

    # Dessiner une bordure autour du tableau
    border_color = (0, 0, 0)
    border_thickness = 5
    draw.rectangle([0, 0, width, height], outline=border_color, width=border_thickness)

    # Sauvegarder l'image
    filename = f"leaderboard_{serveur}.png"
    image.save(filename)
    return filename

@bot.tree.command(name="leaderboard", description="Affiche un leaderboard sous forme d'image.")
@app_commands.describe(serveur="Le serveur pour lequel afficher le tableau (ex: T1, T2)")
async def leaderboard_table(interaction: discord.Interaction, serveur: str):
    """
    Affiche un leaderboard sous forme d'image.
    """
    try:
        # Charger les données JSON du serveur
        filename = f"{serveur}.json"
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Le fichier `{serveur}.json` n'existe pas.")

        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Obtenir l'objet guild (serveur)
        guild = interaction.guild

        # Créer l'image avec le tableau
        image_file = create_table_image(data, serveur, guild)

        # Envoyer l'image dans Discord
        await interaction.response.send_message(
            f"📄 Voici le tableau de classement pour le serveur {serveur} :",
            file=discord.File(image_file)
        )

    except FileNotFoundError:
        await interaction.response.send_message(f"⚠️ Le fichier `{serveur}.json` n'existe pas.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Une erreur est survenue : {e}", ephemeral=True)



@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Commandes Slash synchronisées. Connecté en tant que {bot.user}.")
    print(f"📋 Commandes enregistrées : {[cmd.name for cmd in bot.tree.get_commands()]}")

        
# Lancer le bot
bot.run(os.getenv("DISCORD_TOKEN"))
