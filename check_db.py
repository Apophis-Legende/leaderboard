
from replit import db
from datetime import datetime

def check_db_content():
    print("\n=== Contenu des Commissions dans la DB ===\n")
    
    today = datetime.now().strftime('%Y-%m-%d')
    servers = ["T1", "T2", "O1", "H1", "E1"]
    
    # Vérifier les commissions journalières
    for server in servers:
        commission_key = f"COMMISSION/{server}/{today}"
        commission_data = db.get(commission_key, {})
        print(f"\n== Commissions {server} du {today} ==")
        print(f"Total: {commission_data.get('commissions', {}).get('total', '0')} jetons")
        
        # Vérifier l'historique des commissions
        history_key = f"{server}_commission_history"
        commission_history = db.get(history_key, {})
        print(f"\nHistorique des commissions {server}:")
        for date, data in commission_history.items():
            print(f"- Date: {date}")
            print(f"  Total: {data.get('total', 0)}")
            
        # Vérifier les détails des croupiers
        details_key = f"{server}_croupier_details"
        croupier_details = db.get(details_key, {})
        print(f"\nDétails des croupiers {server}:")
        for croupier_id, data in croupier_details.items():
            print(f"- Croupier: {data.get('username', 'Unknown')}")
            print(f"  Commission totale: {data.get('total_commission', 0)}")

if __name__ == "__main__":
    check_db_content()
