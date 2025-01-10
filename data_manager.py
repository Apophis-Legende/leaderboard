
from replit import db

def load_json(filename, default_data=None):
    """
    Charge les données depuis Replit DB avec une valeur par défaut
    """
    if default_data is None:
        default_data = {}
    try:
        if filename in db:
            return db[filename]
        db[filename] = default_data
        return default_data
    except Exception as e:
        print(f"❌ Erreur lors du chargement des données {filename}: {e}")
        return default_data

def save_json(filename, data):
    """
    Sauvegarde les données dans Replit DB
    """
    try:
        db[filename] = data
        print(f"✅ Données sauvegardées pour : {filename}")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde des données {filename}: {e}")
        raise

def extract_user_data(data):
    """
    Extrait les données des utilisateurs
    """
    users = data.get("utilisateurs", {})
    user_info = []

    for user_id, user_data in users.items():
        user_info.append({
            "user_id": user_id,
            "username": user_data["username"],
            "total_wins": user_data["total_wins"],
            "total_losses": user_data["total_losses"],
            "total_bets": user_data["total_bets"],
            "participation": user_data["participation"]
        })

    return user_info
