import json
import requests
import os  # Pour accéder aux secrets d'environnement
from prettytable import PrettyTable

# Fichier pour stocker les informations de leaderboard
leaderboard_file = "leaderboard.json"

# Convertir le prix en jetons
def calculate_prize_in_tokens(prize_str):
    if isinstance(prize_str, (int, float)):
        return float(prize_str)

    # Remplacer les notations "K" et "M" pour les convertir en jetons
    prize_str = prize_str.lower().replace("m", "000000").replace("k", "000").replace(" ", "")
    return float(prize_str)  # Retourne le montant en jetons

# Convertir le prix en nombre
def convert_prize_to_number(prize_str):
    if isinstance(prize_str, (int, float)):
        return float(prize_str)

    prize_str = prize_str.lower().replace("m", "000000").replace("k", "000").replace(" ", "")
    return float(prize_str)

def convert_amount_to_float(amount_str):
    try:
        if isinstance(amount_str, (int, float)):
            return float(amount_str)

        amount_str = amount_str.replace("jetons", "").strip()  # Retire 'jetons' et les espaces

        if "k" in amount_str.lower():
            return float(amount_str.replace("k", "").replace("K", "").strip()) * 1000
        elif "m" in amount_str.lower():
            return float(amount_str.replace("m", "").replace("M", "").strip()) * 1000000

        return float(amount_str)  # Convertit directement en float
    except ValueError as e:
        print(f"Erreur lors de la conversion de '{amount_str}': {e}")
        return 0.0  # Retourne 0.0 en cas d'erreur

# Fonction pour formater les montants en jetons
def format_amount(amount):
    if amount >= 1000000:  # 1M
        return f"{amount / 1000000:.2f}M jetons"
    elif amount >= 1000:  # 1K
        return f"{amount / 1000:.2f}K jetons"
    else:
        return f"{amount:.2f} jetons"

# Récupérer les données depuis l'API
def fetch_giveaway_info(lien):
    response = requests.get(lien)
    if response.status_code != 200:
        raise Exception("Erreur lors de l'accès à l'API")
    return response.json()

def update_leaderboard(winners, entries, host, prize):
    # Lire le leaderboard existant ou l'initialiser
    if os.path.exists(leaderboard_file):
        with open(leaderboard_file, "r") as f:
            leaderboard = json.load(f)
    else:
        leaderboard = {"users": {}, "hosts": {}}

    # Convertir le prix en nombre de jetons
    total_prize = convert_prize_to_number(prize)  # Convertir le prix en jetons
    total_bets = total_prize / 0.95  # Appliquer la réduction de 5%

    # Calculer la commission de 5 % pour l'hôte
    commission = total_bets * 0.05

    # Mettre à jour les gains, pertes et mises pour chaque gagnant
    for winner in winners:
        user_id = winner['id']
        username = winner['username']

        if user_id not in leaderboard["users"]:
            leaderboard["users"][user_id] = {
                "username": username,
                "total_wins": "0 jetons",
                "total_losses": "0 jetons",
                "total_bets": "0 jetons"
            }

        # Mettre à jour les gains
        current_wins = convert_amount_to_float(leaderboard["users"][user_id]["total_wins"])
        leaderboard["users"][user_id]["total_wins"] = format_amount(current_wins + total_prize)

    # Mettre à jour les pertes et les mises pour tous les participants
    for entry in entries:
        user_id = entry['id']
        username = entry['username']

        if user_id not in [winner['id'] for winner in winners]:  # S'il n'est pas gagnant
            if user_id not in leaderboard["users"]:
                leaderboard["users"][user_id] = {
                    "username": username,
                    "total_wins": "0 jetons",
                    "total_losses": "0 jetons",
                    "total_bets": "0 jetons"
                }
            # Mettre à jour les pertes
            current_losses = convert_amount_to_float(leaderboard["users"][user_id]["total_losses"])
            leaderboard["users"][user_id]["total_losses"] = format_amount(current_losses + (total_bets / len(entries)))

        # Mettre à jour les mises
        current_bets = convert_amount_to_float(leaderboard["users"][user_id]["total_bets"])
        leaderboard["users"][user_id]["total_bets"] = format_amount(current_bets + (total_bets / len(entries)))

    # Mettre à jour les mises pour l'hôte
    if host['id'] not in leaderboard["hosts"]:
        leaderboard["hosts"][host['id']] = {
            "username": host['username'],
            "total_bets": "0 jetons",
            "total_commission": "0 jetons"  # Ajouter la clé pour la commission
        }

    current_host_bets = convert_amount_to_float(leaderboard["hosts"][host['id']]["total_bets"])
    leaderboard["hosts"][host['id']]["total_bets"] = format_amount(current_host_bets + total_bets)

    # Mettre à jour la commission de l'hôte
    current_host_commission = convert_amount_to_float(leaderboard["hosts"][host['id']]["total_commission"])
    leaderboard["hosts"][host['id']]["total_commission"] = format_amount(current_host_commission + commission)

    # Enregistrer le leaderboard mis à jour
    with open(leaderboard_file, "w") as f:
        json.dump(leaderboard, f, indent=4)

from prettytable import PrettyTable

def get_leaderboard():
    # Lire le fichier leaderboard.json
    if os.path.exists(leaderboard_file):
        with open(leaderboard_file, "r") as f:
            leaderboard = json.load(f)
    else:
        return "Le leaderboard est vide."

    # Créer un tableau PrettyTable
    table = PrettyTable()
    table.field_names = ["Pseudo", "Mise", "Gains"]

    # Trier les utilisateurs par mise
    sorted_users = sorted(
        leaderboard["users"].items(), 
        key=lambda x: convert_amount_to_float(x[1]["total_bets"]), 
        reverse=True
    )

    # Ajouter les utilisateurs au tableau
    for user_id, user_data in sorted_users:
        total_bets = user_data["total_bets"]
        total_wins = user_data["total_wins"]
        total_losses = user_data["total_losses"]

        # Calculer les gains
        gains = convert_amount_to_float(total_wins) - convert_amount_to_float(total_losses)

        # Formater le résultat des gains
        gains_display = f"{gains:.2f} jetons"  # Formater pour afficher 2 décimales

        # Ajouter la ligne au tableau sans le @ devant le pseudo
        table.add_row([user_data['username'], total_bets, gains_display])

    return f"```{table}```"  # Retourner le tableau formaté

leaderboard_file = "leaderboard.json"  # Mettez le chemin vers votre fichier ici.

def delete_leaderboard_file():
    # Vérifier si le fichier leaderboard.json existe et le supprimer
    if os.path.exists(leaderboard_file):
        os.remove(leaderboard_file)

