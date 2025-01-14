from replit import db
from datetime import datetime, timedelta
import time
from format_utils import format_kamas
from config import COMMISSION_CHANNELS



def get_today_timestamp():
    """Retourne le timestamp de minuit du jour actuel"""
    now = datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight.timestamp()

def save_daily_leaderboard(server, giveaway_data=None):
    """Sauvegarde le leaderboard du jour avec les détails du dernier giveaway"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        server_data = db.get(f"{server}.json", {})

        # Récupérer la commission totale avant réinitialisation
        commission_totale = server_data.get("commission_totale", "0 jetons")
        if isinstance(commission_totale, str):
            commission_totale = int(commission_totale.split()[0])

        # Structure pour les données journalières
        daily_data = {
            "date": today,
            "serveur": server,
            "nombre_de_jeux": server_data.get("nombre_de_jeux", 0),
            "commissions": {
                "total": commission_totale,
                "details": []
            },
            "host": {
                "id": None,
                "username": None
            } if not giveaway_data else {
                "id": giveaway_data["giveaway"]["host"]["id"],
                "username": giveaway_data["giveaway"]["host"]["username"]
            }
        }

        # Réinitialiser la commission dans les données du serveur
        server_data["commission_totale"] = "0 jetons"
        db[f"{server}.json"] = server_data

        # Ajouter les détails du nouveau giveaway s'il existe
        if giveaway_data and "giveaway" in giveaway_data:
            prize_info = giveaway_data["giveaway"]["prize"].split()
            if len(prize_info) >= 2:
                gain = int(prize_info[1])
                bet = int(gain / 0.95)
                commission = bet - gain

                giveaway_detail = {
                    "timestamp": datetime.now().timestamp(),
                    "host": {
                        "id": giveaway_data["giveaway"]["host"]["id"],
                        "username": giveaway_data["giveaway"]["host"]["username"]
                    },
                    "prize": gain,
                    "bet": bet,
                    "commission": commission,
                    "server": server
                }
                daily_data["commissions"]["details"].append(giveaway_detail)

        # Récupérer l'historique existant ou créer un nouveau
        history_key = f"LB/{server}/{today}"

        # Structure pour le leaderboard quotidien
        lb_data = {
            "date": today,
            "serveur": server,
            "nombre_de_jeux": server_data.get("nombre_de_jeux", 0),
            "mises_totales_avant_commission": server_data.get("mises_totales_avant_commission", "0 jetons"),
            "gains_totaux": server_data.get("gains_totaux", "0 jetons"), 
            "commission_totale": server_data.get("commission_totale", "0 jetons"),
            "utilisateurs": server_data.get("utilisateurs", {}),
            "hôtes": server_data.get("hôtes", {}),
            "croupiers": server_data.get("croupiers", {})
        }

        db[history_key] = lb_data

        # Récupérer l'historique existant ou utiliser les nouvelles données
        history_key = f"COMMISSION/{server}/{today}"
        existing_data = db.get(history_key, daily_data)

        # Fusionner les nouvelles données avec l'existant
        if giveaway_data:
            if "commissions" not in existing_data:
                existing_data["commissions"] = {"total": 0, "details": []}
            existing_data["commissions"]["total"] = daily_data["commissions"]["total"]
            if giveaway_data and "details" in daily_data["commissions"]:
                existing_data["commissions"]["details"].extend(daily_data["commissions"]["details"])

        # Sauvegarder dans la DB
        db[history_key] = existing_data

        print(f"✅ Commissions sauvegardées pour {server} - {today}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde du leaderboard: {e}")
        return False

def calculate_daily_commissions(server):
    """Calcule les commissions journalières pour un serveur"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        server_data = db.get(f"LB/{server}/{today}", {})
        if not server_data:
            return {
                "date": get_today_timestamp(),
                "total": 0,
                "croupiers": {}
            }

        croupiers = server_data.get("croupiers", {})
        today = get_today_timestamp()
        daily_commissions = {
            "date": today,
            "total": 0,
            "croupiers": {}
        }

        # Calculer les commissions pour l'hôte
        host_data = server_data.get("hôtes", {})
        for host_id, data in host_data.items():
            commission = data.get("total_commission", "0 jetons")
            if isinstance(commission, str):
                amount = int(commission.split()[0])
                # 40% pour le croupier
                croupier_share = int(amount * 0.40)
                # 10% pour l'investissement 
                investment_share = int(amount * 0.10)
                # 50% pour les VIP (géré par commission_calculator.py)

                # Sauvegarder la part investissement
                if "investment_share" not in server_data:
                    server_data["investment_share"] = "0 jetons"
                current_investment = int(server_data["investment_share"].split()[0])
                server_data["investment_share"] = f"{current_investment + investment_share} jetons"

                # Formatter le montant selon le serveur
                if server == "E1":
                    formatted_amount = f"{croupier_share:.2f}€"
                else:
                    kamas = croupier_share * 10000
                    if kamas >= 1000000:
                        millions = kamas/1000000
                        whole = int(millions)
                        decimal = int((millions - whole) * 10)
                        formatted_amount = f"{whole}M{decimal} Kamas" if decimal else f"{whole}M Kamas"
                    else:
                        formatted_amount = f"{kamas//1000}K Kamas"

                daily_commissions["croupiers"][host_id] = {
                    "username": data.get("username", "Unknown"),
                    "commission": croupier_share if server != "E1" else f"{croupier_share:.2f}",
                    "formatted_commission": formatted_amount,
                    "role": data.get("role", "standard")
                }
                daily_commissions["total"] += croupier_share

        # Sauvegarder l'historique détaillé
        history_key = f"{server}_commission_history"
        commission_history_key = f"{server}_croupier_details"

        history = db.get(history_key, {})
        commission_details = db.get(commission_history_key, {})

        # Sauvegarder l'historique standard
        history[str(today)] = daily_commissions
        db[history_key] = history

        # Sauvegarder les détails des croupiers
        for croupier_id, data in daily_commissions["croupiers"].items():
            if croupier_id not in commission_details:
                commission_details[croupier_id] = {
                    "username": data["username"],
                    "total_commission": 0,
                    "commission_history": {},
                    "servers": {}
                }

            # Mettre à jour les totaux
            commission_details[croupier_id]["total_commission"] += data["commission"]

            # Ajouter l'historique par date
            if str(today) not in commission_details[croupier_id]["commission_history"]:
                commission_details[croupier_id]["commission_history"][str(today)] = {}

            commission_details[croupier_id]["commission_history"][str(today)][server] = {
                "commission": data["commission"],
                "formatted_commission": data["formatted_commission"]
            }

            # Mettre à jour les stats par serveur
            if server not in commission_details[croupier_id]["servers"]:
                commission_details[croupier_id]["servers"][server] = 0
            commission_details[croupier_id]["servers"][server] += data["commission"]

        db[commission_history_key] = commission_details

        # Sauvegarder le leaderboard du jour avant réinitialisation
        save_daily_leaderboard(server)

        # Réinitialiser les commissions journalières
        for croupier in croupiers.values():
            croupier["daily_commission"] = "0 jetons"
        db[f"{server}.json"] = server_data

        return daily_commissions

    except Exception as e:
        print(f"❌ Erreur lors du calcul des commissions pour {server}: {e}")
        return None

