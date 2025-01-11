
import requests
from replit import db

def convert_amount_to_int(amount_str):
    return int(amount_str.split(" ")[0])

def format_amount(amount):
    return f"{int(amount)} jetons"

def process_giveaway(link, new_prize):
    try:
        api_url = link.replace("https://giveawaybot.party/summary#", "https://summary-api.giveawaybot.party/?")
        response = requests.get(api_url)
        if response.status_code != 200:
            raise Exception(f"Impossible d'extraire les données depuis le lien")

        giveaway_data = response.json()
        if not giveaway_data or "giveaway" not in giveaway_data:
            raise Exception("Données du giveaway invalides")

        server = new_prize.split()[0]
        gain_after_commission = int(new_prize.split()[1])
        total_bet_before_commission = int(gain_after_commission / 0.95)
        commission_total = total_bet_before_commission - gain_after_commission

        server_file = f"{server}.json"
        server_data = db.get(server_file)
        if not server_data:
            server_data = {
                "serveur": server,
                "nombre_de_jeux": 0,
                "mises_totales_avant_commission": "0 jetons",
                "gains_totaux": "0 jetons",
                "commission_totale": "0 jetons",
                "utilisateurs": {},
                "hôtes": {},
                "croupiers": {}
            }

        winners = giveaway_data.get("winners", [])
        entries = giveaway_data.get("entries", [])
        entries_count = len(entries) if entries else 1

        for winner in winners:
            user_id = str(winner["id"])
            if user_id not in server_data["utilisateurs"]:
                server_data["utilisateurs"][user_id] = {
                    "username": winner["username"],
                    "total_wins": "0 jetons",
                    "total_losses": "0 jetons",
                    "total_bets": "0 jetons",
                    "participation": 0
                }

            user = server_data["utilisateurs"][user_id]
            current_wins = convert_amount_to_int(user["total_wins"])
            current_bets = convert_amount_to_int(user["total_bets"])

            user["total_wins"] = format_amount(current_wins + gain_after_commission)
            user["total_bets"] = format_amount(current_bets + total_bet_before_commission // entries_count)
            user["participation"] += 1

        for entry in entries:
            user_id = str(entry["id"])
            if user_id not in [str(w["id"]) for w in winners]:
                if user_id not in server_data["utilisateurs"]:
                    server_data["utilisateurs"][user_id] = {
                        "username": entry["username"],
                        "total_wins": "0 jetons",
                        "total_losses": "0 jetons",
                        "total_bets": "0 jetons",
                        "participation": 0
                    }

                user = server_data["utilisateurs"][user_id]
                current_losses = convert_amount_to_int(user["total_losses"])
                current_bets = convert_amount_to_int(user["total_bets"])

                user["total_losses"] = format_amount(current_losses + total_bet_before_commission // entries_count)
                user["total_bets"] = format_amount(current_bets + total_bet_before_commission // entries_count)
                user["participation"] += 1

        host = giveaway_data["giveaway"]["host"]
        host_id = str(host["id"])
        if host_id not in server_data["hôtes"]:
            server_data["hôtes"][host_id] = {
                "username": host["username"],
                "total_bets": "0 jetons",
                "total_commission": "0 jetons"
            }

        host_data = server_data["hôtes"][host_id]
        current_host_bets = convert_amount_to_int(host_data["total_bets"])
        current_host_commission = convert_amount_to_int(host_data["total_commission"])

        host_data["total_bets"] = format_amount(current_host_bets + total_bet_before_commission)
        host_data["total_commission"] = format_amount(current_host_commission + commission_total)

        server_data["nombre_de_jeux"] += 1
        current_total_bets = convert_amount_to_int(server_data["mises_totales_avant_commission"])
        current_total_gains = convert_amount_to_int(server_data["gains_totaux"])
        current_total_commission = convert_amount_to_int(server_data["commission_totale"])

        server_data["mises_totales_avant_commission"] = format_amount(current_total_bets + total_bet_before_commission)
        server_data["gains_totaux"] = format_amount(current_total_gains + gain_after_commission)
        server_data["commission_totale"] = format_amount(current_total_commission + commission_total)

        db[server_file] = server_data
        return "✅ Données modifiées et sauvegardées avec succès"

    except Exception as e:
        return f"❌ Une erreur est survenue : {str(e)}"
