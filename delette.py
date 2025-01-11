
import discord
from discord.ext import commands
from replit import db
import requests

async def delete_giveaway(interaction: discord.Interaction, link: str):
    try:
        # Convertir le lien en API
        api_url = link.replace("https://giveawaybot.party/summary#", "https://summary-api.giveawaybot.party/?")
        response = requests.get(api_url)
        giveaway_data = response.json()

        if not giveaway_data or "giveaway" not in giveaway_data:
            raise Exception("Données du giveaway invalides")

        # Extraire les informations du serveur et du prix
        prize = giveaway_data["giveaway"]["prize"]
        server = prize.split()[0]
        server_file = f"{server}.json"

        # Charger les données du serveur
        data = db.get(server_file)
        if not data:
            raise Exception(f"Données non trouvées pour le serveur {server}")

        # Extraire les participants et gagnants
        winners = giveaway_data.get("winners", [])
        entries = giveaway_data.get("entries", [])
        
        if not entries:
            raise Exception("Aucun participant trouvé")

        # Calculer les montants
        gain = int(prize.split()[1])
        bet = int(gain / 0.95)
        commission = bet - gain
        bet_per_player = bet // len(entries)

        # Mettre à jour les statistiques des gagnants
        for winner in winners:
            user_id = str(winner["id"])
            if user_id in data["utilisateurs"]:
                user = data["utilisateurs"][user_id]
                current_wins = int(user.get("total_wins", "0 jetons").split()[0])
                current_bets = int(user.get("total_bets", "0 jetons").split()[0])
                
                user["total_wins"] = f"{max(0, current_wins - gain)} jetons"
                user["total_bets"] = f"{max(0, current_bets - bet_per_player)} jetons"
                user["participation"] = max(0, user.get("participation", 1) - 1)

        # Mettre à jour les statistiques des perdants
        for entry in entries:
            user_id = str(entry["id"])
            if user_id not in [str(w["id"]) for w in winners] and user_id in data["utilisateurs"]:
                user = data["utilisateurs"][user_id]
                current_losses = int(user.get("total_losses", "0 jetons").split()[0])
                current_bets = int(user.get("total_bets", "0 jetons").split()[0])
                
                user["total_losses"] = f"{max(0, current_losses - bet_per_player)} jetons"
                user["total_bets"] = f"{max(0, current_bets - bet_per_player)} jetons"
                user["participation"] = max(0, user.get("participation", 1) - 1)

        # Mettre à jour les statistiques de l'hôte
        host = giveaway_data["giveaway"]["host"]
        host_id = str(host["id"])
        if host_id in data["hôtes"]:
            host_data = data["hôtes"][host_id]
            current_host_bets = int(host_data.get("total_bets", "0 jetons").split()[0])
            current_host_commission = int(host_data.get("total_commission", "0 jetons").split()[0])
            
            host_data["total_bets"] = f"{max(0, current_host_bets - bet)} jetons"
            host_data["total_commission"] = f"{max(0, current_host_commission - commission)} jetons"

        # Mettre à jour les totaux du serveur
        data["nombre_de_jeux"] = max(0, data["nombre_de_jeux"] - 1)
        current_total_bets = int(data.get("mises_totales_avant_commission", "0 jetons").split()[0])
        current_total_gains = int(data.get("gains_totaux", "0 jetons").split()[0])
        current_total_commission = int(data.get("commission_totale", "0 jetons").split()[0])
        
        data["mises_totales_avant_commission"] = f"{max(0, current_total_bets - bet)} jetons"
        data["gains_totaux"] = f"{max(0, current_total_gains - gain)} jetons"
        data["commission_totale"] = f"{max(0, current_total_commission - commission)} jetons"

        # Sauvegarder les modifications
        db[server_file] = data
        await interaction.followup.send("✅ Giveaway supprimé avec succès")
        
    except Exception as e:
        await interaction.followup.send(f"❌ Erreur: {str(e)}")
