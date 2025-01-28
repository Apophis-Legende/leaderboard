
import random

WINNER_MESSAGES = [
    "GG {winner} ! T'as atomisé {loser} comme un pro ! 🎯",
    "Et bim ! {winner} qui met une petite fessée à {loser} ! 👋",
    "Félicitations {winner} ! {loser} va devoir retourner s'entraîner... 🎮",
    "Même pas stressé {winner} ! {loser} n'a rien vu venir ! 🚀",
    "La chance du débutant ? Non, {winner} c'est juste un boss ! 💪",
    "{winner} est tellement chanceux que même son poisson rouge gagne au poker ! 🎰",
    "RIP {loser}, {winner} t'as envoyé direct au cimetière des loosers ! ⚰️",
    "{winner} en mode machine de guerre ! {loser} n'avait aucune chance ! 🤖",
    "Quelqu'un a vu {loser} ? Ah non, il est parti pleurer... GG {winner} ! 😭",
    "C'était tellement facile pour {winner} que {loser} devrait changer de serveur ! 🎮",
    "{winner} prouve encore une fois que la chance sourit aux audacieux ! 🍀",
    "Et pan ! {winner} qui met une raclée à {loser} sans même transpirer ! 💦",
    "{loser} va devoir vendre son stuff pour se remettre de celle-là ! GG {winner} ! 💰",
    "On applaudit {winner} ! {loser}, t'inquiète pas, y'a pas de honte à perdre... enfin presque ! 👏",
    "Même Chuck Norris est impressionné par la victoire de {winner} ! 💥",
    "{winner} en mode sniper ! {loser} n'a même pas eu le temps de dire ouf ! 🎯",
    "La légende raconte que {loser} cherche encore ce qui s'est passé ! Bien joué {winner} ! 🔍",
    "{winner} plus rapide que l'éclair ! {loser} est encore en train de charger... ⚡",
    "GG {winner} ! {loser}, la prochaine fois essaie d'appuyer sur les bons boutons ! 🎮",
    "{winner} tellement fort qu'il pourrait gagner les yeux fermés ! {loser} en PLS ! 👀",
    "Victoire royale pour {winner} ! {loser} retourne à la case départ ! 👑",
    "{winner} en mode destruction totale ! {loser} n'était qu'un dommage collatéral ! 💣",
    "RIP {loser}, on t'aimait bien... Mais {winner} t'a totalement détruit ! ☠️",
    "{winner} prouve que la classe internationale existe ! {loser} en spectateur ! 🌟",
    "Plus facile qu'un tutoriel pour {winner} ! Désolé {loser} ! 📚",
    "{winner} en mode ultra instinct ! {loser} n'a rien pu faire ! 🔥",
    "La victoire de {winner} était écrite ! {loser}, fallait pas venir aujourd'hui ! 📝",
    "{winner} tellement fort que même ses adversaires l'applaudissent ! Pas vrai {loser} ? 👏",
    "GG {winner} ! {loser}, t'inquiète, y'a toujours McDo qui recrute ! 🍔",
    "{winner} en mode super saiyan ! {loser} retourne s'entraîner ! 🐉",
    "La victoire de {winner} plus propre que le ménage de ma grand-mère ! Déso {loser} ! 🧹",
    "{winner} qui donne une leçon gratuite à {loser} ! C'est beau la générosité ! 📚",
    "Même pas besoin de commentaire, {winner} a tout dit ! {loser} en sueur ! 💦",
    "{winner} tellement dominant que {loser} devrait prendre sa retraite ! 👴",
    "GG {winner} ! {loser}, garde espoir, un jour peut-être... ou pas ! 😅",
    "{winner} en mode machine à gagner ! {loser} en mode machine à perdre ! 🤖",
    "La masterclass de {winner} ! {loser} prend des notes ! 📝",
    "{winner} qui fait son show ! {loser} en spectateur privilégié ! 🎭",
    "Plus rapide que son ombre, c'est {winner} ! {loser} n'a rien vu venir ! 🏃",
    "{winner} en mode no mercy ! {loser}, fallait pas le chercher ! ⚔️",
    "La chance ? Non, juste {winner} qui est trop fort ! Déso pas déso {loser} ! 💪",
    "{winner} qui prouve que la victoire appartient aux audacieux ! {loser} en PLS ! 🦁",
    "GG {winner} ! {loser}, t'inquiète, y'a pas de petites défaites... Ah si, celle-là elle est énorme ! 😂",
    "{winner} en mode festival de victoires ! {loser} en mode festival de défaites ! 🎪",
    "La victoire plus belle que le sourire de {winner} ! {loser} en larmes ! 😭",
    "{winner} qui fait son show ! {loser} en mode plante verte ! 🌿",
    "GG {winner} ! {loser}, y'a des jours comme ça où faut pas se lever ! ⏰",
    "{winner} en mode boss final ! {loser} en mode petit mob ! 👾",
    "La victoire de {winner} plus propre qu'un whisky 12 ans d'âge ! {loser} en mode jus de pomme ! 🥃",
    "GG {winner} ! {loser}, t'inquiète, demain est un autre jour... pour perdre aussi ! 📅",
    "{winner} qui écrit l'histoire ! {loser} qui écrit sa lettre de démission ! 📜",
    "La victoire de {winner} plus belle qu'un coucher de soleil ! {loser} dans le noir ! 🌅",
    "{winner} en mode légende ! {loser} en mode légende... urbaine ! 🏆",
    "GG {winner} ! {loser}, au moins t'as participé... c'est déjà ça ! 🎮",
    "{winner} qui prouve que la classe existe ! {loser} qui prouve que la loose aussi ! 🎭",
    "La victoire de {winner} plus nette qu'un costume trois pièces ! {loser} en pyjama ! 👔",
    "{winner} en mode champion ! {loser} en mode... bah en mode {loser} quoi ! 🏅",
    "GG {winner} ! {loser}, garde la pêche... t'en auras besoin pour la prochaine défaite ! 🎣",
    "{winner} qui donne une leçon de style ! {loser} qui prend des cours du soir ! 📚",
    "La victoire de {winner} plus smooth qu'un jazz à minuit ! {loser} en playback ! 🎷",
    "{winner} en mode first class ! {loser} en classe éco ! ✈️",
    "GG {winner} ! {loser}, c'est pas grave de perdre... enfin, pas trop ! 😅",
    "{winner} qui fait son show à Broadway ! {loser} qui fait la figuration ! 🎭",
    "La victoire de {winner} plus fraîche qu'une menthe à l'eau ! {loser} à l'eau plate ! 🌿",
    "{winner} en mode rockstar ! {loser} en mode groupie ! 🎸",
    "GG {winner} ! {loser}, t'inquiète, y'a pas que la victoire dans la vie... mais ça aide ! 🎯",
    "{winner} qui écrit sa légende ! {loser} qui écrit ses excuses ! 📝",
    "La victoire de {winner} plus précise qu'un chirurgien ! {loser} en salle d'attente ! 🏥",
    "{winner} en mode premium ! {loser} en version d'essai ! 💎",
    "GG {winner} ! {loser}, c'est le jeu ma pauvre Lucette ! 🎲",
    "{winner} qui fait son entrée au panthéon ! {loser} qui fait la queue dehors ! 🏛️",
    "La victoire de {winner} plus brillante qu'un diamant ! {loser} en strass ! 💎",
    "{winner} en mode VIP ! {loser} en mode file d'attente ! 🎟️",
    "GG {winner} ! {loser}, next time... ou pas ! ⏭️",
    "{winner} qui met tout le monde d'accord ! {loser} qui cherche encore ses arguments ! 🗣️",
    "La victoire de {winner} plus clean qu'un cabinet d'avocat ! {loser} au tribunal ! ⚖️",
    "{winner} en mode masterclass ! {loser} en mode classe de rattrapage ! 🎓",
    "GG {winner} ! {loser}, t'es un bon... perdant ! 🎭",
    "{winner} qui fait la une ! {loser} aux petites annonces ! 📰",
    "La victoire de {winner} plus stylée qu'un défilé de mode ! {loser} en coulisses ! 👗",
    "{winner} en mode blockbuster ! {loser} en film de série B ! 🎬",
    "GG {winner} ! {loser}, y'a des défaites qui font mal... celle-là, elle fait très mal ! 🤕",
    "{winner} qui entre dans l'histoire ! {loser} qui sort par la petite porte ! 🚪",
    "La victoire de {winner} plus épique qu'un film de Spielberg ! {loser} au générique ! 🎥",
    "{winner} en mode cinq étoiles ! {loser} au camping ! ⭐",
    "GG {winner} ! {loser}, fallait pas venir... mais alors vraiment pas ! 🚫",
    "{winner} qui fait sensation ! {loser} qui fait... rien du tout ! 💫",
    "La victoire de {winner} plus forte que le café du matin ! {loser} en décaf ! ☕",
    "{winner} en mode festival de Cannes ! {loser} en mode télé-réalité ! 🎭",
    "GG {winner} ! {loser}, retourne t'entraîner... beaucoup t'entraîner ! 💪",
    "{winner} qui marque l'histoire ! {loser} qui marque... une pause ! ⏸️",
    "La victoire de {winner} plus classe qu'un smoking ! {loser} en jogging ! 👔",
    "{winner} en mode chef étoilé ! {loser} en cuisine de cantine ! 👨‍🍳",
    "GG {winner} ! {loser}, c'est pas ta journée... ni ta semaine... ni ton mois en fait ! 📅",
    "{winner} qui fait rêver ! {loser} qui fait dormir ! 😴",
    "La victoire de {winner} plus intense qu'un film d'action ! {loser} en documentaire ! 🎬",
    "{winner} en mode champion olympique ! {loser} en mode sports d'hiver ! 🏅"
]

def get_random_winner_message(winner, loser):
    """Retourne un message aléatoire en remplaçant les noms"""
    message = random.choice(WINNER_MESSAGES)
    return message.format(winner=winner, loser=loser)

async def send_giveaway_message(raw_data, channel):
    """Envoie un message personnalisé après un giveaway"""
    winner = raw_data["winners"][0]["username"] if raw_data.get("winners") else None
    entries = raw_data.get("entries", [])
    loser = next((entry["username"] for entry in entries if entry["username"] != winner), None)

    if winner and loser:
        await asyncio.sleep(3)  # Attendre 3 secondes
        winner_id = next((user["id"] for user in raw_data["winners"] if user["username"] == winner), None)
        loser_id = next((user["id"] for user in raw_data["entries"] if user["username"] == loser), None)
        custom_message = get_random_winner_message(f"<@{winner_id}>", f"<@{loser_id}>")
        await channel.send(f"**```diff\n+ {custom_message}\n```**")
