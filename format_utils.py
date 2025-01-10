from replit import db

SERVER_MAPPING = {
    "Tiliwan1": "T1",
    "Tiliwan2": "T2", 
    "Oshimo": "O1",
    "Herdegrize": "H1",
    "Euro": "E1"
}

def get_highest_vip(user_id, server):
    try:
        # Convertir le nom du serveur
        server_code = SERVER_MAPPING.get(server)
        if not server_code:
            print(f"❌ Serveur {server} non trouvé dans le mapping")
            return {"error": "Serveur non reconnu"}

        # Charger les données depuis la DB
        data = db.get(f"{server_code}.json")
        if not data:
            return {"error": "Aucune donnée trouvée"}

        # Vérifier si l'utilisateur existe
        user_data = data.get("utilisateurs", {}).get(user_id)
        if not user_data:
            return {"error": "Utilisateur non trouvé"}

        # Calculer le niveau VIP basé sur les mises totales
        total_bets = int(user_data["total_bets"].split(" ")[0])

        if total_bets >= 20000:
            return {"vip_level": 3}
        elif total_bets >= 10000:
            return {"vip_level": 2}
        elif total_bets >= 4000:
            return {"vip_level": 1}
        else:
            return {"vip_level": 0}

    except Exception as e:
        print(f"Erreur VIP: {e}")
        return {"error": str(e)}

import json
from vip import calculate_vip_tier

# Mapping des niveaux VIP et seuils
VIP_TIERS = {
    1: 4000,  # 4000 jetons
    2: 10000, # 10000 jetons
    3: 20000  # 20000 jetons
}


def format_kamas(jetons_amount):
    """Convert jetons to kamas format"""
    try:
        amount = int(jetons_amount.split(' ')[0])
        kamas = amount * 10000  # 1 jeton = 10k kamas
        
        if kamas >= 1000000:
            millions = kamas/1000000
            whole = int(millions)
            decimal = int((millions - whole) * 10)
            if decimal == 0:
                return f"{whole}M Kamas"
            return f"{whole}M{decimal} Kamas"
        return f"{kamas//1000}K Kamas"
    except:
        return "0 Kamas"

def calculate_benefice(wins, total_bets):
    """Calculate total benefit (wins - total_bets)"""
    try:
        win_amount = int(wins.split(' ')[0])
        bet_amount = int(total_bets.split(' ')[0])
        total = win_amount - bet_amount
        return f"{total} jetons"
    except:
        return "0 jetons"

def calculate_vip_tier(total_bets):
    """Calculate VIP tier based on total bets"""
    for tier, threshold in sorted(VIP_TIERS.items(), reverse=True):
        if total_bets >= threshold:
            return tier
    return None