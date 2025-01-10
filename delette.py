import json
import os
import requests
import discord
from discord.ext import commands
from threading import Lock

# MAPPING_SERVER_FILE défini pour correspondre aux fichiers JSON par serveur
MAPPING_SERVER_FILE = {
    "T1": "T1.json",
    "T2": "T2.json",
    "O1": "O1.json",
    "H1": "H1.json",
    "E1": "E1.json"
}

# Verrou pour éviter les conflits d'accès simultané aux fichiers JSON
file_lock = Lock()

def load_json(filename):
    """
    Charge un fichier JSON en toute sécurité.
    """
    with file_lock:
        if not os.path.exists(filename):
            return None
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)

def save_json(filename, data):
    """
    Sauvegarde des données dans un fichier JSON en toute sécurité.
    """
    with file_lock:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

def format_amount(amount):
    """
    Convertit un float en une chaîne au format "123 jetons".
    """
    return f"{int(amount)} jetons"

def convert_amount_to_int(amount_str):
    """
    Convertit une chaîne au format "123 jetons" en un entier.
    """
    return int(amount_str.split(" ")[0])

@commands.has_permissions(administrator=True)
async def delete_giveaway(interaction: discord.Interaction, link: str):
    """
    Commande pour supprimer les données d'un giveaway à partir d'un lien donné.
    """
    try:
        # Marquer l'interaction comme différée
        if not interaction.response.is_done():
            await interaction.response.defer()

        # Étape 1 : Télécharger et analyser le JSON
        try:
            response = requests.get(link, timeout=10)  # Timeout pour éviter les blocages
            response.raise_for_status()  # Vérifie les erreurs HTTP
            giveaway_data = response.json()
        except requests.exceptions.RequestException as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"⚠️ Erreur réseau : {e}", ephemeral=True)
            else:
                await interaction.followup.send(f"⚠️ Erreur réseau : {e}", ephemeral=True)
            return
        except json.JSONDecodeError:
            if not interaction.response.is_done():
                await interaction.response.send_message("⚠️ Les données téléchargées ne sont pas au format JSON valide.", ephemeral=True)
            else:
                await interaction.followup.send("⚠️ Les données téléchargées ne sont pas au format JSON valide.", ephemeral=True)
            return

        # Étape 2 : Extraire les informations nécessaires
        prize = giveaway_data.get("giveaway", {}).get("prize", "")
        if not prize:
            if not interaction.response.is_done():
                await interaction.response.send_message("⚠️ Le lien ne contient pas les informations nécessaires.", ephemeral=True)
            else:
                await interaction.followup.send("⚠️ Le lien ne contient pas les informations nécessaires.", ephemeral=True)
            return

        server = prize.split()[0]
        filename = MAPPING_SERVER_FILE.get(server)
        if not filename:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"⚠️ Le serveur {server} n'est pas pris en charge.", ephemeral=True)
            else:
                await interaction.followup.send(f"⚠️ Le serveur {server} n'est pas pris en charge.", ephemeral=True)
            return

        # Étape 3 : Charger les données du serveur
        server_data = load_json(filename)
        if not server_data:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"⚠️ Le fichier {filename} est introuvable ou vide.", ephemeral=True)
            else:
                await interaction.followup.send(f"⚠️ Le fichier {filename} est introuvable ou vide.", ephemeral=True)
            return

        # Étape 4 : Traiter les données du giveaway
        winners = giveaway_data.get("winners", [])
        entries = giveaway_data.get("entries", [])
        gain_after_commission = int(prize.split()[1])
        total_bet_before_commission = int(gain_after_commission / 0.95)
        commission_total = total_bet_before_commission - gain_after_commission

        for winner in winners:
            user_id = winner["id"]
            if user_id in server_data["utilisateurs"]:
                user = server_data["utilisateurs"][user_id]
                user["total_wins"] = format_amount(convert_amount_to_int(user["total_wins"]) - gain_after_commission)
                user["total_bets"] = format_amount(convert_amount_to_int(user["total_bets"]) - total_bet_before_commission / len(entries))
                user["participation"] = max(0, user["participation"] - 1)

        for entry in entries:
            if entry["id"] not in [winner["id"] for winner in winners]:
                user_id = entry["id"]
                if user_id in server_data["utilisateurs"]:
                    user = server_data["utilisateurs"][user_id]
                    user["total_losses"] = format_amount(convert_amount_to_int(user["total_losses"]) - total_bet_before_commission / len(entries))
                    user["total_bets"] = format_amount(convert_amount_to_int(user["total_bets"]) - total_bet_before_commission / len(entries))
                    user["participation"] = max(0, user["participation"] - 1)

        # Mise à jour des hôtes et croupiers
        host_id = giveaway_data["giveaway"]["host"]["id"]
        if host_id in server_data["hôtes"]:
            host = server_data["hôtes"][host_id]
            host["total_bets"] = format_amount(convert_amount_to_int(host["total_bets"]) - total_bet_before_commission)
            host["total_commission"] = format_amount(convert_amount_to_int(host["total_commission"]) - commission_total)

        if host_id in server_data["croupiers"]:
            croupier = server_data["croupiers"][host_id]
            croupier["total_giveaways"] = max(0, croupier["total_giveaways"] - 1)
            croupier["total_kamas_managed"] = format_amount(convert_amount_to_int(croupier["total_kamas_managed"]) - total_bet_before_commission)
            croupier["total_commission"] = format_amount(convert_amount_to_int(croupier["total_commission"]) - commission_total)

        # Mise à jour globale
        server_data["nombre_de_jeux"] = max(0, server_data["nombre_de_jeux"] - 1)
        server_data["mises_totales_avant_commission"] = format_amount(
            convert_amount_to_int(server_data["mises_totales_avant_commission"]) - total_bet_before_commission
        )
        server_data["gains_totaux"] = format_amount(
            convert_amount_to_int(server_data["gains_totaux"]) - gain_after_commission
        )
        server_data["commission_totale"] = format_amount(
            convert_amount_to_int(server_data["commission_totale"]) - commission_total
        )

        # Étape 5 : Sauvegarder les données mises à jour
        save_json(filename, server_data)
        if not interaction.response.is_done():
            await interaction.response.send_message(f"✅ Les données associées au giveaway ont été supprimées dans {filename}.", ephemeral=True)
        else:
            await interaction.followup.send(f"✅ Les données associées au giveaway ont été supprimées dans {filename}.", ephemeral=True)

    except Exception as e:
        # Gestion des erreurs
        error_message = f"❌ Une erreur est survenue : {str(e)}"
        if not interaction.response.is_done():
            await interaction.response.send_message(error_message, ephemeral=True)
        else:
            await interaction.followup.send(error_message, ephemeral=True)
