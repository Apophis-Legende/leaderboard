import discord
from discord.ext import commands
from replit import db
import requests

MAPPING_SERVER_FILE = {
    "T1": "T1",
    "T2": "T2", 
    "O1": "O1",
    "H1": "H1",
    "E1": "E1"
}

async def delete_giveaway(interaction: discord.Interaction, link: str):
    try:
        await interaction.response.defer()

        # Extraire les données du giveaway
        response = requests.get(link)
        giveaway_data = response.json()
        prize = giveaway_data.get("giveaway", {}).get("prize", "")

        server = prize.split()[0]
        server_name = MAPPING_SERVER_FILE.get(server)

        if not server_name:
            await interaction.followup.send(f"⚠️ Serveur {server} non reconnu", ephemeral=True)
            return

        # Charger les données actuelles
        data = db.get(server_name)
        if not data:
            await interaction.followup.send("❌ Données non trouvées", ephemeral=True)
            return

        # Mise à jour des données...
        winners = giveaway_data.get("winners", [])
        entries = giveaway_data.get("entries", [])
        gain = int(prize.split()[1])
        bet = int(gain / 0.95)
        commission = bet - gain

        # Mettre à jour utilisateurs
        for winner in winners:
            user_id = winner["id"]
            if user_id in data["utilisateurs"]:
                user = data["utilisateurs"][user_id] 
                user["total_wins"] = str(int(user["total_wins"].split()[0]) - gain) + " jetons"
                user["total_bets"] = str(int(user["total_bets"].split()[0]) - bet//len(entries)) + " jetons"
                user["participation"] = max(0, user["participation"] - 1)

        # Mettre à jour les données globales        
        data["nombre_de_jeux"] = max(0, data["nombre_de_jeux"] - 1)
        data["mises_totales_avant_commission"] = str(int(data["mises_totales_avant_commission"].split()[0]) - bet) + " jetons"
        data["gains_totaux"] = str(int(data["gains_totaux"].split()[0]) - gain) + " jetons"
        data["commission_totale"] = str(int(data["commission_totale"].split()[0]) - commission) + " jetons"

        # Sauvegarder
        db[server_name] = data

        await interaction.followup.send("✅ Giveaway supprimé avec succès", ephemeral=True)

    except Exception as e:
        await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)