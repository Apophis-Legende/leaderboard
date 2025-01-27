
from replit import db
from datetime import datetime
from format_utils import format_kamas
from daily_commissions import get_daily_data, get_today_timestamp

def generate_daily_report(server):
    """Génère un rapport détaillé pour un serveur sur la journée en cours."""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        daily_data = get_daily_data(server, today)
        
        if not daily_data:
            return "❌ Aucune donnée disponible pour aujourd'hui"
            
        # Stats globales de la journée
        total_stats = {
            'total_bets': 0,
            'total_wins': 0,
            'total_commission': 0,
            'total_games': 0,
            'croupiers': {}
        }
        
        # Collecter les données des croupiers
        for croupier_id, data in daily_data.get('croupiers', {}).items():
            commission = float(data.get('daily_commission', '0 jetons').split()[0])
            total_stats['croupiers'][croupier_id] = {
                'username': data.get('username', 'Unknown'),
                'commission': commission,
                'role': data.get('role', 'standard')
            }
            total_stats['total_commission'] += commission
            
        return format_daily_report(server, total_stats)
        
    except Exception as e:
        return f"❌ Erreur lors de la génération du rapport: {e}"

def format_daily_report(server, stats):
    """Formate les statistiques journalières en carte ASCII."""
    server_names = {
        'T1': 'Tiliwan 1',
        'T2': 'Tiliwan 2',
        'O1': 'Oshimo',
        'H1': 'Herdegrize',
        'E1': 'Euro'
    }
    
    is_euro = server == 'E1'
    server_name = server_names.get(server, server)
    
    # Carte principale
    main_card = f"""```
╔══════════════════════════════════════════
║     Rapport Journalier - {server_name}     
╠══════════════════════════════════════════
║ 📅 Date: {datetime.now().strftime('%d/%m/%Y')}
║ 💰 Commission Totale: {format_kamas(f"{stats['total_commission']} jetons", is_euro)}
╚══════════════════════════════════════════```"""

    # Carte des croupiers
    croupiers_card = "```\n╔══════════════════════════════════════════\n║           Détails Croupiers              \n╠══════════════════════════════════════════"
    
    for croupier_id, data in stats['croupiers'].items():
        croupiers_card += f"\n║ 👤 {data['username']}\n║ 💸 Commission: {format_kamas(f'{data['commission']} jetons', is_euro)}\n║ 📋 Rôle: {data['role']}\n║ ──────────────────────────────────────────"
    
    croupiers_card += "\n╚══════════════════════════════════════════```"
    
    return f"{main_card}\n{croupiers_card}"
