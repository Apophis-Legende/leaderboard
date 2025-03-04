
from replit import db
import discord

def format_amount(amount):
    return f"{amount} jetons"

async def remove_player_data(interaction, player: discord.Member, server: str, amount: int, remove_type: str = "bets"):
    try:
        # Vérifier le format du serveur
        server_file = f"{server}.json"
        
        # Charger les données du serveur
        data = db.get(server_file)
        if not data:
            raise ValueError(f"Aucune donnée trouvée pour le serveur {server}")

        player_id = str(player.id)
        if player_id not in data["utilisateurs"]:
            raise ValueError("Ce joueur n'a pas de données enregistrées")

        # Récupérer les données actuelles du joueur
        user_data = data["utilisateurs"][player_id]
        current_bets = int(user_data["total_bets"].split()[0])
        current_wins = int(user_data.get("total_wins", "0 jetons").split()[0])
        
        if remove_type == "bets":
            if current_bets < amount:
                raise ValueError(f"Le joueur n'a que {current_bets} jetons de mises")
            # Mettre à jour les mises du joueur
            user_data["total_bets"] = format_amount(current_bets - amount)
            user_data["total_wins"] = format_amount(current_wins - amount)
        else:  # remove_type == "wins"
            # Pour les bénéfices négatifs, on ajoute le montant au lieu de le soustraire
            if amount < 0:
                user_data["total_wins"] = format_amount(current_wins + abs(amount))
            else:
                if current_wins < amount:
                    raise ValueError(f"Le joueur n'a que {current_wins} jetons de gains")
                user_data["total_wins"] = format_amount(current_wins - amount)

        # Mettre à jour les statistiques globales
        current_total_bets = int(data["mises_totales_avant_commission"].split()[0])
        current_total_commission = int(data["commission_totale"].split()[0])
        
        # Calculer la commission (5.2631578947368%)
        commission_reduction = int(amount * 0.052631578947368)
        
        data["mises_totales_avant_commission"] = format_amount(current_total_bets - amount)
        data["commission_totale"] = format_amount(current_total_commission - commission_reduction)

        # Sauvegarder les modifications
        db[server_file] = data

        await interaction.followup.send(f"✅ Données mises à jour pour {player.mention}:\n"
                                      f"🎮 Serveur: {server}\n"
                                      f"💰 Mises retirées: {amount} jetons\n"
                                      f"📊 Nouvelles mises totales: {user_data['total_bets']}")

    except Exception as e:
        await interaction.followup.send(f"❌ Une erreur est survenue: {str(e)}")
