import os
import json

# Charger un fichier JSON
def load_json(filename, default_data=None):
    absolute_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    if os.path.exists(absolute_path):
        with open(absolute_path, "r", encoding="utf-8") as file:
            return json.load(file)
    return default_data or {}

# Sauvegarder un fichier JSON
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

# Ajouter les données d'un giveaway
def add_giveaway_data(link, mapping_server_file):
    import requests  # Import ici pour éviter les conflits dans d'autres fichiers

    try:
        # Étape 1 : Récupérer les données depuis le lien
        response = requests.get(link)
        if response.status_code != 200:
            print(f"⚠️ Impossible de récupérer les données depuis le lien {link}.")
            return

        giveaway_data = response.json()
        prize = giveaway_data.get("giveaway", {}).get("prize", "")
        if not prize:
            print("⚠️ Le lien ne contient pas les informations nécessaires.")
            return

        # Étape 2 : Identifier le serveur et le fichier JSON
        server = prize.split()[0]  # Exemple : "E1", "T1"
        filename = mapping_server_file.get(server)
        if not filename:
            print(f"⚠️ Le serveur {server} n'est pas pris en charge.")
            return

        # Charger les données existantes
        server_data = load_json(filename, {
            "utilisateurs": {},
            "hôtes": {},
            "croupiers": {},
            "nombre_de_jeux": 0,
            "mises_totales_avant_commission": "0 jetons",
            "gains_totaux": "0 jetons",
            "commission_totale": "0 jetons",
        })

        # Étape 3 : Extraire les informations de gain et participation
        winners = giveaway_data.get("winners", [])
        entries = giveaway_data.get("entries", [])
        gain_after_commission = int(prize.split()[1])  # Exemple : "190" dans "E1 190"
        total_bet_before_commission = int(gain_after_commission / 0.95)
        commission_total = total_bet_before_commission - gain_after_commission

        # Étape 4 : Ajouter les données pour chaque utilisateur
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

            # Mise à jour des gains
            user = server_data["utilisateurs"][user_id]
            user["total_wins"] = format_amount(convert_amount_to_int(user["total_wins"]) + gain_after_commission)
            user["total_bets"] = format_amount(
                convert_amount_to_int(user["total_bets"]) + total_bet_before_commission // len(entries)
            )
            user["participation"] += 1

        for entry in entries:
            if entry["id"] in [winner["id"] for winner in winners]:
                continue  # Ignorer les gagnants
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

            # Mise à jour des pertes
            user = server_data["utilisateurs"][user_id]
            user["total_losses"] = format_amount(
                convert_amount_to_int(user["total_losses"]) + total_bet_before_commission // len(entries)
            )
            user["total_bets"] = format_amount(
                convert_amount_to_int(user["total_bets"]) + total_bet_before_commission // len(entries)
            )
            user["participation"] += 1

        # Étape 5 : Ajouter les données des hôtes et croupiers
        host_id = giveaway_data["giveaway"]["host"]["id"]
        host_username = giveaway_data["giveaway"]["host"]["username"]

        if host_id not in server_data["hôtes"]:
            server_data["hôtes"][host_id] = {
                "username": host_username,
                "total_bets": "0 jetons",
                "total_commission": "0 jetons"
            }

        host = server_data["hôtes"][host_id]
        host["total_bets"] = format_amount(convert_amount_to_int(host["total_bets"]) + total_bet_before_commission)
        host["total_commission"] = format_amount(convert_amount_to_int(host["total_commission"]) + commission_total)

        if host_id not in server_data["croupiers"]:
            server_data["croupiers"][host_id] = {
                "username": host_username,
                "total_giveaways": 0,
                "total_kamas_managed": "0 jetons",
                "total_commission": "0 jetons"
            }

        croupier = server_data["croupiers"][host_id]
        croupier["total_giveaways"] += 1
        croupier["total_kamas_managed"] = format_amount(
            convert_amount_to_int(croupier["total_kamas_managed"]) + total_bet_before_commission
        )
        croupier["total_commission"] = format_amount(
            convert_amount_to_int(croupier["total_commission"]) + commission_total
        )

        # Étape 6 : Ajouter les données globales
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

        # Étape 7 : Sauvegarder les données
        save_json(filename, server_data)
        print(f"✅ Les données ont été ajoutées au fichier {filename}.")

    except Exception as e:
        print(f"❌ Une erreur est survenue : {e}")