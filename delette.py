
import discord
from discord.ext import commands
from replit import db
import requests

async def delete_giveaway(interaction: discord.Interaction, link: str):
    try:
        await interaction.response.defer()

        # Convertir le lien en lien API si nécessaire
        api_url = link.replace("https://giveawaybot.party/summary#", "https://summary-api.giveawaybot.party/?")
        response = requests.get(api_url)
        giveaway_data = response.json()

        if not giveaway_data or "giveaway" not in giveaway_data:
            raise Exception("Données du giveaway invalides")

        prize = giveaway_data["giveaway"]["prize"]
        server = prize.split()[0]
        server_name = f"{server}.json"

        # Charger les données actuelles
        data = db.get(server_name)
        if not data:
            raise Exception("Données non trouvées pour ce serveur")

        # Extraction des informations
        winners = giveaway_data.get("winners", [])
        entries = giveaway_data.get("entries", [])
        gain = int(prize.split()[1])
        bet = int(gain / 0.95)
        commission = bet - gain

        # Mise à jour des utilisateurs
        for winner in winners:
            user_id = str(winner["id"])
            if user_id in data["utilisateurs"]:
                user = data["utilisateurs"][user_id]
                user["total_wins"] = f"{max(0, int(user['total_wins'].split()[0]) - gain)} jetons"
                user["total_bets"] = f"{max(0, int(user['total_bets'].split()[0]) - bet//len(entries))} jetons"
                user["participation"] = max(0, user["participation"] - 1)

        for entry in entries:
            if str(entry["id"]) not in [str(w["id"]) for w in winners]:
                user_id = str(entry["id"])
                if user_id in data["utilisateurs"]:
                    user = data["utilisateurs"][user_id]
                    user["total_losses"] = f"{max(0, int(user['total_losses'].split()[0]) - bet//len(entries))} jetons"
                    user["total_bets"] = f"{max(0, int(user['total_bets'].split()[0]) - bet//len(entries))} jetons"
                    user["participation"] = max(0, user["participation"] - 1)

        # Mise à jour hôte
        host = giveaway_data["giveaway"]["host"]
        host_id = str(host["id"])
        if host_id in data["hôtes"]:
            host_data = data["hôtes"][host_id]
            host_data["total_bets"] = f"{max(0, int(host_data['total_bets'].split()[0]) - bet)} jetons"
            host_data["total_commission"] = f"{max(0, int(host_data['total_commission'].split()[0]) - commission)} jetons"

        # Mise à jour données globales
        data["nombre_de_jeux"] = max(0, data["nombre_de_jeux"] - 1)
        data["mises_totales_avant_commission"] = f"{max(0, int(data['mises_totales_avant_commission'].split()[0]) - bet)} jetons"
        data["gains_totaux"] = f"{max(0, int(data['gains_totaux'].split()[0]) - gain)} jetons"
        data["commission_totale"] = f"{max(0, int(data['commission_totale'].split()[0]) - commission)} jetons"

        # Sauvegarder
        db[server_name] = data
        await interaction.followup.send("✅ Giveaway supprimé avec succès")

    except Exception as e:
        await interaction.followup.send(f"❌ Erreur: {str(e)}")
