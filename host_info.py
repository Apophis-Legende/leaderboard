
import json
from format_utils import format_kamas

def calculate_host_stats(host_id):
    """Calcule les statistiques pour un hôte spécifique à travers tous les serveurs."""
    servers = ['T1.json', 'T2.json', 'O1.json', 'H1.json', 'E1.json']
    stats_by_server = {'username': None}
    
    for server_file in servers:
        try:
            with open(server_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                server_name = server_file.replace('.json', '')
                
                # Stats en tant qu'hôte
                if host_id in data.get('hôtes', {}):
                    host_data = data['hôtes'][host_id]
                    stats_by_server[server_name] = {
                        'username': host_data['username'],
                        'total_commission': int(host_data['total_commission'].split()[0]),
                        'total_bets': int(host_data['total_bets'].split()[0]),
                        'total_giveaways': host_data.get('total_giveaways', 0),
                        'commission_from_participation': 0
                    }
                
                # Commission générée par ses participations
                if host_id in data.get('utilisateurs', {}):
                    user_data = data['utilisateurs'][host_id]
                    total_bets = int(user_data['total_bets'].split()[0])
                    commission = int(total_bets * 0.05)
                    
                    if server_name in stats_by_server:
                        stats_by_server[server_name]['commission_from_participation'] = commission
                    else:
                        stats_by_server[server_name] = {
                            'username': user_data['username'],
                            'total_commission': 0,
                            'total_bets': 0,
                            'total_giveaways': 0,
                            'commission_from_participation': commission
                        }
                    
        except Exception as e:
            print(f"Erreur lors de la lecture de {server_file}: {e}")
    
    return stats_by_server

def format_host_card(stats):
    """Formate les statistiques de l'hôte en carte ASCII."""
    if not stats:
        return "```\nAucune donnée trouvée pour cet hôte.\n```"
        
    card = "```\n╔══════════════════════════════════════════\n"
    card += "║             Carte de l'Hôte              \n"
    card += "╠══════════════════════════════════════════\n"
    
    for server, data in stats.items():
        card += f"║ 🌍 Serveur: {server}\n"
        card += f"║ 👤 {data['username']}\n"
        card += f"║ 💰 Commission: {format_kamas(str(data['total_commission']) + ' jetons')}\n"
        card += f"║ 🎲 Mises Totales: {format_kamas(str(data['total_bets']) + ' jetons')}\n"
        card += f"║ 🎮 Giveaways: {data['total_giveaways']}\n"
        card += f"║ 💸 Commission générée: {format_kamas(str(data['commission_from_participation']) + ' jetons')}\n"
        card += "║ ──────────────────────────────────────────\n"
    
    card += "╚══════════════════════════════════════════\n```"
    return card
