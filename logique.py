import discord
import os
import json
import re
from discord.ui import View, Select, Button, Modal, TextInput
from discord import Interaction
import asyncio
from replit import db

MAPPING_SERVER_FILE = {
    "T1": "T1.json",
    "T2": "T2.json",
    "O1": "O1.json",
    "H1": "H1.json",
    "E1": "E1.json"
}

from replit import db

def load_json(filename, default_data=None):
    """
    Charge les données depuis Replit DB.
    """
    try:
        return db[filename] if filename in db else (default_data or {})
    except Exception as e:
        print(f"❌ Erreur lors du chargement des données {filename}: {e}")
        return default_data or {}

def save_json(filename, data):
    """
    Sauvegarde les données dans Replit DB.
    """
    try:
        db[filename] = data
        print(f"✅ Données sauvegardées pour : {filename}")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde des données {filename}: {e}")
        raise

def convert_amount_to_float(amount_str):
    """
    Convertit une chaîne "400 jetons" en float 400.0
    """
    return float(amount_str.split(" ")[0])

def format_amount(amount):
    """
    Convertit un float 400.0 en chaîne "400 jetons"
    """
    return f"{int(amount)} jetons"

async def process_giveaway_data(raw_data, channel):
    """
    Traite les données brutes d'un giveaway et met à jour le fichier JSON du serveur concerné.
    """
    try:
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')

        if "giveaway" not in raw_data or "winners" not in raw_data or "entries" not in raw_data:
            raise KeyError("Les clés 'giveaway', 'winners' ou 'entries' sont manquantes dans les données.")

        # Extraire le gagnant et un perdant pour le message personnalisé
        winner = raw_data["winners"][0] if raw_data.get("winners") else None
        entries = raw_data.get("entries", [])

        if winner:
            winner_id = winner["id"]
            loser = next((entry for entry in entries if entry["id"] != winner_id), None)

            if loser:
                from giveaway_messages import get_random_winner_message
                await asyncio.sleep(1)  # Attendre 1 seconde
                custom_message = get_random_winner_message(f"<@{winner_id}>", f"<@{loser['id']}>")
                await channel.send(custom_message)

        print("🔍 Données reçues:", raw_data)  # Debug log

        giveaway_info = raw_data["giveaway"]
        prize = giveaway_info["prize"]
        server, gain_after_commission = prize.split()[0], float(prize.split()[1])

        total_bet_before_commission = int(gain_after_commission / 0.95)
        commission_total = total_bet_before_commission - gain_after_commission

        file_name = f"{server}.json"
        server_data = load_json(file_name, {
            "serveur": server,
            "nombre_de_jeux": 0,
            "mises_totales_avant_commission": "0 jetons",
            "gains_totaux": "0 jetons",
            "commission_totale": "0 jetons",
            "utilisateurs": {},
            "hôtes": {},
            "croupiers": {}
        })

        previous_total_bet = convert_amount_to_float(server_data["mises_totales_avant_commission"])
        server_data["mises_totales_avant_commission"] = format_amount(previous_total_bet + total_bet_before_commission)

        previous_total_gain = convert_amount_to_float(server_data["gains_totaux"])
        server_data["gains_totaux"] = format_amount(previous_total_gain + gain_after_commission)

        previous_total_commission = convert_amount_to_float(server_data["commission_totale"])
        server_data["commission_totale"] = format_amount(previous_total_commission + commission_total)

        server_data["nombre_de_jeux"] += 1
        server_data["derniere_mise_a_jour"] = today

        for winner in raw_data["winners"]:
            user_id = winner["id"]
            username = winner["username"]

            if user_id not in server_data["utilisateurs"]:
                server_data["utilisateurs"][user_id] = {
                    "username": username,
                    "total_wins": "0 jetons",
                    "total_losses": "0 jetons",
                    "total_bets": "0 jetons",
                    "participation": 0
                }

            current_wins = convert_amount_to_float(server_data["utilisateurs"][user_id]["total_wins"])
            current_bets = convert_amount_to_float(server_data["utilisateurs"][user_id]["total_bets"])
            server_data["utilisateurs"][user_id]["total_wins"] = format_amount(current_wins + gain_after_commission)
            server_data["utilisateurs"][user_id]["total_bets"] = format_amount(
                current_bets + total_bet_before_commission // len(raw_data["entries"])
            )
            server_data["utilisateurs"][user_id]["participation"] += 1

        for entry in raw_data["entries"]:
            if entry["id"] in [winner["id"] for winner in raw_data["winners"]]:
                continue
            user_id = entry["id"]
            username = entry["username"]

            if user_id not in server_data["utilisateurs"]:
                server_data["utilisateurs"][user_id] = {
                    "username": username,
                    "total_wins": "0 jetons",
                    "total_losses": "0 jetons",
                    "total_bets": "0 jetons",
                    "participation": 0
                }

            current_losses = convert_amount_to_float(server_data["utilisateurs"][user_id]["total_losses"])
            current_bets = convert_amount_to_float(server_data["utilisateurs"][user_id]["total_bets"])
            server_data["utilisateurs"][user_id]["total_losses"] = format_amount(
                current_losses + total_bet_before_commission // len(raw_data["entries"])
            )
            server_data["utilisateurs"][user_id]["total_bets"] = format_amount(
                current_bets + total_bet_before_commission // len(raw_data["entries"])
            )
            server_data["utilisateurs"][user_id]["participation"] += 1

        host_id = giveaway_info["host"]["id"]
        host_username = giveaway_info["host"]["username"]

        if host_id not in server_data["hôtes"]:
            server_data["hôtes"][host_id] = {
                "username": host_username,
                "total_bets": "0 jetons",
                "total_commission": "0 jetons",
                "total_giveaways": 1
            }
        else:
            if "total_giveaways" not in server_data["hôtes"][host_id]:
                server_data["hôtes"][host_id]["total_giveaways"] = 0
            server_data["hôtes"][host_id]["total_giveaways"] += 1

        current_host_bets = convert_amount_to_float(server_data["hôtes"][host_id]["total_bets"])
        current_host_commission = convert_amount_to_float(server_data["hôtes"][host_id]["total_commission"])
        server_data["hôtes"][host_id]["total_bets"] = format_amount(current_host_bets + total_bet_before_commission)
        server_data["hôtes"][host_id]["total_commission"] = format_amount(current_host_commission + commission_total)

        print(f"💾 Tentative de sauvegarde dans {file_name}...")
        save_json(file_name, server_data)

        # Vérifier immédiatement si les données sont bien sauvegardées
        verification = load_json(file_name)
        if verification:
            print(f"✅ Données sauvegardées avec succès dans {file_name}")
            print(f"📊 Données actuelles dans la base :")
            print(f"- Serveur : {verification.get('serveur')}")
            print(f"- Nombre de jeux : {verification.get('nombre_de_jeux')}")
            print(f"- Utilisateurs : {len(verification.get('utilisateurs', {}))}")
            print(f"- Hôtes : {len(verification.get('hôtes', {}))}")
        else:
            print(f"❌ ERREUR : Les données ne sont pas visibles dans {file_name}")


        return {
            "server": server,
            "gain_after_commission": gain_after_commission,
            "total_bet_before_commission": total_bet_before_commission,
            "commission_total": commission_total,
        }

    except Exception as e:
        print(f"❌ Une erreur inattendue : {e}")
        return {"error": str(e)}

class ConfirmDataView(View):
    def __init__(self, interaction: Interaction, data):
        super().__init__()
        self.interaction = interaction
        self.data = data
        self.value = None

    @discord.ui.button(label="Valider", style=discord.ButtonStyle.success)
    async def confirm(self, button: Button, interaction: Interaction):
        self.value = True
        await interaction.response.send_message("✅ Données validées par l’hôte.")
        self.stop()

    @discord.ui.button(label="Rejeter", style=discord.ButtonStyle.danger)
    async def reject(self, button: Button, interaction: Interaction):
        self.value = False
        await interaction.response.send_message("❌ Données rejetées par l’hôte.")
        self.stop()