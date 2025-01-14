
from replit import db

def check_db_content():
    print("\n=== Contenu de la Replit DB ===\n")

    # Afficher les clés principales
    print("Clés disponibles:", list(db.keys()))

    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Parcourir les serveurs
    servers = ["T1", "T2", "O1", "H1", "E1"]
    for server in servers:
        # Données du serveur pour aujourd'hui
        server_data = db.get(f"LB/{server}/{today}", {})
        print(f"\n== Données {server} du {today} ==")
        print(f"Commission totale: {server_data.get('commission_totale', '0 jetons')}")

        # Historique des commissions
        history_key = f"{server}_commission_history"
        commission_history = db.get(history_key, {})
        print(f"\nHistorique des commissions {server}:")
        for date, data in commission_history.items():
            print(f"- Date: {date}")
            print(f"  Total: {data.get('total', 0)} jetons")

        # Détails des croupiers
        details_key = f"{server}_croupier_details"
        croupier_details = db.get(details_key, {})
        print(f"\nDétails des croupiers {server}:")
        for croupier_id, data in croupier_details.items():
            print(f"- Croupier: {data.get('username', 'Unknown')}")
            print(f"  Total commissions: {data.get('total_commission', 0)} jetons")

if __name__ == "__main__":
    check_db_content()
