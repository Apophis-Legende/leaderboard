
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
    "Tiliwan1": "T1.json",
    "Tiliwan2": "T2.json",
    "Oshimo": "O1.json",
    "Herdegrize": "H1.json",
    "Euro": "E1.json"
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

def get_highest_vip(user_id, server):
    """Get highest VIP level for user"""
    try:
        # Mapping direct des serveurs
        file_mapping = {
            "Tiliwan1": "T1.json",
            "Tiliwan2": "T2.json",
            "Oshimo": "O1.json",
            "Herdegrize": "H1.json",
            "Euro": "E1.json"
        }
        
        # Obtenir le bon fichier JSON
        file_name = file_mapping.get(server)
        if not file_name:
            print(f"❌ Serveur non reconnu: {server}")
            return {'vip1': '0 jetons', 'vip2': '0 jetons', 'vip3': '0 jetons', 'total': '0 jetons'}

        print(f"📂 Lecture du fichier: {file_name}")
            
        # Lire le fichier JSON
        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Obtenir la commission totale
        commission_str = data.get('commission_totale', '0 jetons')
        commission_totale = int(commission_str.split()[0])
        print(f"💰 Commission totale: {commission_totale} jetons")
            
        # Calculer la redistribution (50% de la commission totale)
        redistribution = commission_totale // 2
        print(f"🔄 Montant à redistribuer: {redistribution} jetons")
            
        # Calculer les parts VIP
        vip1 = int(redistribution * 0.2)  # 20% pour VIP 1
        vip2 = int(redistribution * 0.3)  # 30% pour VIP 2
        vip3 = int(redistribution * 0.5)  # 50% pour VIP 3
            
        return {
            'vip1': f"{vip1} jetons",
            'vip2': f"{vip2} jetons",
            'vip3': f"{vip3} jetons",
            'total': f"{commission_totale} jetons"
        }
            
        with open(file_path, 'r') as f:
            data = json.load(f)
            commission_str = data.get('commission_totale', '0 jetons')
            try:
                commission_totale = int(commission_str.split(' ')[0])
                print(f"Commission totale trouvée: {commission_totale}")
            except (ValueError, IndexError):
                print(f"Erreur de conversion commission: {commission_str}")
                commission_totale = 0
            redistribution = commission_totale // 2  # 50% de la commission totale
            
            # Calculer les parts VIP
            vip1_share = int(redistribution * 0.20)  # 20% pour VIP 1
            vip2_share = int(redistribution * 0.30)  # 30% pour VIP 2
            vip3_share = int(redistribution * 0.50)  # 50% pour VIP 3
            
            return {
                'vip1': f"{vip1_share} jetons",
                'vip2': f"{vip2_share} jetons",
                'vip3': f"{vip3_share} jetons",
                'total': f"{commission_totale} jetons"
            }
    except Exception as e:
        print(f"Erreur VIP: {e}")
        return {
            'vip1': "0 jetons",
            'vip2': "0 jetons",
            'vip3': "0 jetons",
            'total': "0 jetons"
        }
