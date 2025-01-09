
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
    """Get highest VIP level for user"""
    from vip import VIP_ROLE_MAPPING
    import json
    try:
        with open('assigned_roles.json', 'r') as f:
            data = json.load(f)
            if str(user_id) in data['users']:
                roles = data['users'][str(user_id)]['roles']
                max_vip = 0
                
                # Vérifier chaque niveau VIP en commençant par le plus haut
                for vip_level in [3, 2, 1]:
                    role_name = VIP_ROLE_MAPPING[vip_level][server]
                    if role_name in roles:
                        return f"VIP {vip_level}"
                
                return "---"
    except Exception as e:
        print(f"Erreur VIP: {e}")
    return "---"
