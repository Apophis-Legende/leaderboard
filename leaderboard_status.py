
import random
from format_utils import format_kamas, SERVER_MAPPING
from vip import calculate_vip_tier

VIP_THRESHOLDS = {
    "E1": {
        1: 150,
        2: 350,
        3: 600
    },
    "default": {
        1: 4000,
        2: 10000,
        3: 15000
    }
}

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
    
    return {
        "current_vip": current_vip,
        "message": message,
        "next_threshold": next_threshold,
        "remaining": remaining
    }
