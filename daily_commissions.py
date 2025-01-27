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
    try:
        data = db.get(key)
        if data is None:
            data = {
                "date": today,
                "serveur": server,
                "croupiers": {},
                "total": 0,
                "details": []
            }
            db[key] = data
        return data
    except Exception as e:
        print(f"❌ Erreur lors de la lecture des données LB : {e}")
        return None


def save_daily_data(server, data, today=None):
    """Sauvegarde les données journalières pour un serveur donné."""
    if not today:
        today = datetime.now().strftime('%Y-%m-%d')
    key = f"LB/{server}/{today}"
    try:
        if isinstance(data, dict):
            db[key] = data
            print(f"✅ Données sauvegardées pour {key}")
            return True
        else:
            print(f"❌ Format de données invalide pour {key}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde des données LB : {e}")
        return False


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
        history_key = f"LB/{server}/{today}"
        print(f"🔍 Tentative de lecture des données pour {history_key}")

        server_data = db.get(history_key)
        if server_data is None:
            print(f"⚠️ Aucune donnée trouvée pour {history_key}")
            default_data = {
                "date": get_today_timestamp(),
                "total": 0,
                "croupiers": {}
            }
            db[history_key] = default_data
            return default_data

        print(f"✅ Données trouvées pour {history_key}: {server_data}")

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
                    commission_parts = commission.split()
                    if not commission_parts:
                        print(f"⚠️ Format de commission invalide: {commission}")
                        continue

                    amount = float(commission_parts[0])
                    print(f"✅ Montant extrait: {amount}")

                    # Répartition des commissions
                    total_amount = float(amount)
                    vip_share = total_amount * 0.50
                    investment_share = total_amount * 0.10
                    croupier_share = total_amount * 0.40

                except (ValueError, IndexError) as e:
                    print(f"❌ Erreur lors de l'extraction du montant: {e}")
                    continue

                # Ajouter les commissions calculées aux données journalières
                daily_commissions["croupiers"][host_id] = {
                    "username": data.get("username", "Unknown"),
                    "commission": f"{croupier_share:.2f}",
                    "role": data.get("role", "standard")
                }
                daily_commissions["total"] += croupier_share

        # Sauvegarder dans LB/{server}/{today}
        db[history_key] = daily_commissions
        print(f"✅ Commissions calculées pour {server} - {today}")
        return daily_commissions

    except Exception as e:
        print(f"❌ Erreur lors du calcul des commissions pour {server}: {e}")
        return None


def extract_commission_data(data):
    """Extrait les données de commission"""
    try:
        commission_data = {
            "total": 0,
            "croupiers": {},
            "details": []
        }

        # Extraction des données des croupiers
        for host_id, host_data in data.get("hôtes", {}).items():
            commission = host_data.get("total_commission", "0 jetons")
            if isinstance(commission, str):
                try:
                    amount = float(commission.split()[0])
                    commission_data["croupiers"][host_id] = {
                        "username": host_data.get("username", "Unknown"),
                        "commission": amount,
                        "role": host_data.get("role", "standard")
                    }
                    commission_data["total"] += amount
                except ValueError:
                    print(f"❌ Erreur de conversion pour la commission de {host_id}")

        # Extraction des détails
        commission_data["details"] = data.get("commissions", {}).get("details", [])

        return commission_data
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction des données de commission : {e}")
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


