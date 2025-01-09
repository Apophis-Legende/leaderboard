
import json
from vip import VIP_ROLE_MAPPING, VIP_TIERS, calculate_vip_tier, MAPPING_SERVER_FILE

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

def get_highest_vip(user_id, server):
    """Get highest VIP level for user based on VIP tiers"""
    try:
        # Charger les données du serveur depuis le mapping
        with open(MAPPING_SERVER_FILE[server], 'r') as f:
            data = json.load(f)
            if str(user_id) in data['utilisateurs']:
                user_data = data['utilisateurs'][str(user_id)]
                total_bets = int(user_data['total_bets'].split(' ')[0])
                
                # Utiliser la même logique que vip.py
                for tier, threshold in sorted(VIP_TIERS.items(), reverse=True):
                    if total_bets >= threshold:
                        # Vérifier le rôle correspondant dans VIP_ROLE_MAPPING
                        role_name = VIP_ROLE_MAPPING[tier][server]
                        if role_name:
                            return f"VIP {tier}"
                            
                return "---"
    except Exception as e:
        print(f"Erreur VIP: {e}")
    return "---"
