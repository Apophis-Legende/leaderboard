from replit import db

def format_kamas(kamas_str, is_euro=False):
    try:
        if isinstance(kamas_str, str):
            amount = float(kamas_str.split()[0])
        else:
            amount = float(kamas_str)

        if is_euro:
            return f"{amount:.2f}€"

        if amount >= 1000000:
            millions = amount/1000000
            whole = int(millions)
            decimal = int((millions - whole) * 10)
            return f"{whole}M{decimal} Kamas" if decimal else f"{whole}M Kamas"
        else:
            return f"{int(amount/1000)}K Kamas"
    except:
        return "0 Kamas"

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
            if total_bets >= 20000:
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

# Mapping des niveaux VIP et seuils
VIP_TIERS = {
    1: 4000,  # 4000 jetons
    2: 10000, # 10000 jetons
    3: 20000  # 20000 jetons
}


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