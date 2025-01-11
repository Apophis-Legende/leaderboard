from replit import db

def calculate_vip_commissions(server):
    """
    Calculer les commissions VIP pour un serveur donné.
    Charge les données depuis Replit DB et calcule les répartitions.
    """
    try:
        # Charger les données depuis la DB
        server_data = db.get(f"{server}.json")
        if not server_data:
            print(f"❌ Aucune donnée trouvée pour {server}")
            return {
                "vip1": 0,
                "vip2": 0,
                "vip3": 0,
                "total": 0
            }

        # Extraire la commission totale
        total_commission = server_data.get("commission_totale", "0 jetons")
        if isinstance(total_commission, str):
            total_commission = int(total_commission.split()[0])

        if total_commission == 0:
            print(f"ℹ️ Pas de commissions à redistribuer pour {server}")
            return {
                "vip1": 0,
                "vip2": 0,
                "vip3": 0,
                "total": 0
            }

        # Calcul des répartitions
        redistributable = total_commission * 0.5  # 50% pour VIPs
        vip1_share = redistributable * 0.2  # 20% de la moitié
        vip2_share = redistributable * 0.3  # 30% de la moitié
        vip3_share = redistributable * 0.5  # 50% de la moitié

        return {
            "vip1": vip1_share,
            "vip2": vip2_share,
            "vip3": vip3_share,
            "total": total_commission
        }

    except Exception as e:
        print(f"❌ Erreur dans le calcul des commissions pour {server}: {e}")
        return {
            "vip1": 0,
            "vip2": 0,
            "vip3": 0,
            "total": 0
        }