def get_commission_history(server, days=7):
    """Récupère l'historique des commissions sur X jours"""
    today = datetime.now().strftime('%Y-%m-%d')
    history_key = f"LB/{server}/{today}"
    history = db.get(history_key, {})

    today = get_today_timestamp()
    start_date = today - (days * 86400)  # 86400 secondes = 1 jour

    filtered_history = {}
    for timestamp, data in history.items():
        if float(timestamp) >= start_date:
            filtered_history[timestamp] = data

    return filtered_history

def add_commission(server, croupier_id, amount, role="standard"):
    """Ajoute une commission pour un croupier"""
    try:
        server_data = db.get(f"{server}.json", {})
        if not server_data:
            server_data = {
                "serveur": server,
                "croupiers": {}
            }

        croupiers = server_data.get("croupiers", {})
        if croupier_id not in croupiers:
            croupiers[croupier_id] = {
                "username": "Unknown",
                "daily_commission": "0 jetons",
                "role": role
            }

        current = int(croupiers[croupier_id]["daily_commission"].split()[0])
        print(f"Ajout de {amount} jetons à {croupier_id}, ancien total: {current} jetons")
        croupiers[croupier_id]["daily_commission"] = f"{current + int(amount)} jetons"

        server_data["croupiers"] = croupiers
        db[f"{server}.json"] = server_data
        print(f"Commission mise à jour pour {croupier_id}: {croupiers[croupier_id]['daily_commission']}")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de l'ajout de la commission: {e}")
        return False