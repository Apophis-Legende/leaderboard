import discord
from discord.ext import commands
from flask import Flask, render_template, jsonify, request
import threading
import os
import json
import requests
from logique import process_giveaway_data, load_json, save_json
from data_manager import load_json, save_json, extract_user_data, list_all_data
from discord.ui import View, Select
from vip import check_vip_status, MAPPING_SERVER_FILE, FORBIDDEN_ROLES, load_assigned_roles, load_forbidden_vip_users
from discord import app_commands
from discord import Interaction
from delette import delete_giveaway
from add import add_giveaway_data
import re
from modif import process_giveaway
from replit import db


# Configuration du bot avec intentions
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Afficher le contenu de la DB
list_all_data()

def get_json_file_from_message(server_name):
    """
    Retourne le fichier JSON associé au serveur détecté (ex: T1 -> T1.json).
    """
    return MAPPING_SERVER_FILE.get(server_name)

MAPPING_SERVER_FILE = {
    "T1": "T1.json",
    "T2": "T2.json",
    "O1": "O1.json",
    "H1": "H1.json",
    "E1": "E1.json"
}


# Configuration de Flask pour le serveur web
app = Flask(__name__)

@app.route('/update_data', methods=["POST"])
def update_data():
    """Endpoint pour recevoir des mises à jour depuis le bot Discord."""
    try:
        data = request.json  # Récupérer les données envoyées en JSON

        if not data:
            return jsonify({"error": "Aucune donnée reçue ou JSON invalide."}), 400

        if not isinstance(data, dict):
            return jsonify({"error": "Les données doivent être un objet JSON valide."}), 400

        return jsonify({"message": "Données mises à jour avec succès"}), 200

    except Exception as e:
        app.logger.error(f"Erreur dans /update_data : {e}")
        return jsonify({"error": f"Une erreur est survenue : {e}"}), 500

def load_json(filename):
    """
    Simule la lecture d'un fichier JSON en utilisant Replit DB.
    """
    try:
        # Charger depuis Replit DB comme si c'était un fichier
        data = db[filename] if filename in db else None
        if data is None:
            # Structure par défaut si le "fichier" n'existe pas
            data = {
                "serveur": filename.replace(".json", ""),
                "nombre_de_jeux": 0,
                "mises_totales_avant_commission": "0 jetons",
                "gains_totaux": "0 jetons",
                "commission_totale": "0 jetons",
                "utilisateurs": {},
                "hôtes": {},
                "croupiers": {}
            }
            db[filename] = data  # Sauvegarder la structure par défaut
        return data
    except Exception as e:
        print(f"❌ Erreur lors du chargement des données {filename}: {e}")
        return None

@app.route('/')
def index():
    """Route pour afficher la page HTML."""
    return render_template('index.html')

@app.route('/api/check_forbidden', methods=["GET"])
def check_forbidden():
    """API pour vérifier si un utilisateur est interdit"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID manquant"}), 400

    try:
        forbidden_users = load_forbidden_vip_users()
        print("Contenu de la DB forbidden_vip_users:", forbidden_users)
        is_forbidden = user_id in forbidden_users
        return jsonify({
            "is_forbidden": is_forbidden,
            "details": forbidden_users.get(user_id) if is_forbidden else None
        })
    except Exception as e:
        print(f"Erreur lors de la vérification des utilisateurs interdits: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/vip_status', methods=["GET"])
def get_vip_status():
    """API pour obtenir le statut VIP d'un utilisateur"""
    from format_utils import get_highest_vip
    user_id = request.args.get('user_id')
    server = request.args.get('server')
    print(f"🔍 Requête VIP reçue - Serveur: {server}, User ID: {user_id}")
    server_code = server.replace("Tiliwan1", "T1").replace("Tiliwan2", "T2").replace("Oshimo", "O1").replace("Herdegrize", "H1").replace("Euro", "E1")
    vip_data = get_highest_vip(user_id, server_code)
    return jsonify(vip_data)

