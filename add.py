
import os
import json
from replit import db
import requests

MAPPING_SERVER_FILE = {
    "T1": "T1",
    "T2": "T2",
    "O1": "O1", 
    "H1": "H1",
    "E1": "E1"
}

def add_giveaway_data(link, mapping_server_file):
    try:
        # Convertir le lien en lien API si nécessaire
        api_url = link.replace("https://giveawaybot.party/summary#", "https://summary-api.giveawaybot.party/?")
        response = requests.get(api_url)
        giveaway_data = response.json()
        
        if not giveaway_data or "giveaway" not in giveaway_data:
            raise Exception("Données du giveaway invalides")

        prize = giveaway_data["giveaway"]["prize"]
        server = prize.split()[0]
        server_name = f"{server}.json"

        # Charger ou créer données
        data = db.get(server_name, {
            "serveur": server,
            "nombre_de_jeux": 0,
            "mises_totales_avant_commission": "0 jetons",
            "gains_totaux": "0 jetons",
            "commission_totale": "0 jetons",
            "utilisateurs": {},
            "hôtes": {},
            "croupiers": {}
        })

        # Mise à jour des données
        winners = giveaway_data.get("winners", [])
        entries = giveaway_data.get("entries", [])
        gain = int(prize.split()[1])
        bet = int(gain / 0.95)
        commission = bet - gain

        # Mettre à jour les données globales
        data["nombre_de_jeux"] += 1
        data["mises_totales_avant_commission"] = f"{int(data['mises_totales_avant_commission'].split()[0]) + bet} jetons"
        data["gains_totaux"] = f"{int(data['gains_totaux'].split()[0]) + gain} jetons"
        data["commission_totale"] = f"{int(data['commission_totale'].split()[0]) + commission} jetons"

        # Mettre à jour les utilisateurs
        for winner in winners:
            user_id = str(winner["id"])
            if user_id not in data["utilisateurs"]:
                data["utilisateurs"][user_id] = {
                    "username": winner["username"],
                    "total_wins": "0 jetons",
                    "total_losses": "0 jetons",
                    "total_bets": "0 jetons",
                    "participation": 0
                }
            
            user = data["utilisateurs"][user_id]
            user["total_wins"] = f"{int(user['total_wins'].split()[0]) + gain} jetons"
            user["total_bets"] = f"{int(user['total_bets'].split()[0]) + bet//len(entries)} jetons"
            user["participation"] += 1

        for entry in entries:
            if str(entry["id"]) not in [str(w["id"]) for w in winners]:
                user_id = str(entry["id"])
                if user_id not in data["utilisateurs"]:
                    data["utilisateurs"][user_id] = {
                        "username": entry["username"],
                        "total_wins": "0 jetons",
                        "total_losses": "0 jetons",
                        "total_bets": "0 jetons",
                        "participation": 0
                    }
                
                user = data["utilisateurs"][user_id]
                user["total_losses"] = f"{int(user['total_losses'].split()[0]) + bet//len(entries)} jetons"
                user["total_bets"] = f"{int(user['total_bets'].split()[0]) + bet//len(entries)} jetons"
                user["participation"] += 1

        # Mettre à jour l'hôte
        host = giveaway_data["giveaway"]["host"]
        host_id = str(host["id"])
        if host_id not in data["hôtes"]:
            data["hôtes"][host_id] = {
                "username": host["username"],
                "total_bets": "0 jetons",
                "total_commission": "0 jetons"
            }
        
        host_data = data["hôtes"][host_id]
        host_data["total_bets"] = f"{int(host_data['total_bets'].split()[0]) + bet} jetons"
        host_data["total_commission"] = f"{int(host_data['total_commission'].split()[0]) + commission} jetons"

        # Sauvegarder
        db[server_name] = data
        print(f"✅ Données ajoutées pour {server_name}")

    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        raise
