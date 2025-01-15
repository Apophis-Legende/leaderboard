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


def get_daily_data(server, today=None):
    """Récupère les données journalières pour un serveur donné."""
    if not today:
        today = datetime.now().strftime('%Y-%m-%d')
    key = f"LB/{server}/{today}"
    return db.get(key, {
        "date": today,
        "serveur": server,
        "croupiers": {},
        "hôtes": {},
        "nombre_de_jeux": 0,
        "commission_totale": "0 jetons",
        "mises_totales_avant_commission": "0 jetons",
        "gains_totaux": "0 jetons"
    })


def save_daily_data(server, data, today=None):
    """Sauvegarde les données journalières pour un serveur donné."""
    if not today:
        today = datetime.now().strftime('%Y-%m-%d')
    key = f"LB/{server}/{today}"
    db[key] = data


def save_daily_leaderboard(server, giveaway_data=None):
    """Sauvegarde le leaderboard du jour avec les détails du dernier giveaway"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        server_data = get_daily_data(server)

        # Récupérer la commission totale avant réinitialisation
        commission_totale = server_data.get("commission_totale", "0 jetons")
        if isinstance(commission_totale, str):
            commission_totale = int(commission_totale.split()[0])

        # Ajouter les détails du nouveau giveaway s'il existe
        if giveaway_data and "giveaway" in giveaway_data:
            prize_info = giveaway_data["giveaway"]["prize"].split()
            if len(prize_info) >= 2:
                gain = int(prize_info[1])
                bet = int(gain / 0.95)
                commission = bet - gain

                giveaway_detail = {
                    "timestamp": datetime.now().timestamp(),
                    "host": giveaway_data["giveaway"]["host"],
                    "prize": gain,
                    "bet": bet,
                    "commission": commission,
                    "server": server
                }
                server_data.setdefault("commissions", {}).setdefault("details", []).append(giveaway_detail)

        # Réinitialiser les données spécifiques du jour
        server_data["commission_totale"] = "0 jetons"
        save_daily_data(server, server_data)
        print(f"✅ Commissions sauvegardées pour {server} - {today}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde du leaderboard: {e}")
        return False


def calculate_daily_commissions(server):
    """Calcule les commissions journalières pour un serveur"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        history_key = f"LB/{server}/{today}"  # Utilisation de LB/{server}/{today}
        server_data = db.get(history_key, {})
        if not server_data:
            return {
                "date": get_today_timestamp(),
                "total": 0,
                "croupiers": {}
            }

        croupiers = server_data.get("croupiers", {})
        today_timestamp = get_today_timestamp()
        daily_commissions = {
            "date": today_timestamp,
            "total": 0,
            "croupiers": {}
        }

        # Calculer les commissions pour chaque hôte
        host_data = server_data.get("hôtes", {})
        for host_id, data in host_data.items():
            commission = data.get("total_commission", "0 jetons")
            if isinstance(commission, str):
                try:
                    # Extraction du montant numérique
                    amount = float(commission.split()[0])

                    # Répartition des commissions
                    croupier_share = float(amount * 0.40)  # 40% pour le croupier
                    investment_share = float(amount * 0.10)  # 10% pour l'investissement
                    # Note: Les 50% restants sont pour les VIP

                except ValueError:
                    amount = 0
                    croupier_share = 0
                    investment_share = 0

                # 50% pour les VIP (géré par commission_calculator.py)

                # Sauvegarder la part investissement
                if "investment_share" not in server_data:
                    server_data["investment_share"] = "0 jetons"
                if server == "E1":
                    current_investment = float(server_data["investment_share"].split()[0])
                    server_data["investment_share"] = f"{current_investment + investment_share:.2f} jetons"
                else:
                    current_investment = int(server_data["investment_share"].split()[0])
                    server_data["investment_share"] = f"{current_investment + investment_share} jetons"

                # Formatter le montant selon le serveur
                if server == "E1":
                    formatted_amount = f"{croupier_share:.2f}€"
                else:
                    kamas = croupier_share * 10000
                    if kamas >= 1000000:
                        millions = kamas / 1000000
                        whole = int(millions)
                        decimal = int((millions - whole) * 10)
                        formatted_amount = f"{whole}M{decimal} Kamas" if decimal else f"{whole}M Kamas"
                    else:
                        formatted_amount = f"{kamas // 1000}K Kamas"

                # Formatage spécial pour E1
                if server == "E1":
                    display_commission = f"{croupier_share:.2f}"
                    formatted_amount = f"{croupier_share:.2f}€"
                else:
                    display_commission = str(croupier_share)
                    kamas = croupier_share * 10000
                    if kamas >= 1000000:
                        millions = kamas / 1000000
                        whole = int(millions)
                        decimal = int((millions - whole) * 10)
                        formatted_amount = f"{whole}M{decimal} Kamas" if decimal else f"{whole}M Kamas"
                    else:
                        formatted_amount = f"{kamas // 1000}K Kamas"

                # Ajouter les commissions calculées aux données journalières
                daily_commissions["croupiers"][host_id] = {
                    "username": data.get("username", "Unknown"),
                    "commission": display_commission,
                    "formatted_commission": formatted_amount,
                    "role": data.get("role", "standard")
                }
                daily_commissions["total"] += float(croupier_share)

        # Sauvegarder dans LB/{server}/{today}
        db[history_key] = daily_commissions

        # Réinitialiser les commissions journalières pour les croupiers
        for croupier in croupiers.values():
            croupier["daily_commission"] = "0 jetons"
        db[history_key] = server_data

        print(f"✅ Commissions calculées pour {server} - {today}")
        return daily_commissions

    except Exception as e:
        print(f"❌ Erreur lors du calcul des commissions pour {server}: {e}")
        return None



def add_commission(server, croupier_id, amount, role="standard"):
    """Ajoute une commission pour un croupier"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        server_data = get_daily_data(server)

        croupiers = server_data.setdefault("croupiers", {})
        if croupier_id not in croupiers:
            croupiers[croupier_id] = {"username": "Unknown", "daily_commission": "0 jetons", "role": role}

        current = float(croupiers[croupier_id]["daily_commission"].split()[0])
        croupiers[croupier_id]["daily_commission"] = f"{current + float(amount)} jetons"

        save_daily_data(server, server_data)
        print(f"✅ Commission ajoutée pour {croupier_id}: {croupiers[croupier_id]['daily_commission']}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout de la commission: {e}")
        return False


def get_commission_history(server, days=7):
    """Récupère l'historique des commissions sur X jours"""
    history = {}
    today = datetime.now()
    for i in range(days):
        date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        daily_data = get_daily_data(server, date)
        history[date] = daily_data
    return history


