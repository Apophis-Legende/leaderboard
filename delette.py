import discord
from discord.ext import commands
from replit import db
import requests

async def delete_giveaway(interaction, link):
    # Extraire l'ID du giveaway depuis le lien
    giveaway_id = link.split('#')[1] if '#' in link else None
    if not giveaway_id:
        raise ValueError("❌ Le lien du giveaway est invalide.")

    # Vérifier et extraire les données du giveaway
    api_url = f"https://summary-api.giveawaybot.party/?{giveaway_id}"
    response = requests.get(api_url)
    if response.status_code != 200:
        raise ValueError("❌ Impossible de récupérer les données du giveaway.")

    data = response.json()
    server_name = data['giveaway']['prize'].split()[0]  # Extrait T1, T2, etc.

    # Vérifier si le serveur existe dans la DB
    json_key = f"{server_name}.json"
    if json_key not in db:
        raise ValueError(f"❌ Aucune donnée trouvée pour le serveur {server_name}")

    # Charger les données actuelles
    server_data = dict(db[json_key])  # Convertir ObservedDict en dict normal

    # Retirer les données des utilisateurs pour ce giveaway
    users = server_data.get("utilisateurs", {})
    for user_id, user_data in list(users.items()):
        # Réduire les statistiques
        participation = int(user_data.get("participation", 0))
        if participation > 0:
            user_data["participation"] = max(0, participation - 1)

        # Si plus de participation, retirer l'utilisateur
        if user_data["participation"] == 0:
            del users[user_id]

    # Mettre à jour les statistiques globales
    server_data["nombre_de_jeux"] = max(0, server_data.get("nombre_de_jeux", 0) - 1)

    # Sauvegarder les modifications dans la DB
    db[json_key] = server_data

    await interaction.followup.send(f"✅ Données du giveaway supprimées avec succès pour le serveur {server_name}.")