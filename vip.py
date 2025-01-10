import discord
import json
import os
from discord import TextChannel, Guild

NOTIFICATION_CHANNEL_ID = 1323220160253001761

# Liste des rôles VIP
VIP_ROLE_MAPPING = {
    1: {
        "T1": "VIP 1 Tiliwan1",
        "T2": "VIP 1 Tiliwan2",
        "O1": "VIP 1 Oshimo",
        "H1": "VIP 1 Herdegrize",
        "E1": "VIP 1 Euro"
    },
    2: {
        "T1": "VIP 2 Tiliwan1",
        "T2": "VIP 2 Tiliwan2",
        "O1": "VIP 2 Oshimo",
        "H1": "VIP 2 Herdegrize",
        "E1": "VIP 2 Euro"
    },
    3: {
        "T1": "VIP 3 Tiliwan1",
        "T2": "VIP 3 Tiliwan2",
        "O1": "VIP 3 Oshimo",
        "H1": "VIP 3 Herdegrize",
        "E1": "VIP 3 Euro"
    }
}

# Liste des paliers VIP
VIP_TIERS = {
    1: 4000,
    2: 10000,
    3: 20000
}

# Liste des ID des rôles interdits de recevoir un VIP
FORBIDDEN_ROLES = [
    1163157667674603582,  # ID du rôle "Croupiers"
    1163157357799415992   # ID du rôle "Lead"
]

MAPPING_SERVER_FILE = {
    "T1": "T1.json",
    "T2": "T2.json",
    "O1": "O1.json",
    "H1": "H1.json",
    "E1": "E1.json"
}

def ensure_forbidden_users_file_exists():
    """
    Vérifie si le fichier forbidden_vip_users.json existe et le crée avec un contenu vide si nécessaire.
    """
    file_name = "forbidden_vip_users.json"
    if not os.path.exists(file_name):
        print(f"📁 Le fichier {file_name} n'existe pas. Création en cours...")
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)  # Fichier vide avec un dictionnaire
        print(f"✅ Fichier {file_name} créé avec succès.")
    else:
        print(f"✔️ Le fichier {file_name} existe déjà.")

def save_forbidden_vip_users(forbidden_users):
    """
    Sauvegarde la liste des utilisateurs interdits dans le fichier forbidden_vip_users.json.
    """
    file_name = "forbidden_vip_users.json"
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(forbidden_users, f, indent=4, ensure_ascii=False)
    print(f"✅ Liste des utilisateurs interdits sauvegardée dans {file_name}.")

async def assign_vip_role(member, server_name, vip_tier, guild: discord.Guild):
    """
    Assigne le rôle VIP au membre, enregistre les données dans assigned_roles.json,
    et envoie une notification dans un salon dédié.
    """
    print(f"🔍 Attribution du rôle VIP pour {member.name} (ID : {member.id})")
    
    # Vérifier si l'utilisateur est interdit
    with open("forbidden_vip_users.json", "r") as f:
        forbidden_users = json.load(f)
        if str(member.id) in forbidden_users:
            print(f"🚫 Utilisateur {member.name} interdit de VIP")
            return
            
    role_name = VIP_ROLE_MAPPING.get(vip_tier, {}).get(server_name, None)

    if role_name:
        role = discord.utils.get(member.guild.roles, name=role_name)
        if role:
            if role not in member.roles:
                try:
                    await member.add_roles(role)
                    print(f"✅ Rôle {role.name} attribué à {member.name}.")

                    # Prépare le message
                    message = f"🎉 Félicitations {member.mention} ! Vous avez reçu le rôle **{role.name}** pour votre participation sur le serveur **{server_name}**."

                    # Récupérer le salon dédié via son ID
                    notification_channel = guild.get_channel(NOTIFICATION_CHANNEL_ID)
                    if notification_channel:
                        await notification_channel.send(message)  # Envoi dans le salon dédié
                        print(f"📩 Notification envoyée dans le salon {notification_channel.name}.")
                    else:
                        print(f"❌ Le salon avec l'ID {NOTIFICATION_CHANNEL_ID} est introuvable.")

                    # Enregistrement des données
                    data = load_assigned_roles()
                    user_data = data["users"].get(str(member.id), {"username": member.name, "roles": []})
                    if role.name not in user_data["roles"]:
                        user_data["roles"].append(role.name)
                    data["users"][str(member.id)] = user_data
                    save_assigned_roles(data)

                except discord.Forbidden:
                    print(f"❌ Permissions insuffisantes pour attribuer le rôle {role.name} à {member.name}.")
                except Exception as e:
                    print(f"❌ Erreur inattendue : {e}")
            else:
                print(f"⚠️ {member.name} possède déjà le rôle {role.name}.")
        else:
            print(f"❌ Le rôle {role_name} n'existe pas sur le serveur {member.guild.name}.")
    else:
        print(f"❌ Aucun rôle trouvé pour le serveur {server_name} et le niveau VIP {vip_tier}.")

