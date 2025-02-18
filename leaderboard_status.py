
import random
from replit import db
from format_utils import format_kamas
from vip import calculate_vip_tier

SERVER_MAPPING = {
    "Tiliwan1": "T1",
    "Tiliwan2": "T2", 
    "Oshimo": "O1",
    "Herdegrize": "H1",
    "Euro": "E1",
    "T1": "T1",
    "T2": "T2",
    "O1": "O1",
    "H1": "H1",
    "E1": "E1"
}

VIP_THRESHOLDS = {
    "E1": {
        1: 150,
        2: 350,
        3: 600
    },
    "default": {
        1: 6000,
        2: 14500,
        3: 24000
    }
}

# Messages spéciaux pour les croupiers et utilisateurs sans données
CROUPIER_MESSAGES = [
    "Hey le croupier ! Tu veux pas plutôt distribuer des cartes au lieu de chercher des VIP ? 🎲",
    "Un croupier qui veut devenir VIP ? C'est comme un poisson qui veut apprendre à voler ! 🐠",
    "T'es croupier mon reuf, tu gagnes déjà assez de kamas comme ça ! 💸",
    "Reste à ta table de jeu, c'est là que tu brilles le plus ! ✨"
]

NO_DATA_MESSAGES = [
    "Tu cherches tes données comme un joueur cherche ses kamas après une défaite ! 🔍",
    "Tes données sont aussi vides que ta bourse de kamas ! 💰",
    "On a rien trouvé... comme tes chances de gagner au poker ! 🎰",
    "Données introuvables... T'as vérifié sous ton tapis ? 🧐"
]

VIP_MESSAGES = {
    0: [
        "Ah... Je vois que tu es aussi riche que mon compte en banque un lendemain de sortie ! 😅",
        "VIP ? C'est quoi ça, ça se mange ? 🍽️",
        "T'es tellement pauvre que même les kamas te font l'aumône ! 💸",
        "VIP ? Non, mais on a un statut 'En Voie de Développement' si tu veux ! 😂",
        "Ton statut VIP est comme ma motivation le lundi matin : inexistant ! 🛌"
    ],
    1: [
        "VIP 1 ! C'est un bon début, comme apprendre à marcher... en trébuchant ! 🚶",
        "VIP 1, bienvenue dans le club des petits joueurs qui deviennent grands ! 🌱",
        "T'as réussi à devenir VIP 1 ! La prochaine étape c'est d'arrêter de compter tes kamas ! 💰"
    ],
    2: [
        "VIP 2 ! Tu commences à faire peur aux banquiers ! 🏦",
        "Niveau VIP 2... Les autres joueurs commencent à te demander des autographes ? 📝",
        "VIP 2 ? Je vois que quelqu'un a décidé de jouer dans la cour des grands ! 🎮"
    ],
    3: [
        "T'es déjà VIP 3... Tu veux la lune ou quoi ? 🌙",
        "VIP 3 ? Ça commence à sentir le patron ici ! Tu vises quoi, le trône ? 👑",
        "Déjà VIP 3 ? Tu vas bientôt devoir signer des autographes. ✍️",
        "VIP 3, sérieusement ? À ce rythme, t'es le boss du serveur demain. 🎯",
        "Oh, VIP 3, carrément. La prochaine étape, c'est quoi ? Président du serveur ? 🎖️",
        "T'as atteint VIP 3... Laisse un peu de place aux autres quand même ! 🚀",
        "VIP 3 et tu veux encore plus ? On va bientôt mettre ton nom sur le serveur. 🏆",
        "VIP 3 ? Fais gaffe, y'a des joueurs qui te regardent déjà avec des étoiles dans les yeux. ⭐",
        "T'as monté VIP 3… T'es sûr que le serveur n'est pas à toi en secret ? 🤔",
        "VIP 3 déjà ? Attends, je vais prévenir le maire, ça devient sérieux. 📢"
    ]
}

def get_vip_status(user_id, server, total_bets):
    """Calculate VIP status and next threshold for a user"""
    is_euro = server == "E1"
    server_code = SERVER_MAPPING.get(server, server)
    
    # Vérifier si l'utilisateur est un croupier
    forbidden_users = db.get("forbidden_vip_users", {})
    if str(user_id) in forbidden_users:
        return {
            "current_vip": None,
            "message": random.choice(CROUPIER_MESSAGES),
            "next_threshold": None,
            "remaining": 0
        }

    # Vérifier si l'utilisateur a des données
    server_code = SERVER_MAPPING.get(server, server)
    server_data = db.get(f"{server_code}.json", {})
    user_data = server_data.get("utilisateurs", {}).get(str(user_id), {})
    
    if not user_data:
        return {
            "current_vip": None,
            "message": random.choice(NO_DATA_MESSAGES),
            "next_threshold": None,
            "remaining": 0
        }

    server_code = SERVER_MAPPING.get(server, server)
    thresholds = VIP_THRESHOLDS["E1"] if server_code == "E1" else VIP_THRESHOLDS["default"]
    
    current_vip = calculate_vip_tier(total_bets, server_code)
    if not current_vip:
        current_vip = 0
        
    next_threshold = None
    remaining = 0
    
    if current_vip < 3:
        next_level = current_vip + 1
        next_threshold = thresholds[next_level]
        remaining = next_threshold - total_bets

    message = random.choice(VIP_MESSAGES[current_vip])
    
    formatted_remaining = format_kamas(f"{remaining} jetons", is_euro) if remaining > 0 else "0"
    return {
        "current_vip": current_vip,
        "message": message,
        "next_threshold": next_threshold,
        "remaining": formatted_remaining
    }