@app.route('/api/vip_commissions', methods=["GET"])
def get_vip_commissions():
    """API pour calculer et obtenir les commissions VIP"""
    from commission_calculator import calculate_vip_commissions  # Import de la fonction adaptée

    # Récupération des paramètres
    server = request.args.get('server')
    print(f"🔍 Requête pour les commissions VIP reçue - Serveur: {server}")

    # Vérification du paramètre serveur
    if not server:
        print("❌ Paramètre 'server' manquant")
        return jsonify({"error": "Paramètre 'server' manquant"}), 400

    # Mapping des noms de serveur vers les codes internes
    server_code = server.replace("Tiliwan1", "T1").replace("Tiliwan2", "T2").replace("Oshimo", "O1").replace("Herdegrize", "H1").replace("Euro", "E1")
    print(f"🔍 Code serveur après mapping : {server_code}")

    # Appel à la fonction de calcul des commissions
    commissions = calculate_vip_commissions(server_code)

    # Vérification des résultats
    if commissions["total"] == 0:
        print(f"ℹ️ Pas de commissions disponibles pour le serveur : {server_code}")
        return jsonify({"message": "Aucune commission à redistribuer", "data": commissions}), 200

    # Retourner les résultats
    print(f"✅ Commissions calculées pour {server_code} : {commissions}")
    return jsonify(commissions)

