
from replit import db
from format_utils import format_kamas

def calculate_host_stats(host_id):
    """Calcule les statistiques pour un hôte spécifique à travers tous les serveurs."""
    servers = ['T1', 'T2', 'O1', 'H1', 'E1']
    total_stats = {
        'username': '',
        'total_commission': 0,
        'total_commission_euro': 0,
        'total_bets': 0,
        'total_giveaways': 0,
        'commission_from_participation': 0,
        'commission_from_participation_euro': 0
    }

    for server in servers:
        try:
            server_data = db.get(f"{server}.json", {})
            if not server_data:
                continue

            # Stats en tant qu'hôte
            hosts = server_data.get('hôtes', {})
            if host_id in hosts:
                host_data = hosts[host_id]
                total_stats['username'] = host_data['username']
                commission = int(host_data['total_commission'].split()[0])
                if server == 'E1':
                    total_stats['total_commission_euro'] += commission
                else:
                    total_stats['total_commission'] += commission
                total_stats['total_bets'] += int(host_data['total_bets'].split()[0])
                total_stats['total_giveaways'] += host_data.get('total_giveaways', 0)

            # Commission générée par participations
            users = server_data.get('utilisateurs', {})
            if host_id in users:
                user_data = users[host_id]
                total_bets = int(user_data['total_bets'].split()[0])
                total_stats['commission_from_participation'] += int(total_bets * 0.05)

        except Exception as e:
            print(f"❌ Erreur lecture données {server}: {e}")

    return total_stats

def format_host_card(stats):
    """Formate les statistiques de l'hôte en carte ASCII."""
    cards = []

    # Carte des stats totales
    total_card = f"""```
╔══════════════════════════════════════════
║           Stats Totales Hôte             
╠══════════════════════════════════════════
║ 👤 {stats['username']}
║ 💰 Commission Totale: {format_kamas(f"{stats['total_commission']} jetons")} + {format_kamas(f"{stats['total_commission_euro']} jetons", is_euro=True)}
║ 🎲 Mises Totales: {format_kamas(f"{stats['total_bets']} jetons")}
║ 🎮 Giveaways Organisés: {stats['total_giveaways']}
║ 💸 Commission générée : {format_kamas(f"{stats['commission_from_participation']} jetons", is_euro=True)}
╚══════════════════════════════════════════```"""
    cards.append(total_card)

    # Cartes par serveur
    server_names = {
        'T1': 'Tiliwan 1',
        'T2': 'Tiliwan 2',
        'O1': 'Oshimo',
        'H1': 'Herdegrize',
        'E1': 'Euro'
    }

    for server in ['T1', 'T2', 'O1', 'H1', 'E1']:
        try:
            server_data = db.get(f"{server}.json", {})
            hosts = server_data.get('hôtes', {})
            host_data = next((data for data in hosts.values() if data.get('username') == stats['username']), None)
            
            if host_data:
                server_card = f"""```
╔══════════════════════════════════════════
║              {server_names[server]}                
╠══════════════════════════════════════════
║ 💰 Commission: {format_kamas(host_data['total_commission'], server=='E1')}
║ 🎲 Mises: {format_kamas(host_data['total_bets'], server=='E1')}
║ 🎮 Giveaways: {host_data.get('total_giveaways', 0)}
╚══════════════════════════════════════════```"""
                cards.append(server_card)
        except Exception as e:
            print(f"❌ Erreur format carte {server}: {e}")
            continue

    return "\n".join(cards)
