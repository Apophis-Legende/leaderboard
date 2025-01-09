
import json
from format_utils import format_kamas

def calculate_host_stats(host_id):
    """Calcule les statistiques pour un hôte spécifique à travers tous les serveurs."""
    servers = ['T1.json', 'T2.json', 'O1.json', 'H1.json', 'E1.json']
    total_stats = {
        'username': '',
        'total_commission': 0,
        'total_bets': 0,
        'total_giveaways': 0,
        'commission_from_participation': 0
    }
    
    for server_file in servers:
        try:
            with open(server_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Stats en tant qu'hôte
                if host_id in data.get('hôtes', {}):
                    host_data = data['hôtes'][host_id]
                    total_stats['username'] = host_data['username']
                    total_stats['total_commission'] += int(host_data['total_commission'].split()[0])
                    total_stats['total_bets'] += int(host_data['total_bets'].split()[0])
                    if 'total_giveaways' in data['croupiers'].get(host_id, {}):
                        total_stats['total_giveaways'] += data['croupiers'][host_id]['total_giveaways']
                
                # Commission générée par ses participations
                if host_id in data.get('utilisateurs', {}):
                    user_data = data['utilisateurs'][host_id]
                    total_bets = int(user_data['total_bets'].split()[0])
                    total_stats['commission_from_participation'] += int(total_bets * 0.05)
                    
        except Exception as e:
            print(f"Erreur lors de la lecture de {server_file}: {e}")
    
    return total_stats

def format_host_card(stats):
    """Formate les statistiques de l'hôte en carte ASCII."""
    return f"""```
╔══════════════════════════════════════════
║             Carte de l'Hôte              
╠══════════════════════════════════════════
║ 👤 {stats['username']}
║ 💰 Commission Totale: {format_kamas(f"{stats['total_commission']} jetons")}
║ 🎲 Mises Totales: {format_kamas(f"{stats['total_bets']} jetons")}
║ 🎮 Giveaways Organisés: {stats['total_giveaways']}
║ 💸 Commission générée : {format_kamas(f"{stats['commission_from_participation']} jetons")}
╚══════════════════════════════════════════
```"""
