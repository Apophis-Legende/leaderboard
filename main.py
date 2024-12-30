import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
import json
from logique import fetch_giveaway_info, update_leaderboard, calculate_prize_in_tokens, get_leaderboard, delete_leaderboard_file
from roll import roll_dice
from tokens_manager import get_bot_tokens, update_bot_tokens, deduct_bot_tokens
import re
import functools

# Création de l'instance du bot avec intents
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# Définition de la commande pour ajouter les informations d'un giveaway via scraping
@tree.command(name='add', description='Ajouter les informations d\'un giveaway via scraping')
async def add(interaction: discord.Interaction, lien: str):
    try:
        lien = lien.strip()
        if not lien.startswith(('http://', 'https://')):
            await interaction.response.send_message("L'URL doit commencer par 'http://' ou 'https://'.")
            return

        print(f"Lien reçu : {lien}")  # Pour le débogage
        data = fetch_giveaway_info(lien)

        # Afficher les données JSON récupérées pour le débogage
        print("Données JSON récupérées : ", data)

        # Vérifiez si les clés existent
        if 'winners' not in data or 'entries' not in data or 'giveaway' not in data:
            raise KeyError("Les données du giveaway sont incomplètes.")

        winners = data['winners']
        entries = data['entries']
        giveaway_info = data['giveaway']

        host = giveaway_info['host']
        prize_raw = giveaway_info['prize']

        # Assurez-vous que prize_raw est bien une chaîne
        if isinstance(prize_raw, int):
            prize_raw = str(prize_raw)

        prize = calculate_prize_in_tokens(prize_raw)

        # Mettre à jour le leaderboard avec les nouvelles données
        update_leaderboard(winners, entries, host, prize)

        await interaction.response.send_message("Les informations du giveaway ont été ajoutées avec succès !")
    except Exception as e:
        await interaction.response.send_message(f"Erreur : {str(e)}")

@tree.command(name='lbg', description='Afficher le leaderboard des joueurs')
async def lbg(interaction: discord.Interaction):
    try:
        leaderboard_message = get_leaderboard()  # Assurez-vous que cette fonction est importée
        await interaction.response.send_message(leaderboard_message)
    except Exception as e:
        await interaction.response.send_message(f"Erreur lors de l'affichage du leaderboard : {str(e)}")

@tree.command(name="delete_leaderboard", description="Supprimer le leaderboard.")
async def delete_leaderboard(interaction: discord.Interaction):
    # Appeler la fonction pour supprimer le fichier
    delete_leaderboard_file()

    await interaction.response.send_message("Le leaderboard a été supprimé.")

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    match = re.match(r'!give <@!?(\d+)> (\d+)', message.content)
    if match:
        user_id = int(match.group(1))
        bet_amount = int(match.group(2))

        bot_tokens = get_bot_tokens()

        # Vérifier si le bot a assez de jetons avant de procéder
        if bot_tokens >= bet_amount:
            update_bot_tokens(-bet_amount)  # Retirer le montant misé
            await create_dice_buttons(message, bet_amount, user_id)
        else:
            await message.channel.send("Pas assez de jetons dans le stock. Ta mise a été annulée.")

async def create_dice_buttons(message, bet_amount, user_id):
    view = discord.ui.View(timeout=None)

    # Boucle pour créer les boutons de 1 à 6
    for i in range(1, 7):
        button = discord.ui.Button(label=str(i), style=discord.ButtonStyle.primary)

        # Capturer correctement les variables pour le callback
        async def button_callback(interaction: discord.Interaction, roll_value=i):
            result = await roll_dice(interaction, bet_amount, user_id)
            if result:  # Si le joueur gagne
                await interaction.response.send_message(f"Tu as gagné ! Résultat du dé : {roll_value}. Jetons du bot maintenant : {get_bot_tokens()}")
            else:  # Si le joueur perd
                await interaction.response.send_message(f"Tu as perdu. Résultat du dé : {roll_value}. Jetons du bot : {get_bot_tokens()}")

        button.callback = button_callback
        view.add_item(button)

    await message.channel.send("Choisissez un nombre en cliquant sur un des boutons :", view=view)

@bot.event
async def on_ready():
    await tree.sync()  # Synchroniser les commandes
    print(f"Connecté en tant que {bot.user}")

# Récupérer le token du bot Discord depuis les secrets de Replit
TOKEN = os.getenv('DISCORD_TOKEN')

# Lancer le bot
bot.run(TOKEN)