@app.route('/api/leaderboard', methods=["GET"])
def get_leaderboard():
    """API pour fournir les données JSON à la page."""
    server = request.args.get('server')

    if not server:
        return jsonify({"error": "Paramètre 'server' manquant dans la requête."}), 400

    file_name = MAPPING_SERVER_FILE.get(server.replace("Tiliwan1", "T1").replace("Tiliwan2", "T2").replace("Oshimo", "O1").replace("Herdegrize", "H1").replace("Euro", "E1"))
    if not file_name:
        return jsonify({"error": f"Serveur '{server}' non reconnu."}), 404

    print(f"🔍 Requête pour le fichier JSON : {file_name}")

    try:
        from replit import db
        print(f"🔍 Tentative de connexion à la base de données Replit...")
        # Vérification explicite de la connexion à la base de données
        if not db:
            print("❌ Erreur: Impossible de se connecter à la base de données Replit")
            return jsonify({"error": "Erreur de connexion à la base de données"}), 500
        print("✅ Connexion à la base de données Replit réussie")
            
        # Charger depuis Replit db avec vérification
        data = db.get(file_name, {
            "serveur": server,
            "nombre_de_jeux": 0,
            "mises_totales_avant_commission": "0 jetons", 
            "gains_totaux": "0 jetons",
            "commission_totale": "0 jetons",
            "utilisateurs": {},
            "hôtes": {},
            "croupiers": {}
        })
        
        # Convertir récursivement les ObservedDict en dictionnaires standard
        def convert_to_dict(obj):
            if hasattr(obj, 'value'):  # Pour ObservedDict/ObservedList
                obj = obj.value
            if isinstance(obj, dict):
                return {k: convert_to_dict(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_dict(item) for item in obj]
            return obj
            
        formatted_data = convert_to_dict(data)
        print(f"✅ Données chargées: {formatted_data}")

        response = jsonify(formatted_data)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    except Exception as e:
        print(f"❌ Erreur lors du traitement du fichier {file_name} : {e}")
        return jsonify({"error": f"Une erreur est survenue lors de la lecture du fichier {file_name} : {str(e)}"}), 500

def is_admin():
    async def predicate(interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            print(f"🚫 {interaction.user} n'a pas la permission d'administrateur.")
            return False
        return True
    return app_commands.check(predicate)

def is_in_guild():
    async def predicate(interaction: discord.Interaction):
        if interaction.guild is None:
            print(f"🚫 {interaction.user} tente d'exécuter une commande en DM.")
            return False
        return True
    return app_commands.check(predicate)

def run_flask():
    # Assurez-vous que Flask écoute sur 0.0.0.0 pour permettre l'accès externe
    app.run(host='0.0.0.0', port=3000, debug=False)

# ID du bot cible
TARGET_BOT_ID = 294882584201003009  # ID du GiveawayBot
# Mapping entre les serveurs et leurs fichiers JSON

SERVER_FILE_MAPPING = {
    "Tiliwan1": "T1.json",
    "Tiliwan2": "T2.json",
    "Oshimo": "O1.json",
    "Herdegrize": "H1.json",
    "Euro": "E1.json"
}

def extract_server_from_message(message_content):
    """
    Extrait le nom du serveur à partir d'un message contenant des informations de giveaway.
    """
    # Liste des serveurs connus
    known_servers = ["Tiliwan1", "Tiliwan2", "Oshimo", "Herdegrize", "Euro"]
    for server in known_servers:
        if server in message_content:
            return server
    return None


def load_server_json(server):
    """Charge les données du fichier JSON correspondant au serveur."""
    file_name = SERVER_FILE_MAPPING.get(server)
    if not file_name:
        raise ValueError(f"Serveur '{server}' non reconnu.")

    if not os.path.exists(file_name):
        print(f"❌ Fichier JSON pour le serveur '{server}' introuvable : {file_name}")
        return {}  # Retourne un dictionnaire vide si le fichier n'existe pas

    with open(file_name, "r", encoding="utf-8") as f:
        return json.load(f)  # Charge les données JSON

async def send_data_to_flask(data):
    """Met à jour directement les données dans Flask."""
    try:
        print("✅ Mise à jour des données...")
        return {"status": "success"}
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour des données : {e}")
        raise

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que : {bot.user}")
    ensure_forbidden_users_exists()
    print(f"✅ Bot connecté en tant que : {bot.user}")
    print(f"✅ ID du bot : {bot.user.id}")

    try:
        synced = await bot.tree.sync()
        print(f"✅ Commandes slash synchronisées : {len(synced)}")
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation des commandes slash : {e}")

    # Vérifier et initialiser les fichiers JSON
    verifier_et_initialiser_fichiers_json(MAPPING_SERVER_FILE)

    print("✅ Vérification et initialisation des fichiers JSON terminées.")

async def send_data_to_flask(data):
    """Envoie des données JSON au serveur Flask."""
    try:
        url = "http://127.0.0.1:3000/update_data"  # Endpoint Flask
        headers = {'Content-Type': 'application/json'}

        # Vérifiez que les données sont un dictionnaire
        if not isinstance(data, dict):
            raise ValueError("Les données à envoyer doivent être un dictionnaire JSON.")

        # Envoyer une requête POST avec les données
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Lève une exception pour les erreurs HTTP

        print(f"✅ Données envoyées à Flask avec succès : {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de l'envoi des données à Flask : {e}")
        raise

async def download_json_from_summary(url, channel):
    """
    Télécharge les données JSON d'un giveaway, traite les données et les envoie au serveur Flask.
    Ajoute une validation interactive par l'hôte si des erreurs sont détectées.
    """
    print(f"🌐 Téléchargement du JSON depuis : {url}")
    api_url = url.replace("https://giveawaybot.party/summary#", "https://summary-api.giveawaybot.party/?")

    try:
        # Télécharger les données brutes depuis l'API
        response = requests.get(api_url)
        response.raise_for_status()
        raw_data = response.json()

        print(f"✅ JSON brut récupéré avec succès : {raw_data}")

        # Vérifiez que les données brutes sont valides
        if not raw_data or not isinstance(raw_data, dict):
            raise ValueError("Les données JSON brutes récupérées ne sont pas valides ou sont vides.")

        # Appeler le traitement des données
        processed_data = await process_giveaway_data(raw_data, channel)

        # Vérifiez que les données traitées sont valides
        if not processed_data:
            raise ValueError("Les données traitées sont vides ou nulles.")
        if not isinstance(processed_data, dict):
            raise ValueError(f"Les données traitées ne sont pas un dictionnaire. Type actuel : {type(processed_data)}")

        # Envoyer les données traitées au serveur Flask
        print("🚀 Envoi des données au serveur Flask...")
        await send_data_to_flask(processed_data)

        # Confirmer l'envoi réussi au canal Discord
        await channel.send(f"🎉 Les données du giveaway ont été enregistrées !")

    except requests.exceptions.RequestException as req_err:
        # Gestion des erreurs liées à la requête HTTP
        print(f"❌ Erreur HTTP lors de la récupération des données JSON : {req_err}")
        await channel.send("⚠️ Erreur lors de la récupération des données JSON.")

    except ValueError as val_err:
        # Gestion des erreurs liées au format des données
        print(f"❌ Erreur de format des données : {val_err}")
        await channel.send(f"⚠️ Erreur lors du traitement des données : {val_err}")

    except Exception as e:
        # Gestion générique des erreurs
        print(f"❌ Une erreur inattendue est survenue : {e}")
        await channel.send("⚠️ Une erreur inattendue est survenue lors du traitement des données JSON.")

        # Validation interactive par l’hôte en cas d’erreur majeure
        view = ConfirmDataView(channel.guild, raw_data)
        await channel.guild.owner.send("❓ Une erreur est survenue lors du traitement des données. Voulez-vous valider ou rejeter les données suivantes :", view=view)
        await view.wait()

        if view.value:
            await channel.send("✅ Données validées par l'hôte, traitement en cours.")
            # Recommencez le traitement avec les données validées
            processed_data = await process_giveaway_data(raw_data, channel)
            if processed_data:
                await send_data_to_flask(processed_data)
                await channel.send("🎉 Données validées et enregistrées avec succès.")
        else:
            await channel.send("❌ Données rejetées par l'hôte.")


# Gestion des messages : suivre uniquement ceux du bot cible
@bot.event
async def on_message(message):
    print(f"\n🚨 Nouveau message reçu 🚨")
    print(f"📨 Contenu du message : {message.content}")
    print(f"👤 Auteur : {message.author} (ID : {message.author.id})")

    # Ignorer tous les messages sauf ceux du bot cible
    if message.author.id != TARGET_BOT_ID:
        print("🔄 Ignoré : ce message ne provient pas du bot cible.")
        return

    print("🎯 Message suivi : ce message provient du bot cible !")

    # Vérifier si un gagnant a été annoncé
    if "won the" in message.content.lower():
        print("🎉 Un gagnant a été détecté dans le message.")
        await retrieve_previous_message_with_summary(message.channel)

        try:
            # Extraire la partie contenant le serveur depuis le message
            parts = message.content.split("won the")[-1].strip().split(" ")
            raw_server_name = parts[0]  # Récupère "T2"
            server_name = raw_server_name.strip("**")  # Supprime les `**` si présents

            print(f"📝 Serveur détecté pour VIP : {server_name}")

            # Utiliser MAPPING_SERVER_FILE pour trouver le fichier JSON correspondant
            if server_name not in MAPPING_SERVER_FILE:
                raise ValueError(f"Serveur inconnu ou non pris en charge : {server_name}")

            json_file = MAPPING_SERVER_FILE[server_name]

            # Vérifier si le fichier JSON du serveur existe et mettre à jour les VIP
            print(f"🔄 Mise à jour des statuts VIP pour le serveur {server_name} en cours...")
            await check_vip_status(json_file, message.channel)
            print(f"✅ Mise à jour des statuts VIP pour le serveur {json_file} terminée.")

        except (IndexError, ValueError) as e:
            print(f"❌ Erreur lors de l'extraction des informations VIP : {e}")
            await message.channel.send("⚠️ Impossible de déterminer le serveur pour la mise à jour VIP.")

async def update_vip_status(json_file, channel):
    """
    Met à jour les statuts VIP pour un fichier JSON donné.
    """
    print(f"🔄 Lecture des données pour le fichier {json_file}...")

    try:
        # Charger les données du fichier JSON
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        utilisateurs = data.get("utilisateurs", {})
        print(f"🔍 Utilisateurs trouvés : {utilisateurs}")

        for user_id, user_data in utilisateurs.items():
            total_bets = int(user_data["total_bets"].split(" ")[0])  # Conversion à partir de "XXXX jetons"
            vip_tier = calculate_vip_tier(total_bets)

            if vip_tier and vip_tier != user_data.get("vip_tier"):
                user_data["vip_tier"] = vip_tier
                await channel.send(
                    f"🎉 **Félicitations** <@{user_id}> : Vous avez débloqué le statut VIP {vip_tier} !"
                )

        print(f"✅ Mise à jour des statuts VIP terminée pour le fichier {json_file}.")
        await channel.send(f"✅ Mise à jour des statuts VIP pour le serveur **{json_file.replace('.json', '')}** terminée.")

    except FileNotFoundError:
        print(f"❌ Fichier introuvable : {json_file}")
        await channel.send(f"⚠️ Fichier `{json_file}` introuvable. Impossible de mettre à jour les VIP.")

    except Exception as e:
        print(f"❌ Une erreur est survenue lors de la mise à jour des VIP : {e}")
        await channel.send(f"⚠️ Une erreur est survenue lors de la mise à jour des VIP : {e}")

def extract_server_and_prize(prize_text):
    """
    Extrait le nom du serveur et le montant du prix depuis le champ 'prize'.
    Exemple : 'E1 380 blabla' -> ('E1', 380)
    """
    try:
        match = re.match(r"^(\w+)\s+(\d+)", prize_text)
        if match:
            server = match.group(1)
            prize = int(match.group(2))
            return server, prize
        else:
            raise ValueError(f"Impossible d'extraire les données de 'prize' : {prize_text}")
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction du serveur et du prix : {e}")
        return None, None

async def retrieve_previous_message_with_summary(channel):
    """
    Parcourt les 50 derniers messages pour trouver un bouton "Giveaway Summary"
    et télécharge les données associées.
    """
    print("🔍 Recherche des messages récents avec un résumé de giveaway...")
    try:
        # Parcourt les 50 derniers messages dans le canal
        async for msg in channel.history(limit=50):
            if hasattr(msg, "components") and msg.components:
                print(f"📩 Analyse des composants du message ID {msg.id}")
                for component in msg.components:
                    for button in component.children:
                        # Vérifiez si le bouton a une étiquette valide
                        if button.label and button.label.lower() == "giveaway summary":
                            if button.url:
                                print(f"🌐 Bouton 'Giveaway Summary' trouvé : {button.url}")
                                await download_json_from_summary(button.url, channel)
                                return
                            else:
                                print("⚠️ Bouton 'Giveaway Summary' trouvé, mais l'URL est absente.")
            else:
                print(f"❌ Le message ID {msg.id} ne contient pas de composants.")

        # Si aucun bouton "Giveaway Summary" n'est trouvé
        print("❌ Aucun bouton 'Giveaway Summary' trouvé dans les 50 derniers messages.")
        await channel.send("⚠️ Aucun résumé de giveaway trouvé dans les messages récents.")

    except Exception as e:
        # Gestion générique des erreurs
        print(f"❌ Une erreur inattendue est survenue dans retrieve_previous_message_with_summary : {e}")
        await channel.send(f"⚠️ Une erreur inattendue est survenue lors de la recherche du résumé : {e}")

async def process_giveaway_event(player_id, server, bets_to_add):
    """
    Met à jour les mises VIP d'un joueur après un giveaway.
    """
    # Mise à jour du statut VIP
    update_player_vip(player_id, server, bets_to_add)

    # Affichage dans les logs
    display_vip_status(player_id, server)

async def display_server_data(server, channel):
    """
    Lit les données d'un serveur depuis son fichier JSON et les affiche dans Discord.
    """
    try:
        # Lire les données du serveur
        data = load_server_json(server)

        if not data:
            await channel.send(f"⚠️ Aucune donnée trouvée pour le serveur {server}.")
            return

        # Formatage des données pour Discord
        formatted_data = json.dumps(data, indent=4, ensure_ascii=False)
        await channel.send(f"📊 Données du serveur **{server}** :\n```json\n{formatted_data}\n```")

    except ValueError as e:
        await channel.send(f"❌ Erreur : {e}")
    except Exception as e:
        await channel.send(f"❌ Une erreur inattendue est survenue : {e}")

async def handle_giveaway(raw_data, channel):
    """
    Exemple : Traite les données d'un giveaway et met à jour les VIP.
    """
    try:
        # Extraction du serveur et des informations
        server = raw_data["giveaway"]["prize"].split(" ")[0]  # Nom du serveur
        print(f"🔍 Serveur extrait : {server}")

        # Mise à jour des VIP
        await check_vip_status(server, channel)
    except Exception as e:
        print(f"❌ Erreur dans handle_giveaway : {e}")
        await channel.send(f"⚠️ Une erreur est survenue lors du traitement des données du giveaway : {e}")

def find_server_file(server, mapping):
    """
    Trouve le fichier JSON associé à un serveur à partir du mapping.
    Vérifie l'existence du fichier dans le répertoire courant.

    Args:
        server (str): Le nom du serveur (par exemple, "E1", "T1").
        mapping (dict): Mapping des serveurs vers les fichiers JSON.

    Returns:
        str: Le chemin du fichier JSON s'il existe.

    Raises:
        FileNotFoundError: Si le fichier correspondant au serveur est introuvable.
    """
    filename = mapping.get(server)
    if not filename:
        raise FileNotFoundError(f"⚠️ Le serveur '{server}' n'est pas défini dans le mapping.")

    if not os.path.exists(filename):
        raise FileNotFoundError(f"⚠️ Le fichier {filename} n'existe pas dans le répertoire courant.")

    print(f"✅ Fichier trouvé pour le serveur {server}: {filename}")
    return filename

# Événement pour synchroniser les commandes du bot
@bot.event
async def on_ready():
    try:
        # Initialiser les fichiers JSON
        for server_file in MAPPING_SERVER_FILE.values():
            if not os.path.exists(server_file):
                initial_data = {
                    "serveur": server_file.replace('.json', ''),
                    "nombre_de_jeux": 0,
                    "mises_totales_avant_commission": "0 jetons",
                    "gains_totaux": "0 jetons",
                    "commission_totale": "0 jetons",
                    "utilisateurs": {},
                    "hôtes": {},
                    "croupiers": {}
                }
                with open(server_file, 'w', encoding='utf-8') as f:
                    json.dump(initial_data, f, indent=4, ensure_ascii=False)
                print(f"✅ Fichier {server_file} créé")

        # Synchroniser les commandes
        synced = await bot.tree.sync()
        print(f"✅ Commandes slash synchronisées : {len(synced)} commandes.")
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation des commandes : {e}")

@bot.tree.command(name="modif-json", description="Extrait et transforme des données brutes JSON depuis un lien.")
@is_admin()  # Restriction aux administrateurs
@is_in_guild()  # Bloque l'accès en DM
@app_commands.describe(link="Lien vers le fichier JSON brut", prize="Nouveau prize (format : 'T1 950')")
async def modif_json(interaction: discord.Interaction, link: str, prize: str):
    await interaction.response.defer()
    
    from data_manager import verify_db_connection
    if not verify_db_connection():
        await interaction.followup.send("❌ Erreur: Impossible d'accéder à la base de données. Veuillez réessayer plus tard.")
        return

    try:
        # Appeler la fonction principale pour traiter le fichier JSON
        result = process_giveaway(link, prize)
        await interaction.followup.send(result)

    except Exception as e:
        await interaction.followup.send(f"❌ Une erreur est survenue : {str(e)}")


@bot.tree.command(name="add_giveaway", description="Ajoute les données associées à un giveaway via son lien.")
@is_admin()  # Restriction aux administrateurs
@is_in_guild()  # Bloque l'accès en DM
async def add_giveaway(interaction: discord.Interaction, link: str):
    try:
        await interaction.response.defer()  # Defer the interaction to indicate processing
        add_giveaway_data(link, MAPPING_SERVER_FILE)
        await interaction.followup.send("✅ Données ajoutées avec succès !")
    except Exception as e:
        print(f"❌ Erreur : {e}")
        # Check if the response is already done before sending a follow-up
        if not interaction.response.is_done():
            await interaction.followup.send(f"❌ Une erreur est survenue : {e}")
        else:
            await interaction.followup.send("❌ Une erreur est survenue et une réponse n’a pas pu être correctement traitée.")


@bot.tree.command(name="delete_giveaway", description="Supprime les données associées à un giveaway via son lien.")
@is_admin()  # Restriction aux administrateurs
@is_in_guild()  # Bloque l'accès en DM
async def delete_giveaway_command(interaction: discord.Interaction, link: str):
    try:
        # Marquer l'interaction comme différée
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        # Appeler la fonction pour supprimer le giveaway
        await delete_giveaway(interaction, link)

        # Vérifier si une réponse a été envoyée
        if not interaction.response.is_done():
            await interaction.response.send_message("✅ Giveaway supprimé avec succès.", ephemeral=True)
        else:
            await interaction.followup.send("✅ Giveaway supprimé avec succès.", ephemeral=True)

    except Exception as e:
        # Gérer les erreurs
        error_message = f"❌ Une erreur est survenue : {str(e)}"
        try:
            # Vérifier si une réponse a été envoyée
            if not interaction.response.is_done():
                await interaction.response.send_message(error_message, ephemeral=True)
            else:
                await interaction.followup.send(error_message, ephemeral=True)
        except discord.errors.InteractionResponded:
            # Gérer les cas où l'interaction a déjà une réponse
            print(f"Interaction déjà répondue : {error_message}")


@bot.tree.command(name="update_vip", description="Met à jour les statuts VIP pour un serveur donné.")
@is_admin()  # Restriction aux administrateurs
@is_in_guild()  # Bloque l'accès en DM
async def update_vip(interaction: discord.Interaction, server: str):
    await interaction.response.defer()
    print(f"🔄 Demande de mise à jour VIP pour le serveur {server}")

    # Ajoutez un mapping des serveurs si nécessaire
    server_mapping = {
        "Tiliwan2": "T2",
        "Tiliwan1": "T1",
        "Herdegrize": "H1",
        "Oshimo": "O1"
    }

    server_name = server_mapping.get(server, server)  # Par défaut, utilise le nom donné
    await interaction.followup.send(f"🔄 Mise à jour des statuts VIP pour le serveur **{server}** en cours...")
    await check_vip_status(server_name, interaction.channel)

@bot.tree.command(name="add_forbidden_user", description="Ajoute un membre interdit dans Replit DB.")
@is_admin()  # Restriction aux administrateurs
@is_in_guild()  # Bloque l'accès en DM
@app_commands.describe(user_id="ID du membre à interdire", reason="Raison pour laquelle ce membre est interdit.")
async def add_forbidden_user(interaction: discord.Interaction, user_id: str, reason: str):
    await interaction.response.defer()  # Indique à Discord que la commande est en cours de traitement

    from replit import db  # Importer Replit DB
    forbidden_users = db.get("forbidden_vip_users", {})

    # Vérifier si l'utilisateur est déjà dans la liste
    if user_id in forbidden_users:
        await interaction.followup.send(
            f"⚠️ L'utilisateur avec l'ID `{user_id}` est déjà dans la liste des interdits."
        )
        return

    guild = interaction.guild

    try:
        # Utilisez fetch_member pour garantir que l'utilisateur est récupéré
        member = await guild.fetch_member(int(user_id))
    except discord.NotFound:
        await interaction.followup.send(
            f"⚠️ Impossible de trouver un membre avec l'ID `{user_id}` dans cette guilde."
        )
        return

    # Extraire les rôles sous forme de liste
    roles = [role.name for role in member.roles if role.name != "@everyone"]

    # Ajouter l'utilisateur avec le username, les rôles et la raison
    forbidden_users[user_id] = {
        "username": member.name,
        "roles": roles,
        "reason": reason
    }

    # Sauvegarder les données dans Replit DB
    db["forbidden_vip_users"] = forbidden_users

    # Réponse finale
    await interaction.followup.send(
        f"✅ L'utilisateur `{member.name}` avec l'ID `{user_id}` a été ajouté à la liste des interdits.\n"
        f"📋 Rôles : {', '.join(roles)}\n"
        f"❓ Raison : {reason}"
    )


@bot.tree.command(name="list_forbidden_users", description="Affiche la liste des membres interdits dans Replit DB.")
@is_admin()  # Restriction aux administrateurs
@is_in_guild()  # Bloque l'accès en DM
async def list_forbidden_users(interaction: discord.Interaction):
    """
    Liste les membres interdits dans Replit DB.
    """
    from replit import db  # Importer Replit DB
    forbidden_users = db.get("forbidden_vip_users", {})  # Charger les utilisateurs interdits existants

    if not forbidden_users:
        await interaction.response.send_message("⚠️ Aucun membre interdit trouvé.")
        return

    # Créer une liste des utilisateurs interdits
    response = "🔒 **Liste des membres interdits :**\n"
    for user_id, data in forbidden_users.items():
        reason = data.get("reason", "Non spécifiée")
        roles = ", ".join(data.get("roles", []))
        response += f"- **{data['username']}** (ID : `{user_id}`)\n  Rôles : {roles}\n  Raison : {reason}\n\n"

    await interaction.response.send_message(response[:2000])  # Discord limite les messages à 2000 caractères.


@bot.tree.command(name="remove_forbidden_user", description="Supprime un membre de la liste des interdits dans Replit DB.")
@is_admin()  # Restriction aux administrateurs
@is_in_guild()  # Bloque l'accès en DM
@app_commands.describe(user_id="ID du membre à retirer de la liste des interdits.")
async def remove_forbidden_user(interaction: discord.Interaction, user_id: str):
    """
    Supprime un membre de la liste des interdits dans Replit DB.
    """
    from replit import db  # Importer Replit DB
    forbidden_users = db.get("forbidden_vip_users", {})  # Charger les utilisateurs interdits existants

    # Vérifier si l'utilisateur est dans la liste
    if user_id in forbidden_users:
        del forbidden_users[user_id]  # Supprimer l'utilisateur
        db["forbidden_vip_users"] = forbidden_users  # Sauvegarder les modifications

        await interaction.response.send_message(
            f"✅ L'utilisateur avec l'ID `{user_id}` a été retiré de la liste des interdits."
        )
    else:
        await interaction.response.send_message(
            f"⚠️ Aucun utilisateur avec l'ID `{user_id}` trouvé dans la liste des interdits."
        )


@bot.tree.command(name="reset_vip", description="Réinitialise les rôles VIP")
@is_admin()
@is_in_guild()
async def reset_vip(interaction: discord.Interaction):
    """Réinitialise uniquement les rôles VIP"""
    await interaction.response.defer()

    guild = interaction.guild
    data = load_assigned_roles()
    users = data.get("users", {})

    if users:
        for user_id, user_data in users.items():
            try:
                member = await guild.fetch_member(int(user_id))
                roles_to_remove = [discord.utils.get(guild.roles, name=role) for role in user_data["roles"]]
                roles_to_remove = [role for role in roles_to_remove if role is not None]

                if roles_to_remove:
                    await member.remove_roles(*roles_to_remove)
                    print(f"✅ Rôles retirés pour {member.name} : {', '.join([role.name for role in roles_to_remove])}")
            except discord.NotFound:
                print(f"❌ Membre introuvable avec l'ID {user_id}")
            except Exception as e:
                print(f"❌ Erreur pour l'utilisateur {user_id} : {e}")

    # Réinitialiser les rôles assignés dans la db
    db["assigned_roles.json"] = {"users": {}}
    
    await interaction.followup.send("✅ Réinitialisation des rôles VIP effectuée")

@bot.tree.command(name="reset_lb", description="Réinitialise les données des leaderboards")
@is_admin()
@is_in_guild()
async def reset_lb(interaction: discord.Interaction):
    """Réinitialise uniquement les données des leaderboards"""
    await interaction.response.defer()

    initial_data = {
        "serveur": "",
        "nombre_de_jeux": 0,
        "mises_totales_avant_commission": "0 jetons",
        "gains_totaux": "0 jetons",
        "commission_totale": "0 jetons",
        "utilisateurs": {},
        "hôtes": {},
        "croupiers": {}
    }

    servers = ["T1", "T2", "O1", "H1", "E1"]
    for server in servers:
        try:
            data = initial_data.copy()
            data["serveur"] = server
            db[f"{server}.json"] = data
            print(f"✅ Données {server} réinitialisées")
        except Exception as e:
            print(f"❌ Erreur pour {server}: {e}")

    await interaction.followup.send("✅ Réinitialisation des leaderboards effectuée")

@bot.tree.command(name="host_info", description="Affiche les informations d'un hôte")
@is_admin()
@is_in_guild()
async def host_info(interaction: discord.Interaction, user_id: str):
    """Affiche les informations détaillées d'un hôte."""
    try:
        from host_info import calculate_host_stats, format_host_card
        stats = calculate_host_stats(user_id)
        if stats['username']:
            cards = format_host_card(stats)
            # Envoyer les cartes en plusieurs messages si nécessaire
            cards_list = cards.split('\n\n')
            for card in cards_list:
                if card.strip():
                    try:
                        await asyncio.sleep(1)  # Ajoute un délai de 1 seconde
                        await interaction.followup.send(card)
                    except discord.HTTPException as e:
                        if e.code == 429:  # Too Many Requests
                            retry_after = e.retry_after if hasattr(e, 'retry_after') else 5
                            await asyncio.sleep(retry_after)
                            await interaction.followup.send(card)
                        else:
                            raise
            if not interaction.response.is_done():
                await interaction.response.send_message("✅ Informations de l'hôte affichées ci-dessous.")
        else:
            await interaction.response.send_message("❌ Aucune donnée d'hôte trouvée pour cet utilisateur.")
    except Exception as e:
        if not interaction.response.is_done():
            await interaction.response.send_message(f"❌ Une erreur est survenue : {str(e)}")
        else:
            await interaction.followup.send(f"❌ Une erreur est survenue : {str(e)}")



# Lancer le bot Discord
def run_bot():
    while True:
        try:
            bot.run(os.getenv("TOKEN"))
        except discord.errors.HTTPException as e:
            if e.status == 429:  # Rate limit error
                print(f"Rate limit hit. Waiting 30 seconds before retrying...")
                import time
                time.sleep(30)
                continue
            raise e

# Exécuter Flask et Discord en parallèle
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()  # Lancer Flask dans un thread
    run_bot()  # Lancer le bot Discord