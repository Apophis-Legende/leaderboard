
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
    import json
    try:
        with open('assigned_roles.json', 'r') as f:
            data = json.load(f)
            if str(user_id) in data['users']:
                roles = data['users'][str(user_id)]['roles']
                max_vip = 0
                
                # Map server codes to full names
                server_mapping = {
                    "T1": "Tiliwan1",
                    "T2": "Tiliwan2",
                    "O1": "Oshimo",
                    "H1": "Herdegrize",
                    "E1": "Euro"
                }
                
                server_name = server_mapping.get(server, server)
                
                for role in roles:
                    if server_name in role and 'VIP' in role:
                        try:
                            vip_level = int(role.split('VIP')[1].split()[0])
                            max_vip = max(max_vip, vip_level)
                        except (IndexError, ValueError):
                            continue
                
                return f"VIP {max_vip}" if max_vip > 0 else "---"
    except Exception as e:
        print(f"Erreur VIP: {e}")
    return "---"