async def check_vip_status(file_name, channel: discord.TextChannel):
    """
    Vérifie et met à jour les statuts VIP pour les utilisateurs depuis Replit DB,
    et attribue les rôles VIP sur Discord.
    """
    from replit import db
    server_name = file_name.replace('.json', '')
    print(f"🔄 Lecture des données pour le serveur : {server_name}...")

    try:
        server_data = db.get(server_name)
        if not server_data:
            print(f"📝 Initialisation des données pour {server_name}")
            server_data = {
                "serveur": server_name,
                "nombre_de_jeux": 0,
                "mises_totales_avant_commission": "0 jetons",
                "gains_totaux": "0 jetons",
                "commission_totale": "0 jetons",
                "utilisateurs": {},
                "hôtes": {},
                "croupiers": {}
            }
            db[server_name] = server_data
    except Exception as e:
        print(f"❌ Une erreur est survenue : {e}")


        users = server_data.get("utilisateurs", {})
        print(f"🔍 Utilisateurs trouvés : {users}")

        if not users:
            print(f"ℹ️ Aucun utilisateur trouvé pour le serveur {server_name}")
            return
            
        for user_id, user_data in users.items():
            print(f"🔍 Utilisateur {user_id} : {user_data}")
            try:
                # Extraire la mise totale
                total_bets = int(user_data.get("total_bets", "0 jetons").split(" ")[0])

                # Calculer le palier VIP
                new_vip_tier = calculate_vip_tier(total_bets)

                if new_vip_tier:
                    # Vérifiez que le membre est présent dans le serveur
                    try:
                        member = await channel.guild.fetch_member(int(user_id))
                        # Assigner le rôle VIP en fonction du serveur et du niveau VIP
                        server_name = file_name.split('.')[0]  # Extrait "T1" de "T1.json"
                        await assign_vip_role(member, server_name, new_vip_tier, channel.guild)
                    except discord.NotFound:
                        print(f"❌ Le membre {user_id} n'a pas pu être trouvé.")
                        continue  # Correct ici car dans une boucle for
            except ValueError:
                print(f"❌ Erreur de format pour les mises de l'utilisateur {user_id}. Ignoré.")
                continue


            
            # Assigner le rôle VIP en fonction du serveur et du niveau VIP
            server_name = file_name.split('.')[0]  # Extrait "T1" de "T1.json"
            await assign_vip_role(member, server_name, new_vip_tier, channel.guild)


def load_server_json(file_name):
    """
    Charge les données depuis Replit DB.
    """
    from replit import db
    server_name = file_name.replace('.json', '')
    
    try:
        data = db.get(server_name)
        if data is None:
            print(f"📝 Initialisation des données pour {server_name}")
            initial_data = {
                "serveur": server_name,
                "nombre_de_jeux": 0,
                "mises_totales_avant_commission": "0 jetons",
                "gains_totaux": "0 jetons",
                "commission_totale": "0 jetons",
                "utilisateurs": {},
                "hôtes": {},
                "croupiers": {}
            }
            db[server_name] = initial_data
            return initial_data
        return dict(data)
    except Exception as e:
        print(f"❌ Erreur lors du chargement des données {server_name}: {e}")
        return {}

def calculate_vip_tier(total_bets):
    """
    Calcule le palier VIP en fonction des mises totales.
    """
    for tier, threshold in sorted(VIP_TIERS.items(), reverse=True):
        if total_bets >= threshold:
            return tier
    return None

def load_forbidden_vip_users():
    """
    Charge les utilisateurs interdits du fichier forbidden_vip_users.json.
    """
    file_name = "forbidden_vip_users.json"
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Fichier des utilisateurs interdits introuvable : {file_name}")
        return {}
    except json.JSONDecodeError:
        print(f"⚠️ Erreur de format dans le fichier JSON des utilisateurs interdits.")
        return {}

def add_forbidden_user(user_id, member, role_name, reason="Non spécifiée"):
    """
    Ajoute un utilisateur interdit dans le fichier JSON, avec son username, ses rôles et la raison.
    """
    file_name = "forbidden_vip_users.json"

    # Si le fichier n'existe pas, le créer avec un dictionnaire vide
    if not os.path.exists(file_name):
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)

    # Charger les membres interdits existants
    with open(file_name, "r", encoding="utf-8") as f:
        forbidden_users = json.load(f)

    # Ajouter ou mettre à jour l'utilisateur dans la liste
    if user_id in forbidden_users:
        existing_roles = forbidden_users[user_id].get("roles", [])
        if role_name not in existing_roles:
            forbidden_users[user_id]["roles"].append(role_name)
            forbidden_users[user_id]["reason"] = reason  # mettre à jour la raison
            print(f"✅ Rôle {role_name} ajouté à {member.name} avec la raison : {reason}")
        else:
            print(f"⚠️ {member.name} a déjà ce rôle dans la liste des interdits.")
    else:
        forbidden_users[user_id] = {
            "username": member.name,  # Ajouter le username
            "roles": [role_name],  # Ajouter le rôle attribué
            "reason": reason  # Ajouter la raison
        }
        print(f"✅ Utilisateur {member.name} ajouté à la liste des interdits avec la raison : {reason}")

    # Sauvegarder la liste mise à jour
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(forbidden_users, f, indent=4, ensure_ascii=False)


def save_assigned_roles(data):
    """
    Sauvegarde les données des utilisateurs dans le fichier assigned_roles.json.
    """
    file_name = "assigned_roles.json"
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"✅ Données des rôles attribués sauvegardées dans {file_name}.")


def load_assigned_roles():
    """
    Charge les données des utilisateurs depuis le fichier assigned_roles.json.
    """
    file_name = "assigned_roles.json"
    if not os.path.exists(file_name):
        print(f"📁 Le fichier {file_name} n'existe pas. Création en cours...")
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump({"users": {}}, f, indent=4, ensure_ascii=False)
        return {"users": {}}

    try:
        with open(file_name, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"❌ Erreur de format dans le fichier {file_name}. Réinitialisation.")
        return {"users": {}}
