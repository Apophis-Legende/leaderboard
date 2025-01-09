import json
import os

def load_json(filename, default_data=None):
    """
    Charge un fichier JSON ou retourne les données par défaut si le fichier n'existe pas.
    """
    absolute_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    if os.path.exists(absolute_path):
        with open(absolute_path, "r", encoding="utf-8") as file:
            return json.load(file)
    return default_data or {}

def save_json(filename, data):
    """
    Sauvegarde des données dans un fichier JSON.
    """
    absolute_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(absolute_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"✅ Fichier sauvegardé : {absolute_path}")

def extract_user_data(data):
    """
    Extrait les données des utilisateurs du fichier JSON.
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
