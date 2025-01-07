import os
import json

def load_json(filename, default_data=None):
    """
    Charge un fichier JSON ou retourne les données par défaut si le fichier n'existe pas.
    """
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    return default_data or {}

def save_json(filename, data):
    """
    Sauvegarde des données dans un fichier JSON.
    """
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"✅ Fichier sauvegardé : {filename}")

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

def process_giveaway_data(raw_data):
    """
    Traite les données brutes d'un giveaway et met à jour le fichier JSON du serveur concerné.
    Retourne un dictionnaire contenant un résumé des données mises à jour.
    """
    try:
        giveaway_info = raw_data["giveaway"]
        prize = giveaway_info["prize"]

        # Extraire le serveur et le gain
        server, gain_after_commission = prize.split(" ")
        gain_after_commission = int(gain_after_commission)

        # Calculer la mise totale avant commission
        total_bet_before_commission = int(gain_after_commission / 0.95)
        commission_total = total_bet_before_commission - gain_after_commission

        print(f"🎯 Serveur : {server}")
        print(f"💰 Gain après commission : {gain_after_commission} jetons")
        print(f"💸 Mise totale avant commission (calculée) : {total_bet_before_commission} jetons")
        print(f"💸 Commission totale : {commission_total} jetons")

        # Charger ou initialiser les données du serveur
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

        # Mise à jour des stats globales
        previous_total_bet = convert_amount_to_float(server_data["mises_totales_avant_commission"])
        server_data["mises_totales_avant_commission"] = format_amount(previous_total_bet + total_bet_before_commission)

        previous_total_gain = convert_amount_to_float(server_data["gains_totaux"])
        server_data["gains_totaux"] = format_amount(previous_total_gain + gain_after_commission)

        previous_total_commission = convert_amount_to_float(server_data["commission_totale"])
        server_data["commission_totale"] = format_amount(previous_total_commission + commission_total)

        server_data["nombre_de_jeux"] += 1

        # Mise à jour des joueurs (gagnants et perdants)
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

            # Mise à jour des gains, mises, et participation
            current_wins = convert_amount_to_float(server_data["utilisateurs"][user_id]["total_wins"])
            current_bets = convert_amount_to_float(server_data["utilisateurs"][user_id]["total_bets"])
            server_data["utilisateurs"][user_id]["total_wins"] = format_amount(current_wins + gain_after_commission)
            server_data["utilisateurs"][user_id]["total_bets"] = format_amount(current_bets + total_bet_before_commission // len(raw_data["entries"]))
            server_data["utilisateurs"][user_id]["participation"] += 1

        for entry in raw_data["entries"]:
            if entry["id"] in [winner["id"] for winner in raw_data["winners"]]:
                continue  # Ignore les gagnants ici
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

            # Mise à jour des pertes, mises, et participation
            current_losses = convert_amount_to_float(server_data["utilisateurs"][user_id]["total_losses"])
            current_bets = convert_amount_to_float(server_data["utilisateurs"][user_id]["total_bets"])
            server_data["utilisateurs"][user_id]["total_losses"] = format_amount(current_losses + total_bet_before_commission // len(raw_data["entries"]))
            server_data["utilisateurs"][user_id]["total_bets"] = format_amount(current_bets + total_bet_before_commission // len(raw_data["entries"]))
            server_data["utilisateurs"][user_id]["participation"] += 1

        # Mise à jour des hôtes
        host_id = giveaway_info["host"]["id"]
        host_username = giveaway_info["host"]["username"]

        if host_id not in server_data["hôtes"]:
            server_data["hôtes"][host_id] = {
                "username": host_username,
                "total_bets": "0 jetons",
                "total_commission": "0 jetons"
            }

        current_host_bets = convert_amount_to_float(server_data["hôtes"][host_id]["total_bets"])
        current_host_commission = convert_amount_to_float(server_data["hôtes"][host_id]["total_commission"])
        server_data["hôtes"][host_id]["total_bets"] = format_amount(current_host_bets + total_bet_before_commission)
        server_data["hôtes"][host_id]["total_commission"] = format_amount(current_host_commission + commission_total)

        # Mise à jour des croupiers
        if host_id not in server_data["croupiers"]:
            server_data["croupiers"][host_id] = {
                "username": host_username,
                "total_giveaways": 0,
                "total_kamas_managed": "0 jetons",
                "total_commission": "0 jetons"
            }

        server_data["croupiers"][host_id]["total_giveaways"] += 1
        current_kamas_managed = convert_amount_to_float(server_data["croupiers"][host_id]["total_kamas_managed"])
        current_croupier_commission = convert_amount_to_float(server_data["croupiers"][host_id]["total_commission"])
        server_data["croupiers"][host_id]["total_kamas_managed"] = format_amount(current_kamas_managed + total_bet_before_commission)
        server_data["croupiers"][host_id]["total_commission"] = format_amount(current_croupier_commission + commission_total)

        # Sauvegarder les données dans le fichier JSON du serveur
        save_json(file_name, server_data)
        print(f"✅ Données sauvegardées pour le serveur {server} dans {file_name}.")

        # Retourner un résumé des données traitées
        return {
            "server": server,
            "gain_after_commission": gain_after_commission,
            "total_bet_before_commission": total_bet_before_commission,
            "commission_total": commission_total,
        }

    except ValueError as e:
        print(f"❌ Erreur : {e}")
        return {"error": str(e)}

    except KeyError as e:
        print(f"❌ Données manquantes : {e}")
        return {"error": f"Données manquantes : {e}"}

    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
        return {"error": f"Erreur inattendue : {e}"}

