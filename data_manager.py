
from replit import db

def list_all_data():
    """Liste toutes les données dans Replit DB"""
    print("📂 Contenu de Replit DB :")
    for key in db.keys():
        print(f"🔑 {key}")
        try:
            data = dict(db[key])
            print(f"📄 {data}")
        except Exception as e:
            print(f"❌ Erreur de lecture pour {key}: {e}")

def load_json(filename, default_data=None):
    """Charge les données depuis Replit DB"""
    server_name = filename.replace('.json', '')
    if default_data is None:
        default_data = {
            "serveur": server_name,
            "nombre_de_jeux": 0,
            "mises_totales_avant_commission": "0 jetons",
            "gains_totaux": "0 jetons",
            "commission_totale": "0 jetons",
            "utilisateurs": {},
            "hôtes": {},
            "croupiers": {}
        }
    
    try:
        data = db.get(server_name)
        if data is None:
            print(f"📝 Initialisation des données pour {server_name}")
            db[server_name] = default_data
            return default_data
        return dict(data)
    except Exception as e:
        print(f"❌ Erreur de lecture DB pour {server_name}: {e}")
        return default_data

def save_json(filename, data):
    """Sauvegarde les données dans Replit DB"""
    server_name = filename.replace('.json', '')
    try:
        db[server_name] = dict(data)
        print(f"✅ Données sauvegardées pour {server_name}")
    except Exception as e:
        print(f"❌ Erreur de sauvegarde DB pour {server_name}: {e}")
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
