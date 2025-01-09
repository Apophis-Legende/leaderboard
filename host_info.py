
import json
from format_utils import format_kamas

def calculate_host_stats(host_id):
    """Calcule les statistiques pour un hôte spécifique à travers tous les serveurs."""
    servers = ['T1.json', 'T2.json', 'O1.json', 'H1.json', 'E1.json']
    stats_by_server = {}
    
    for server_file in servers:
        try:
            with open(server_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                server_name = server_file.replace('.json', '')
                
                # Stats en tant qu'hôte
                host_data = data.get('hôtes', {}).get(str(host_id))
                if host_data:
                    stats_by_server[server_name] = {
                        'username': host_data['username'],
                        'total_commission': host_data['total_commission'],
                        'total_bets': host_data['total_bets'],
                        'total_giveaways': host_data.get('total_giveaways', 0),
                        'commission_from_participation': "0 jetons"
                    }
                
                # Commission générée par ses participations
                user_data = data.get('utilisateurs', {}).get(str(host_id))
                if user_data:
                    total_bets = int(user_data['total_bets'].split()[0])
                    commission = f"{int(total_bets * 0.05)} jetons"
                    
                    if server_name in stats_by_server:
                        stats_by_server[server_name]['commission_from_participation'] = commission
                    else:
                        stats_by_server[server_name] = {
                            'username': user_data['username'],
                            'total_commission': "0 jetons",
                            'total_bets': "0 jetons",
                            'total_giveaways': 0,
                            'commission_from_participation': commission
                        }
                    
        except Exception as e:
            print(f"Erreur lors de la lecture de {server_file}: {e}")
    
    return stats_by_server

def format_host_card(stats):
    """Formate les statistiques de l'hôte en carte ASCII."""
    if not stats:
        return "```\nAucune donnée d'hôte trouvée pour cet utilisateur.\n```"
    
    has_data = False
    for server_data in stats.values():
        if server_data and any(server_data.values()):
            has_data = True
            break
            
    if not has_data:
        return "```\nAucune donnée d'hôte trouvée pour cet utilisateur.\n```"
        
    card = "```\n╔══════════════════════════════════════════\n"
    card += "║             Carte de l'Hôte              \n"
    card += "╠══════════════════════════════════════════\n"
    
    for server, data in stats.items():
        card += f"║ 🌍 Serveur: {server}\n"
        card += f"║ 👤 {data['username']}\n"
        card += f"║ 💰 Commission: {format_kamas(data['total_commission'])}\n"
        card += f"║ 🎲 Mises Totales: {format_kamas(data['total_bets'])}\n"
        card += f"║ 🎮 Giveaways: {data['total_giveaways']}\n"
        card += f"║ 💸 Commission générée: {format_kamas(data['commission_from_participation'])}\n"
        card += "║ ──────────────────────────────────────────\n"
    
    card += "╚══════════════════════════════════════════\n```"
    return card
