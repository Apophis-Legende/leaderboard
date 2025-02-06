
from discord import app_commands
import discord
from replit import db

def format_amount(amount):
    return f"{amount} jetons"

async def manual_add_giveaway(interaction, participants_count: int, winner: discord.Member, prize: str):
    try:
        # Vérifier le format du prix (ex: "T2 950")
        server = prize.split()[0]
        gain = int(prize.split()[1])
        server_file = f"{server}.json"
        
        # Calculer les mises et commissions
        bet = int(gain / 0.95)  # Mise totale avant commission
        commission = bet - gain  # Commission
        bet_per_player = bet // participants_count  # Mise par joueur
        
        # Charger ou créer les données du serveur
        data = db.get(server_file, {
            "serveur": server,
            "nombre_de_jeux": 0,
            "mises_totales_avant_commission": "0 jetons",
            "gains_totaux": "0 jetons",
            "commission_totale": "0 jetons",
            "utilisateurs": {},
            "hôtes": {},
            "croupiers": {}
        })

        # Mettre à jour les statistiques globales
        data["nombre_de_jeux"] += 1
        data["mises_totales_avant_commission"] = format_amount(int(data["mises_totales_avant_commission"].split()[0]) + bet)
        data["gains_totaux"] = format_amount(int(data["gains_totaux"].split()[0]) + gain)
        data["commission_totale"] = format_amount(int(data["commission_totale"].split()[0]) + commission)

        # Mettre à jour le gagnant
        winner_id = str(winner.id)
        if winner_id not in data["utilisateurs"]:
            data["utilisateurs"][winner_id] = {
                "username": winner.name,
                "total_wins": "0 jetons",
                "total_losses": "0 jetons",
                "total_bets": "0 jetons",
                "participation": 0
            }
        
        user_data = data["utilisateurs"][winner_id]
        user_data["total_wins"] = format_amount(int(user_data["total_wins"].split()[0]) + gain)
        user_data["total_bets"] = format_amount(int(user_data["total_bets"].split()[0]) + bet_per_player)
        user_data["participation"] += 1

        # Sauvegarder les données
        db[server_file] = data
        
        await interaction.followup.send(f"✅ Giveaway ajouté manuellement:\n"
                                      f"🎮 Serveur: {server}\n"
                                      f"👥 Participants: {participants_count}\n"
                                      f"🏆 Gagnant: {winner.mention}\n"
                                      f"💰 Prix: {gain} jetons")
        
    except Exception as e:
        await interaction.followup.send(f"❌ Une erreur est survenue: {str(e)}")
