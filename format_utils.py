
import json
from vip import calculate_vip_tier

# Mapping des niveaux VIP et seuils
VIP_TIERS = {
    1: 4000,  # 4000 jetons
    2: 10000, # 10000 jetons
    3: 20000  # 20000 jetons
}

# Mapping des fichiers serveur
MAPPING_SERVER_FILE = {
    "T1": "T1.json",
    "T2": "T2.json", 
    "O1": "O1.json",
    "H1": "H1.json",
    "E1": "E1.json"
}

def format_kamas(jetons_amount):
    """Convert jetons to kamas format"""
    try:
        amount = int(jetons_amount.split(' ')[0])
        kamas = amount * 10000  # 1 jeton = 10k kamas
        
        if kamas >= 1000000:
            return f"{kamas/1000000:.1f}M Kamas".replace('.0M', 'M')
        return f"{kamas//1000}K Kamas"
    except:
        return "0 Kamas"

def calculate_benefice(wins, losses):
    """Calculate total benefit"""
    try:
        win_amount = int(wins.split(' ')[0])
        loss_amount = int(losses.split(' ')[0])
        total = win_amount - loss_amount
        return f"{total} jetons"
    except:
        return "0 jetons"

def calculate_vip_tier(total_bets):
    """Calculate VIP tier based on total bets"""
    for tier, threshold in sorted(VIP_TIERS.items(), reverse=True):
        if total_bets >= threshold:
            return tier
    return None

def get_highest_vip(user_id, server):
    """Get highest VIP level for user"""
    try:
        with open(MAPPING_SERVER_FILE[server], 'r') as f:
            data = json.load(f)
            if str(user_id) in data['utilisateurs']:
                user_data = data['utilisateurs'][str(user_id)]
                total_bets = int(user_data['total_bets'].split(' ')[0])
                
                vip_tier = calculate_vip_tier(total_bets)
                return f"VIP {vip_tier}" if vip_tier else "---"
    except Exception as e:
        print(f"Erreur VIP: {e}")
    return "---"
