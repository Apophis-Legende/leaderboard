
from replit import db

def calculate_vip_commissions(server):
    """Calcule les commissions VIP pour un serveur donné"""
    try:
        server_data = db.get(f"{server}.json", {})
        if not server_data:
            return {
                "vip1": 0,
                "vip2": 0,
                "vip3": 0,
                "total": 0
            }

        total_commission = int(server_data.get("commission_totale", "0 jetons").split()[0])
        
        return {
            "vip1": total_commission * 0.20,  # VIP 1 : 20%
            "vip2": total_commission * 0.30,  # VIP 2 : 30%
            "vip3": total_commission * 0.50,  # VIP 3 : 50%
            "total": total_commission
        }
    except Exception as e:
        print(f"❌ Erreur calcul commissions: {e}")
        return {
            "vip1": 0,
            "vip2": 0,
            "vip3": 0,
            "total": 0
        }
