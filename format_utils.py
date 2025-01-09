
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
                # Convert server names: Tiliwan1 -> T1, etc.
                server_mapping = {
                    "Tiliwan1": "T1",
                    "Tiliwan2": "T2",
                    "Oshimo": "O1",
                    "Herdegrize": "H1",
                    "Euro": "E1"
                }
                server_code = server_mapping.get(server, server)
                
                for role in roles:
                    if server_code in role and 'VIP' in role:
                        try:
                            level = int(role.split(' ')[1])
                            max_vip = max(max_vip, level)
                        except (IndexError, ValueError):
                            continue
                return f"VIP {max_vip}" if max_vip > 0 else "---"
    except:
        pass
    return "---"
