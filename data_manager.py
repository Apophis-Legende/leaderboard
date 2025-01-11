from replit import db
import time

MAX_RETRIES = 3
RETRY_DELAY = 2

def verify_db_connection():
    """Vérifie la connexion à Replit DB avec retries"""
    for attempt in range(MAX_RETRIES):
        try:
            db["test_connection"] = True
            del db["test_connection"]
            return True
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"⚠️ Tentative {attempt + 1}/{MAX_RETRIES} échouée: {e}")
                time.sleep(RETRY_DELAY)
            else:
                print(f"❌ Erreur de connexion à Replit DB après {MAX_RETRIES} tentatives: {e}")
                return False

def load_json(filename, default_data=None):
    """Charge les données depuis Replit DB avec retries"""
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
    
    for attempt in range(MAX_RETRIES):
        try:
            data = db.get(server_name)
            if data is None:
                print(f"📝 Initialisation des données pour {server_name}")
                db[server_name] = default_data
                return default_data
            return dict(data)
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"⚠️ Tentative {attempt + 1}/{MAX_RETRIES} échouée: {e}")
                time.sleep(RETRY_DELAY)
            else:
                print(f"❌ Erreur de lecture DB pour {server_name} après {MAX_RETRIES} tentatives: {e}")
                return default_data

def save_json(filename, data):
    """Sauvegarde les données dans Replit DB avec retries"""
    server_name = filename.replace('.json', '')
    for attempt in range(MAX_RETRIES):
        try:
            db[server_name] = dict(data)
            print(f"✅ Données sauvegardées pour {server_name}")
            return True
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"⚠️ Tentative {attempt + 1}/{MAX_RETRIES} échouée: {e}")
                time.sleep(RETRY_DELAY)
            else:
                print(f"❌ Erreur de sauvegarde DB pour {server_name} après {MAX_RETRIES} tentatives: {e}")
                raise

def list_all_data():
    """Liste toutes les données dans Replit DB avec retries"""
    if not verify_db_connection():
        print("❌ Impossible d'accéder à Replit DB")
        return
        
    print("📂 Contenu de Replit DB :")
    for key in db.keys():
        for attempt in range(MAX_RETRIES):
            try:
                data = dict(db[key])
                print(f"🔑 {key}")
                print(f"📄 {data}")
                break
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    print(f"⚠️ Tentative {attempt + 1}/{MAX_RETRIES} échouée pour {key}: {e}")
                    time.sleep(RETRY_DELAY)
                else:
                    print(f"❌ Erreur de lecture pour {key} après {MAX_RETRIES} tentatives: {e}")

def extract_user_data(data):
    """Extrait les données des utilisateurs"""
    users = data.get("utilisateurs", {})
    user_info = []

    for user_id, user_data in users.items():
        try:
            user_info.append({
                "user_id": user_id,
                "username": user_data["username"],
                "total_wins": user_data["total_wins"],
                "total_losses": user_data["total_losses"],
                "total_bets": user_data["total_bets"],
                "participation": user_data["participation"]
            })
        except Exception as e:
            print(f"❌ Erreur lors de l'extraction des données pour l'utilisateur {user_id}: {e}")
            continue

    return user_info
