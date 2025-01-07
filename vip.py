import json
import os

# Mapping entre les serveurs et leurs fichiers JSON
SERVER_FILE_MAPPING = {
    "Tiliwan1": "T1.json",
    "Tiliwan2": "T2.json",
    "Oshimo": "O1.json",
    "Herdegrize": "H1.json",
    "Euro": "E1.json"
}

# Définition des paliers VIP
VIP_TIERS = {
    3: 20000,  # Palier VIP 3 : 20000 jetons ou plus
    2: 10000,  # Palier VIP 2 : Entre 10000 et 19999 jetons
    1: 4000    # Palier VIP 1 : Entre 4000 et 9999 jetons
}

def load_server_json(server):
    """Charge les données du fichier JSON correspondant au serveur."""
    file_name = SERVER_FILE_MAPPING.get(server)
    if not file_name:
        raise ValueError(f"Serveur '{server}' non reconnu.")

    if not os.path.exists(file_name):
        print(f"❌ Fichier JSON pour le serveur '{server}' introuvable : {file_name}")
        return {}

    with open(file_name, "r", encoding="utf-8") as f:
        return json.load(f)

def calculate_vip_tier(total_bets):
    """Calcule le palier VIP en fonction des mises totales."""
    if total_bets >= VIP_TIERS[3]:
        return 3  # VIP 3
    elif total_bets >= VIP_TIERS[2]:
        return 2  # VIP 2
    elif total_bets >= VIP_TIERS[1]:
        return 1  # VIP 1
    else:
        return None  # Aucun palier atteint

async def check_and_notify_vip(player_id, server, channel):
    """
    Vérifie le palier VIP d'un utilisateur et envoie une notification s'il a débloqué un nouveau VIP.
    """
    try:
        # Charger les données du serveur
        server_data = load_server_json(server)
        user_data = server_data.get("utilisateurs", {}).get(player_id)

        if not user_data:
            print(f"❌ Aucun utilisateur avec l'ID {player_id} trouvé sur {server}.")
            return

        # Récupérer le total des mises
        total_bets = int(user_data["total_bets"].split(" ")[0])  # Exemple : "4500 jetons"

        # Calculer le palier VIP actuel
        current_vip_tier = calculate_vip_tier(total_bets)
        previous_vip_tier = user_data.get("vip_tier")  # Palier VIP précédent

        # Vérifier si un nouveau palier a été atteint
        if current_vip_tier and current_vip_tier != previous_vip_tier:
            # Mettre à jour les données utilisateur (en mémoire, pas dans le fichier)
            user_data["vip_tier"] = current_vip_tier

            # Envoyer un message Discord
            await channel.send(
                f"🎉 **Félicitations** <@{player_id}> : Vous avez débloqué le VIP {current_vip_tier} !"
            )

        else:
            print(f"🔹 Aucun nouveau palier VIP pour l'utilisateur {player_id}.")

    except Exception as e:
        print(f"❌ Erreur dans check_and_notify_vip : {e}")

def get_player_vip_status(player_id, server):
    """
    Récupère le statut VIP actuel d'un joueur pour un serveur donné depuis le fichier JSON du serveur.
    """
    try:
        # Charger les données du serveur
        server_data = load_server_json(server)

        # Récupérer les données du joueur
        player_data = server_data.get("utilisateurs", {}).get(player_id, {"total_bets": 0, "vip_tier": None})
        return player_data

    except Exception as e:
        print(f"❌ Erreur lors de la récupération des données VIP : {e}")
        return {"total_bets": 0, "vip_tier": None}

def display_vip_status(player_id, server):
    """
    Affiche les informations VIP d'un joueur pour un serveur donné.
    """
    player_data = get_player_vip_status(player_id, server)
    total_bets = player_data.get("total_bets", 0)
    vip_tier = player_data.get("vip_tier", None)

    if vip_tier:
        print(f"🔹 Joueur {player_id} sur {server} : Palier VIP {vip_tier}, Total misé : {total_bets} jetons.")
    else:
        print(f"🔸 Joueur {player_id} sur {server} : Aucun palier VIP atteint. Total misé : {total_bets} jetons.")
