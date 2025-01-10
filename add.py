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
        response = requests.get(link)
        giveaway_data = response.json()
        prize = giveaway_data.get("giveaway", {}).get("prize", "")

        server = prize.split()[0]
        server_name = mapping_server_file.get(server)

        if not server_name:
            print(f"⚠️ Serveur {server} non reconnu")
            return

        # Charger ou créer données
        data = db.get(server_name, {
            "serveur": server_name,
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

        # Mettre à jour les données...
        data["nombre_de_jeux"] += 1
        data["mises_totales_avant_commission"] = str(int(data["mises_totales_avant_commission"].split()[0]) + bet) + " jetons"
        data["gains_totaux"] = str(int(data["gains_totaux"].split()[0]) + gain) + " jetons"
        data["commission_totale"] = str(int(data["commission_totale"].split()[0]) + commission) + " jetons"

        # Sauvegarder
        db[server_name] = data
        print(f"✅ Données ajoutées pour {server_name}")

    except Exception as e:
        print(f"❌ Erreur: {str(e)}")