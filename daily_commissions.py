
from replit import db
from datetime import datetime, timedelta
import time

def get_today_timestamp():
    """Retourne le timestamp de minuit du jour actuel"""
    now = datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight.timestamp()

def calculate_daily_commissions(server):
    """Calcule les commissions journalières pour un serveur"""
    try:
        server_data = db.get(f"{server}.json", {})
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

        # Calculer les commissions pour chaque croupier
        for croupier_id, data in croupiers.items():
            commission = data.get("daily_commission", "0 jetons")
            if isinstance(commission, str):
                amount = int(commission.split()[0])
                daily_commissions["croupiers"][croupier_id] = {
                    "username": data.get("username", "Unknown"),
                    "commission": amount
                }
                daily_commissions["total"] += amount

        # Sauvegarder l'historique
        history_key = f"{server}_commission_history"
        history = db.get(history_key, {})
        history[str(today)] = daily_commissions
        db[history_key] = history

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
    history_key = f"{server}_commission_history"
    history = db.get(history_key, {})
    
    today = get_today_timestamp()
    start_date = today - (days * 86400)  # 86400 secondes = 1 jour
    
    filtered_history = {}
    for timestamp, data in history.items():
        if float(timestamp) >= start_date:
            filtered_history[timestamp] = data
            
    return filtered_history

def add_commission(server, croupier_id, amount):
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
                "daily_commission": "0 jetons"
            }

        current = int(croupiers[croupier_id]["daily_commission"].split()[0])
        croupiers[croupier_id]["daily_commission"] = f"{current + amount} jetons"
        
        server_data["croupiers"] = croupiers
        db[f"{server}.json"] = server_data
        return True

    except Exception as e:
        print(f"❌ Erreur lors de l'ajout de la commission: {e}")
        return False
