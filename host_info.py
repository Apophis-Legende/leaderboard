from replit import db
from format_utils import format_kamas

def calculate_host_stats(host_id):
    """Calcule les statistiques pour un hôte spécifique à travers tous les serveurs dans Replit DB."""
    servers = ['T1', 'T2', 'O1', 'H1', 'E1']
    total_stats = {
        'username': '',
        'total_commission': 0,
        'total_bets': 0,
        'total_giveaways': 0,
        'commission_from_participation': 0
    }

    for server in servers:
        try:
            # Charger les données du serveur depuis Replit DB
            data = db.get(server, {})

            # Stats en tant qu'hôte
            if host_id in data.get('hôtes', {}):
                host_data = data['hôtes'][host_id]
                total_stats['username'] = host_data['username']
                total_stats['total_commission'] += int(host_data['total_commission'].split()[0])
                total_stats['total_bets'] += int(host_data['total_bets'].split()[0])
                total_stats['total_giveaways'] += host_data.get('total_giveaways', 0)

            # Commission générée par ses participations
            if host_id in data.get('utilisateurs', {}):
                user_data = data['utilisateurs'][host_id]
                total_bets = int(user_data['total_bets'].split()[0])
                total_stats['commission_from_participation'] += int(total_bets * 0.05)

        except Exception as e:
            print(f"Erreur lors de la lecture des données du serveur {server}: {e}")

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
║ 💰 Commission Totale: {format_kamas(f"{stats['total_commission']} jetons")}
║ 🎲 Mises Totales: {format_kamas(f"{stats['total_bets']} jetons")}
║ 🎮 Giveaways Organisés: {stats['total_giveaways']}
║ 💸 Commission générée : {format_kamas(f"{stats['commission_from_participation']} jetons")}
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
            # Charger les données du serveur depuis Replit DB
            data = db.get(server, {})
            if stats['username'] in [host_data.get('username') for host_data in data.get('hôtes', {}).values()]:
                host_data = next(hd for hd in data['hôtes'].values() if hd.get('username') == stats['username'])
                server_name = server_names[server]
                server_card = f"""```
╔══════════════════════════════════════════
║              {server_name}                
╠══════════════════════════════════════════
║ 💰 Commission: {format_kamas(host_data['total_commission'])}
║ 🎲 Mises: {format_kamas(host_data['total_bets'])}
║ 🎮 Giveaways: {host_data.get('total_giveaways', 0)}
╚══════════════════════════════════════════```"""
                cards.append(server_card)
        except Exception as e:
            continue

    return "\n".join(cards)
