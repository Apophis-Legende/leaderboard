
import random

WINNER_MESSAGES = [
    # Messages existants conservés
    "La victoire de {winner} plus clean qu'un cabinet d'avocat ! {loser} au tribunal ! ⚖️",
    "{winner} en mode masterclass ! {loser} en mode classe de rattrapage ! 🎓",
    "GG {winner} ! {loser}, t'es un bon... perdant ! 🎭",
    # Nouveaux messages ajoutés
    "{winner} en mode fusée SpaceX ! {loser} coincé au décollage ! 🚀",
    "La victoire de {winner} plus précise qu'une montre suisse ! {loser} en retard ! ⌚",
    "{winner} en mode chef d'orchestre ! {loser} qui joue faux ! 🎼",
    "GG {winner} ! {loser} plus perdu qu'un GPS en panne ! 🗺️",
    "{winner} qui danse la samba ! {loser} qui fait la macarena... tout seul ! 💃",
    "La victoire de {winner} plus fraîche que la clim en été ! {loser} en sueur ! ❄️",
    "{winner} en mode laser ! {loser} qui cherche l'interrupteur ! 🔦",
    "GG {winner} ! {loser} parti chercher des excuses au pôle nord ! 🧊",
    "{winner} en pilote automatique vers la victoire ! {loser} au garage ! 🚗",
    "La victoire de {winner} plus évidente que 2+2=4 ! {loser} en cours de maths ! 📐",
    "{winner} en mode Matrix ! {loser} bloqué dans la simulation ! 🕶️",
    "GG {winner} ! {loser} plus confus qu'un pingouin dans le désert ! 🐧",
    "{winner} qui fait un carton ! {loser} qui ramasse les morceaux ! 📦",
    "La victoire de {winner} plus certaine que le lever du soleil ! {loser} dans le noir ! 🌅",
    "{winner} en mode ninja ! {loser} qui fait du bruit en marchant ! 🥷",
    "GG {winner} ! {loser} parti méditer sur sa défaite... au Tibet ! 🏔️",
    "{winner} en mode supernova ! {loser} en étoile filante ! ⭐",
    "La victoire de {winner} plus douce qu'un massage aux pierres chaudes ! {loser} tout tendu ! 💆",
    "{winner} en mode magicien ! {loser} qui cherche encore le truc ! 🎩",
    "GG {winner} ! {loser} plus perdu que Némo ! 🐠",
    "{winner} qui écrit l'histoire ! {loser} qui lit le manuel ! 📚",
    "La victoire de {winner} plus nette qu'une photo en 4K ! {loser} en 144p ! 📸",
    "{winner} en mode Ferrari ! {loser} en tricycle ! 🏎️",
    "GG {winner} ! {loser} parti faire un tour... autour de la défaite ! 🌍",
    "{winner} qui fait un festival ! {loser} qui vend les billets ! 🎪",
    "La victoire de {winner} plus intense qu'un curry indien ! {loser} à l'eau ! 🌶️",
    "{winner} en mode satellite ! {loser} qui cherche le réseau ! 📡",
    "GG {winner} ! {loser} plus confus qu'une chauve-souris en plein jour ! 🦇",
    "{winner} en haute définition ! {loser} en mode pixel art ! 🖥️",
    "La victoire de {winner} plus sûre qu'un coffre-fort ! {loser} qui cherche le code ! 🔒",
    "{winner} en mode tsunami ! {loser} avec ses bouées ! 🌊",
    "GG {winner} ! {loser} parti hiberner... jusqu'à la prochaine défaite ! 🐻",
    "{winner} qui fait un carton plein ! {loser} qui compte les points ! 🎯",
    "La victoire de {winner} plus brillante qu'un diamant ! {loser} en strass ! 💎",
    "{winner} en mode super-héros ! {loser} qui cherche sa cape ! 🦸",
    "GG {winner} ! {loser} plus perdu qu'un poisson dans le désert ! 🐟",
    "{winner} en première classe ! {loser} en classe éco... sans bagage ! ✈️",
    "La victoire de {winner} plus fraîche qu'un sorbet en été ! {loser} qui fond ! 🍧",
    "{winner} en mode F1 ! {loser} au stand... pour toujours ! 🏁",
    "GG {winner} ! {loser} parti chercher de la motivation sur YouTube ! 📺",
    "{winner} qui fait un strike ! {loser} dans la gouttière ! 🎳",
    "La victoire de {winner} plus pure qu'un diamant ! {loser} en charbon ! 💎",
    "{winner} en mode sniper ! {loser} qui tire à côté ! 🎯",
    "GG {winner} ! {loser} plus perdu qu'un manchot dans le Sahara ! 🐧",
    "{winner} en 5G ! {loser} en 56k ! 📱",
    "La victoire de {winner} plus smooth qu'un jazz à minuit ! {loser} qui fait du bruit ! 🎷",
    "{winner} en mode chef étoilé ! {loser} qui brûle les pâtes ! 👨‍🍳",
    "GG {winner} ! {loser} parti réviser ses classiques ! 📚",
    "{winner} en direct live ! {loser} en différé ! 📺",
    "La victoire de {winner} plus naturelle que l'eau de source ! {loser} en eau trouble ! 💧",
    "{winner} en mode turbo ! {loser} à vélo ! 🚀",
    "GG {winner} ! {loser} plus confus qu'un chat sous la pluie ! 🐱",
    "{winner} en 4D ! {loser} en 2D ! 🎮",
    "La victoire de {winner} plus précise qu'un GPS ! {loser} perdu en ville ! 🗺️",
    "{winner} en mode champion ! {loser} qui garde le banc au chaud ! 🏆",
    "GG {winner} ! {loser} plus perdu qu'une aiguille dans une botte de foin ! 🌾",
    "{winner} en ultraHD ! {loser} en noir et blanc ! 📺",
    "La victoire de {winner} plus rapide que l'éclair ! {loser} qui compte les secondes ! ⚡",
    "{winner} en mode pro ! {loser} en version bêta ! 🎮",
    "GG {winner} ! {loser} plus confus qu'un pingouin au Brésil ! 🐧",
    "{winner} en mode laser ! {loser} en mode bougie ! 💡",
    "La victoire de {winner} plus fraîche que la menthe poivrée ! {loser} qui pique ! 🌿",
    "{winner} en mode fusée ! {loser} en montgolfière ! 🚀",
    "GG {winner} ! {loser} plus perdu qu'un flamant rose en Antarctique ! 🦩",
    "{winner} en 8K ! {loser} en 240p ! 🎥",
    "La victoire de {winner} plus douce qu'un nuage de coton ! {loser} qui gratte ! ☁️",
    "{winner} en mode turbo ! {loser} en mode escargot ! 🐌",
    "GG {winner} ! {loser} plus confus qu'un poisson volant ! 🐠",
    "{winner} en première page ! {loser} aux petites annonces ! 📰",
    "La victoire de {winner} plus brillante que le soleil ! {loser} à l'ombre ! ☀️",
    "{winner} en mode fusée ! {loser} à pied ! 🚀",
    "GG {winner} ! {loser} plus perdu qu'un manchot en short ! 🐧",
    "{winner} en 4K ! {loser} en 144p ! 🎮",
    "La victoire de {winner} plus nette qu'un costume sur mesure ! {loser} en pyjama ! 👔",
    "{winner} en mode pilote ! {loser} passager du fond ! ✈️",
    "GG {winner} ! {loser} plus confus qu'un poisson dans un arbre ! 🐠",
    "{winner} en mode champion ! {loser} en mode spectateur ! 🏆",
    "La victoire de {winner} plus précise qu'une horloge suisse ! {loser} en retard ! ⌚",
    "{winner} en mode ninja ! {loser} qui fait du bruit ! 🥷",
    "GG {winner} ! {loser} plus perdu qu'un pingouin dans le désert ! 🐧",
    "{winner} en direct ! {loser} en replay ! 📺",
    "La victoire de {winner} plus fraîche qu'un iceberg ! {loser} qui fond ! 🧊",
    "{winner} en mode F1 ! {loser} en vélo ! 🏎️",
    "GG {winner} ! {loser} plus confus qu'un chat dans l'eau ! 🐱",
    "{winner} en haute définition ! {loser} en basse résolution ! 🖥️",
    "La victoire de {winner} plus sûre qu'un coffre-fort ! {loser} qui cherche la clé ! 🔑",
    "{winner} en mode tsunami ! {loser} avec sa bouée canard ! 🦆",
    "GG {winner} ! {loser} parti hiberner jusqu'à la prochaine saison ! 🐻",
    "{winner} qui cartonne ! {loser} qui fait de la figuration ! 🎭",
    "La victoire de {winner} plus brillante qu'une étoile ! {loser} dans les nuages ! ⭐",
    "{winner} en mode super-héros ! {loser} qui cherche son masque ! 🦸",
    "GG {winner} ! {loser} plus perdu qu'un poisson dans le désert ! 🐠",
    "{winner} en business class ! {loser} en classe éco ! ✈️",
    "La victoire de {winner} plus fraîche qu'un sorbet ! {loser} qui fond ! 🍦",
    "{winner} en mode formule 1 ! {loser} en tricycle ! 🏎️",
    "GG {winner} ! {loser} parti chercher des excuses sur Google ! 🔍",
    "{winner} qui fait un strike ! {loser} dans le caniveau ! 🎳",
    "La victoire de {winner} plus pure que l'eau de source ! {loser} en eau trouble ! 💧",
    "{winner} en mode sniper ! {loser} qui tire avec les yeux fermés ! 🎯",
    "GG {winner} ! {loser} plus perdu qu'un surfer au pôle nord ! 🏄",
    "{winner} en 5G ! {loser} en morse ! 📡",
    "La victoire de {winner} plus douce qu'une berceuse ! {loser} qui fait du bruit ! 🎵",
    "{winner} en mode masterchef ! {loser} qui brûle l'eau ! 👨‍🍳",
    "GG {winner} ! {loser} parti apprendre les règles ! 📚",
    "{winner} en direct ! {loser} qui buffer ! 📺",
    "La victoire de {winner} plus claire que du cristal ! {loser} dans le brouillard ! 💎",
    "{winner} en mode fusée ! {loser} en mode tortue ! 🐢",
    "GG {winner} ! {loser} plus confus qu'un chat devant un concombre ! 🥒",
    "{winner} en 4D ! {loser} en point ! ⚫",
    "La victoire de {winner} plus précise qu'un archer ! {loser} qui vise les nuages ! 🏹",
    "{winner} en mode champion ! {loser} qui cherche l'entrée ! 🏆",
    "GG {winner} ! {loser} plus perdu qu'un plongeur dans le désert ! 🤿",
    "{winner} en ultraHD ! {loser} en mode dessin animé ! 🎨",
    "La victoire de {winner} plus rapide que la lumière ! {loser} à la bougie ! 💡",
    "{winner} en mode pro ! {loser} en mode tutoriel ! 🎮",
    "GG {winner} ! {loser} plus confus qu'un eskimo au Sahara ! 🏜️",
    "{winner} en mode fusée ! {loser} en ballon de baudruche ! 🎈",
    "La victoire de {winner} plus précise qu'un chirurgien ! {loser} avec des moufles ! 🧤",
    "{winner} en mode astronaute ! {loser} qui cherche sa combinaison ! 👨‍🚀",
    "GG {winner} ! {loser} plus perdu qu'un snowboarder à la plage ! 🏂",
    "{winner} en 8K ! {loser} en gravure rupestre ! 🗿",
    "La victoire de {winner} plus douce qu'un nuage ! {loser} dans la tempête ! ⛈️",
    "{winner} en mode supersonique ! {loser} en mode escargot ! 🐌",
    "GG {winner} ! {loser} plus confus qu'un poisson dans un arbre ! 🎄",
    "{winner} en première classe ! {loser} en soute ! ✈️",
    "La victoire de {winner} plus brillante que les projecteurs ! {loser} dans l'ombre ! 💡",
    "{winner} en mode fusée ! {loser} en mode vélo rouillé ! 🚲",
    "GG {winner} ! {loser} plus perdu qu'un pingouin au carnaval ! 🎭",
    "{winner} en 4K ! {loser} en dessin animé des années 60 ! 📺",
    "La victoire de {winner} plus nette qu'un costume trois pièces ! {loser} en peignoir ! 👔",
    "{winner} en mode capitaine ! {loser} moussaillon malade ! ⛵",
    "GG {winner} ! {loser} plus confus qu'un poisson dans le désert ! 🐠",
    "{winner} en mode légende ! {loser} en mode conte de fées ! 📖",
    "La victoire de {winner} plus précise qu'un horloger suisse ! {loser} sans montre ! ⌚",
    "{winner} en mode samouraï ! {loser} avec une épée en plastique ! ⚔️",
    "GG {winner} ! {loser} plus perdu qu'un morse au Sahara ! 🦭",
    "{winner} en direct ! {loser} en différé de 3 jours ! 📅",
    "La victoire de {winner} plus fraîche qu'un igloo ! {loser} qui transpire ! 🥵",
    "{winner} en mode F1 ! {loser} en mode petit train ! 🚂",
    "GG {winner} ! {loser} plus confus qu'un chat dans une piscine ! 🏊",
    "{winner} en 4K HDR ! {loser} en noir et blanc granuleux ! 📺",
    "La victoire de {winner} plus sûre qu'un bunker ! {loser} à découvert ! 🏰",
    "{winner} en mode tsunami ! {loser} avec un parapluie ! ☔",
    "GG {winner} ! {loser} parti hiberner jusqu'au prochain millénaire ! 💤",
    "{winner} qui cartonne ! {loser} qui fait le carton ! 📦",
    "La victoire de {winner} plus brillante qu'un phare ! {loser} dans le brouillard ! 🏮",
    "{winner} en mode super-héros ! {loser} qui cherche son costume ! 🦸",
    "GG {winner} ! {loser} plus perdu qu'une mouette dans le désert ! 🦅",
    "{winner} en jet privé ! {loser} en montgolfière percée ! 🎈",
    "La victoire de {winner} plus fraîche qu'un iceberg ! {loser} sur le Titanic ! 🚢",
    "{winner} en mode pilote de chasse ! {loser} en ULM ! ✈️",
    "GG {winner} ! {loser} parti chercher des excuses sur Mars ! 🚀",
    "{winner} qui fait un home run ! {loser} qui cherche la balle ! ⚾",
    "La victoire de {winner} plus pure qu'un diamant ! {loser} en plastique ! 💎",
    "{winner} en mode pro gamer ! {loser} qui cherche le bouton ON ! 🎮",
    "GG {winner} ! {loser} plus perdu qu'un cosmonaute sans GPS ! 👨‍🚀",
    "{winner} en 8K ! {loser} en 8 bits ! 🕹️",
    "La victoire de {winner} plus smooth qu'un jazz à minuit ! {loser} qui fait du bruit ! 🎷",
    "{winner} en mode chef étoilé ! {loser} qui mange des nouilles instantanées ! 🍜",
    "GG {winner} ! {loser} parti réviser les bases ! 📚",
    "{winner} en streaming 4K ! {loser} en connexion dial-up ! 📡",
    "La victoire de {winner} plus naturelle que l'air pur ! {loser} en zone polluée ! 🌬️",
    "{winner} en mode supersonique ! {loser} à dos de tortue ! 🐢",
    "GG {winner} ! {loser} plus confus qu'un panda dans une discothèque ! 🐼",
    "{winner} en VR ! {loser} en 2D ! 🥽",
    "La victoire de {winner} plus précise qu'un laser ! {loser} qui vise avec les yeux fermés ! 🎯",
    "{winner} en mode légende ! {loser} encore en tutoriel ! 🎮",
    "GG {winner} ! {loser} plus perdu qu'un manchot au carnaval de Rio ! 🎭",
    "{winner} en 16K ! {loser} en papier carbone ! 📄",
    "La victoire de {winner} plus rapide qu'un TGV ! {loser} en patins à roulettes ! 🚅",
    "{winner} en mode expert ! {loser} qui lit encore le manuel ! 📖",
    "GG {winner} ! {loser} plus confus qu'un koala sous la pluie ! 🐨",
    "{winner} en mode satellite ! {loser} avec des signaux de fumée ! 💨",
    "La victoire de {winner} plus fraîche que la banquise ! {loser} au sauna ! 🧊",
    "{winner} en mode navette spatiale ! {loser} en montgolfière ! 🚀",
    "GG {winner} ! {loser} plus perdu qu'un yéti à la plage ! 🏖️",
    "{winner} en réalité augmentée ! {loser} en croquis ! ✏️",
    "La victoire de {winner} plus douce qu'un câlin de koala ! {loser} qui pique ! 🐨",
    "{winner} en mode turbo ! {loser} en mode économie d'énergie ! 🔋",
    "GG {winner} ! {loser} plus confus qu'un DJ sans électricité ! 🎧",
    "{winner} en couverture ! {loser} en page 404 ! 📰",
    "La victoire de {winner} plus brillante qu'un feu d'artifice ! {loser} avec des allumettes ! 🎆",
    "{winner} en mode NASA ! {loser} avec une boussole cassée ! 🧭",
    "GG {winner} ! {loser} plus perdu qu'un vampire au soleil ! 🧛",
    "{winner} en 12K ! {loser} en flipbook ! 📚",
    "La victoire de {winner} plus nette qu'un costume sur mesure ! {loser} en sac poubelle ! 👔",
    "{winner} en mode commandant ! {loser} en stage d'observation ! 👨‍✈️",
    "GG {winner} ! {loser} plus confus qu'un poisson dans un aquarium vide ! 🐠",
    "{winner} en mode champion olympique ! {loser} en compétition de village ! 🏅",
    "La victoire de {winner} plus précise qu'un thermomètre médical ! {loser} qui estime à l'œil ! 🌡️",
    "{winner} en mode samouraï ! {loser} avec un cure-dent ! 🥢",
    "GG {winner} ! {loser} plus perdu qu'un phoque dans le désert ! 🦭",
    "{winner} en temps réel ! {loser} avec 999ms de ping ! 🌐",
    "La victoire de {winner} plus fraîche que la menthe polaire ! {loser} qui brûle ! 🌿",
    "{winner} en Formule 1 ! {loser} en kart à pédales ! 🏎️",
    "GG {winner} ! {loser} plus confus qu'un chat sur un skateboard ! 🛹",
    "{winner} en ultra-définition ! {loser} en mode pixel art ! 🖼️",
    "La victoire de {winner} plus sûre qu'un bunker anti-atomique ! {loser} sous une tente ! ⛺",
    "{winner} en mode ouragan ! {loser} avec un éventail ! 🌪️",
    "GG {winner} ! {loser} parti hiberner sur Mars ! 🚀",
    "{winner} qui explose les scores ! {loser} qui compte sur ses doigts ! 🔢",
    "La victoire de {winner} plus brillante qu'une supernova ! {loser} en veilleuse ! 💫",
    "{winner} en mode Avenger ! {loser} en cosplay carton ! 🦸",
    "GG {winner} ! {loser} plus perdu qu'un astronaute sans combinaison ! 👨‍🚀",
    "{winner} en classe affaires ! {loser} en soute à bagages ! ✈️",
    "La victoire de {winner} plus fraîche qu'un congélateur ! {loser} au micro-ondes ! ❄️",
    "{winner} en mode Top Gun ! {loser} en mode paper plane ! ✈️",
    "GG {winner} ! {loser} parti chercher des excuses dans une autre dimension ! 🌌",
    "{winner} qui fait un perfect ! {loser} qui cherche la manette ! 🎮",
    "La victoire de {winner} plus pure que l'eau des glaciers ! {loser} en eau de vaisselle ! 💧",
    "{winner} en mode tireur d'élite ! {loser} qui vise les nuages ! 🎯",
    "GG {winner} ! {loser} plus perdu qu'un plombier sur Mars ! 👨‍🔧",
    "{winner} en fibre optique ! {loser} en pigeon voyageur ! 🐦",
    "La victoire de {winner} plus douce qu'une berceuse de sirène ! {loser} qui fait du karaoké ! 🎤",
    "{winner} en mode chef trois étoiles ! {loser} qui brûle des surgelés ! 👨‍🍳",
    "GG {winner} ! {loser} parti apprendre à compter ! 🔢",
    "{winner} en live mondial ! {loser} en rediffusion locale ! 📺",
    "La victoire de {winner} plus claire que le cristal ! {loser} dans la purée de pois ! 🌫️",
    "{winner} en mode avion supersonique ! {loser} en mode cerf-volant ! 🪁",
    "GG {winner} ! {loser} plus confus qu'un pingouin au hammam ! 🐧",
    "{winner} en 5D ! {loser} en point de croix ! 🧵",
    "La victoire de {winner} plus précise qu'un tir de sniper ! {loser} qui joue aux fléchettes ! 🎯",
    "{winner} en mode champion du monde ! {loser} qui cherche encore les règles ! 🏆",
    "GG {winner} ! {loser} plus perdu qu'un sousmarin dans le Sahara ! 🌵",
    "{winner} en définition quantique ! {loser} en peinture rupestre ! 🎨",
    "La victoire de {winner} plus rapide que la 5G ! {loser} en mode pigeon voyageur ! 📡",
    "{winner} en mode dieu du game ! {loser} en mode rage quit ! 🎮",
    "GG {winner} ! {loser} plus confus qu'un esquimau à l'équateur ! 🌡️"
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
