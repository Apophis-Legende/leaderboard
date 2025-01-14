
from replit import db
from datetime import datetime, timedelta
import time
from format_utils import format_kamas

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
        
        # Créer une copie des données du jour
        daily_data = {
            "date": today,
            "serveur": server,
            "nombre_de_jeux": server_data.get("nombre_de_jeux", 0),
            "mises_totales_avant_commission": server_data.get("mises_totales_avant_commission", "0 jetons"),
            "gains_totaux": server_data.get("gains_totaux", "0 jetons"),
            "commission_totale": server_data.get("commission_totale", "0 jetons"),
            "utilisateurs": server_data.get("utilisateurs", {}),
            "hôtes": server_data.get("hôtes", {}),
            "croupiers": server_data.get("croupiers", {}),
            "giveaways": []
        }
        
        # Récupérer l'historique existant ou créer un nouveau
        history_key = f"LB/{server}/{today}"
        existing_data = db.get(history_key, daily_data)
        
        # Ajouter le nouveau giveaway s'il existe
        if giveaway_data:
            if "giveaways" not in existing_data:
                existing_data["giveaways"] = []
            existing_data["giveaways"].append({
                "timestamp": datetime.now().timestamp(),
                "prize": giveaway_data["giveaway"]["prize"],
                "host": giveaway_data["giveaway"]["host"]["username"],
                "winners": [w["username"] for w in giveaway_data.get("winners", [])],
                "entries_count": len(giveaway_data.get("entries", [])),
            })
        
        # Sauvegarder dans la DB
        db[history_key] = existing_data
        
        print(f"✅ Leaderboard sauvegardé pour {server} - {today}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde du leaderboard: {e}")
        return False

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
                is_euro = server == "E1"
                formatted_amount = format_kamas(str(croupier_share), is_euro)
                
                daily_commissions["croupiers"][croupier_id] = {
                    "username": data.get("username", "Unknown"),
                    "commission": croupier_share,
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
    history_key = f"{server}_commission_history"
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
        croupiers[croupier_id]["daily_commission"] = f"{current + int(amount)} jetons"
        
        server_data["croupiers"] = croupiers
        db[f"{server}.json"] = server_data
        return True

    except Exception as e:
        print(f"❌ Erreur lors de l'ajout de la commission: {e}")
        return False
