from replit import db
from vip import calculate_vip_tier

SERVER_MAPPING = {
    "Tiliwan1": "T1",
    "Tiliwan2": "T2", 
    "Oshimo": "O1",
    "Herdegrize": "H1",
    "Euro": "E1",
    "T1": "T1",
    "T2": "T2",
    "O1": "O1",
    "H1": "H1",
    "E1": "E1"
}

def get_highest_vip(user_id, server):
    try:
        # Charger les données depuis la DB
        server_data = db.get(f"{server}.json")
        if not server_data:
            print(f"❌ Aucune donnée trouvée pour {server}")
            return {"vip_level": 0}

        # Vérifier si l'utilisateur existe
        users = server_data.get("utilisateurs", {})
        user_data = users.get(str(user_id))

        if not user_data:
            print(f"❌ Utilisateur {user_id} non trouvé dans {server}")
            return {"vip_level": 0}

        # Calculer le niveau VIP basé sur les mises totales
        total_bets = int(user_data.get("total_bets", "0 jetons").split(" ")[0])
        print(f"💰 Mises totales pour {user_id}: {total_bets} jetons")

        # Différents seuils selon le serveur
        if server == "E1":  # Serveur Euro
            if total_bets >= 600:
                return {"vip_level": 3}
            elif total_bets >= 350:
                return {"vip_level": 2}
            elif total_bets >= 150:
                return {"vip_level": 1}
            else:
                return {"vip_level": 0}
        else:  # Autres serveurs
            if total_bets >= 15000:
                return {"vip_level": 3}
            elif total_bets >= 10000:
                return {"vip_level": 2}
            elif total_bets >= 4000:
                return {"vip_level": 1}
            else:
                return {"vip_level": 0}

    except Exception as e:
        print(f"❌ Erreur VIP: {e}")
        return {"vip_level": 0}


# Mapping des niveaux VIP et seuils
VIP_TIERS = {
    1: 4000,  # 4000 jetons
    2: 10000, # 10000 jetons
    3: 15000  # 20000 jetons
}


def format_kamas(jetons_amount, is_euro=False):
    """Convert jetons to kamas format or euro format"""
    try:
        amount = float(jetons_amount.split(' ')[0])
        if is_euro:
            return f"{amount:.2f}€"

        kamas = amount * 10000  # 1 jeton = 10k kamas
        if kamas >= 1000000:
            millions = kamas/1000000
            if millions.is_integer():
                return f"{int(millions)}M Kamas"
            return f"{millions:.1f}M Kamas"
        return f"{kamas//1000}K Kamas"
    except:
        return "0 Kamas" if not is_euro else "0.00€"

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