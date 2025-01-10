import os
import json
import requests

# Mapping des serveurs vers les fichiers JSON
MAPPING_SERVER_FILE = {
    "T1": "T1.json",
    "T2": "T2.json",
    "O1": "O1.json",
    "H1": "H1.json",
    "E1": "E1.json"
}

# Charger un fichier JSON local
def load_json(filename, default_data=None):
    try:
        absolute_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        with open(absolute_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return default_data or {}

# Sauvegarder un fichier JSON local
def save_json(filename, data):
    absolute_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(absolute_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"✅ Fichier sauvegardé : {absolute_path}")

# Convertir un montant "123 jetons" en entier
def convert_amount_to_int(amount_str):
    return int(amount_str.split(" ")[0])

# Convertir un montant entier en chaîne "123 jetons"
def format_amount(amount):
    return f"{int(amount)} jetons"

# Fonction principale pour traiter les données JSON extraites
def process_giveaway(link, new_prize):
    try:
        # Étape 1 : Extraire les données brutes depuis le lien
        response = requests.get(link)
        if response.status_code != 200:
            raise Exception(f"Impossible d'extraire les données depuis le lien : {link}")

        giveaway_data = response.json()
        prize = giveaway_data.get("giveaway", {}).get("prize", None)
        if not prize:
            raise Exception("Aucun `prize` trouvé dans les données extraites.")

        # Étape 2 : Extraire le serveur du prize
        server = new_prize.split()[0]  # Exemple : "T1"
        gain_after_commission = int(new_prize.split()[1])
        total_bet_before_commission = int(gain_after_commission / 0.95)
        commission_total = total_bet_before_commission - gain_after_commission

        # Trouver le fichier JSON correspondant au serveur
        filename = MAPPING_SERVER_FILE.get(server)
        if not filename:
            raise Exception(f"Le serveur `{server}` n'est pas pris en charge.")

        # Charger ou initialiser les données locales
        server_data = load_json(filename, {
            "serveur": server,
            "nombre_de_jeux": 0,
            "mises_totales_avant_commission": "0 jetons",
            "gains_totaux": "0 jetons",
            "commission_totale": "0 jetons",
            "utilisateurs": {},
            "hôtes": {},
            "croupiers": {}
        })

        # Étape 3 : Mettre à jour les utilisateurs
        winners = giveaway_data.get("winners", [])
        entries = giveaway_data.get("entries", [])

        for winner in winners:
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

            user = server_data["utilisateurs"][user_id]
            user["total_wins"] = format_amount(convert_amount_to_int(user["total_wins"]) + gain_after_commission)
            user["total_bets"] = format_amount(
                convert_amount_to_int(user["total_bets"]) + total_bet_before_commission // len(entries)
            )
            user["participation"] += 1

        for entry in entries:
            if entry["id"] in [winner["id"] for winner in winners]:
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

            user = server_data["utilisateurs"][user_id]
            user["total_losses"] = format_amount(
                convert_amount_to_int(user["total_losses"]) + total_bet_before_commission // len(entries)
            )
            user["total_bets"] = format_amount(
                convert_amount_to_int(user["total_bets"]) + total_bet_before_commission // len(entries)
            )
            user["participation"] += 1

        # Étape 4 : Mettre à jour les hôtes et croupiers
        host_id = giveaway_data["giveaway"]["host"]["id"]
        host_username = giveaway_data["giveaway"]["host"]["username"]

        if host_id not in server_data["hôtes"]:
            server_data["hôtes"][host_id] = {
                "username": host_username,
                "total_bets": "0 jetons",
                "total_commission": "0 jetons"
            }

        server_data["hôtes"][host_id]["total_bets"] = format_amount(
            convert_amount_to_int(server_data["hôtes"][host_id]["total_bets"]) + total_bet_before_commission
        )
        server_data["hôtes"][host_id]["total_commission"] = format_amount(
            convert_amount_to_int(server_data["hôtes"][host_id]["total_commission"]) + commission_total
        )

        # Étape 5 : Mettre à jour les totaux globaux
        server_data["nombre_de_jeux"] += 1
        server_data["mises_totales_avant_commission"] = format_amount(
            convert_amount_to_int(server_data["mises_totales_avant_commission"]) + total_bet_before_commission
        )
        server_data["gains_totaux"] = format_amount(
            convert_amount_to_int(server_data["gains_totaux"]) + gain_after_commission
        )
        server_data["commission_totale"] = format_amount(
            convert_amount_to_int(server_data["commission_totale"]) + commission_total
        )

        # Étape 6 : Sauvegarder les données locales
        save_json(filename, server_data)
        return f"✅ Données transformées et sauvegardées dans `{filename}`."

    except Exception as e:
        return f"❌ Une erreur est survenue : {str(e)}"