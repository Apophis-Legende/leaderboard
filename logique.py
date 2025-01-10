import discord
import os
import json
import re
from discord.ui import View, Select, Button, Modal, TextInput
from discord import Interaction
import asyncio

MAPPING_SERVER_FILE = {
    "T1": "T1.json",
    "T2": "T2.json",
    "O1": "O1.json",
    "H1": "H1.json",
    "E1": "E1.json"
}
class ServerSelectionView(View):
    def __init__(self, servers):
        super().__init__()
        self.selected_server = None
        self.add_item(ServerSelect(servers))


class ServerSelect(Select):
    def __init__(self, servers):
        super().__init__(
            placeholder="Sélectionnez un serveur...",
            options=[discord.SelectOption(label=server, value=server) for server in servers],
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_server = self.values[0]
        await interaction.response.edit_message(
            content=f"✅ Serveur sélectionné : {self.view.selected_server}",
            view=None  # Supprime le menu déroulant
        )
        self.view.stop()


# Fonction principale asynchrone pour gérer l'interaction avec l'hôte
async def handle_host_interaction(bot, channel, host):
    try:
        # Attendre la réponse de l'hôte
        response = await bot.wait_for("message", timeout=60.0, check=check_host_response)
        await channel.send(f"✅ Réponse de l'hôte reçue : {response.content}")
    except asyncio.TimeoutError:
        await channel.send("❌ Temps écoulé. Aucun serveur sélectionné.")

async def handle_unknown_server(channel, raw_data, host, servers):
    view = ServerSelectionView(servers)
    try:
        await host.send(
            "⚠️ Serveur inconnu détecté. Veuillez sélectionner le bon serveur dans la liste ci-dessous :",
            view=view,
        )
    except discord.Forbidden:
        await channel.send("❌ Impossible d'envoyer un message privé à l'hôte. Vérifiez ses paramètres.")
        return None  # Arrête si l'hôte ne peut pas être contacté

    await view.wait()

    if view.selected_server:
        raw_data["giveaway"]["prize"] = f"{view.selected_server} {raw_data['giveaway']['prize'].split(' ')[1]}"
        await channel.send(f"✅ Serveur corrigé : {view.selected_server}")
        return view.selected_server
    else:
        await channel.send("❌ Aucun serveur sélectionné. Le processus est interrompu.")
        return None

async def handle_price_correction(channel, raw_data):
    host_id = raw_data["giveaway"]["host"]["id"]
    host = await channel.guild.fetch_member(int(host_id))

    if not host:
        await channel.send("❌ Impossible de trouver l'hôte.")
        return None

    # Demander confirmation
    view = ConfirmPriceView()
    await channel.send(
        f"⚠️ L'hôte {host.mention}, êtes-vous sûr du prix `{raw_data['giveaway']['prize']}` ?",
        view=view
    )
    await view.wait()

    if view.value is True:  # Confirmé
        await channel.send("✅ Prix confirmé par l'hôte.")
        return raw_data["giveaway"]["prize"]

    elif view.value is False:  # Rejeté, ouvrir une fenêtre de saisie
        modal = PriceCorrectionModal()
        await host.send("❌ Veuillez corriger le prix :", view=modal)
        await modal.wait()

        if hasattr(modal, "corrected_prize"):
            await channel.send(f"✅ Prix corrigé par l'hôte : {modal.corrected_prize}")
            return modal.corrected_prize
        else:
            await channel.send("❌ Le prix n'a pas été corrigé.")
            return None


def extract_server_and_prize(prize_text):
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

def load_json(filename, default_data=None):
    """
    Charge un fichier JSON ou retourne les données par défaut si le fichier n'existe pas.
    """
    absolute_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    print(f"🔍 Tentative de lecture du fichier : {absolute_path}")
    if os.path.exists(absolute_path):
        with open(absolute_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            print(f"✅ Fichier chargé avec succès : {filename}")
            return data
    print(f"⚠️ Fichier non trouvé, utilisation des données par défaut : {filename}")
    return default_data or {}

def save_json(file_name, server_data):
    try:
        absolute_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
        with open(absolute_path, "w", encoding="utf-8") as f:
            json.dump(server_data, f, indent=4, ensure_ascii=False)
        print(f"✅ Données sauvegardées dans : {absolute_path}")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde de {file_name}: {e}")

def convert_amount_to_float(amount_str):
    """
    Convertit une chaîne "400 jetons" en float 400.0
    """
    return float(amount_str.split(" ")[0])

def format_amount(amount):
    """
    Convertit un float 400.0 en chaîne "400 jetons"
    """
    return f"{int(amount)} jetons"

async def process_giveaway_data(raw_data, channel):
    """
    Traite les données brutes d'un giveaway et met à jour le fichier JSON du serveur concerné.
    Demande une validation ou correction à l'hôte en cas de données non reconnues.
    """
    try:
        # Validation initiale des clés
        if "giveaway" not in raw_data or "winners" not in raw_data or "entries" not in raw_data:
            raise KeyError("Les clés 'giveaway', 'winners' ou 'entries' sont manquantes dans les données.")

        giveaway_info = raw_data["giveaway"]
        prize = giveaway_info["prize"]

        # Utiliser la fonction d'extraction
        server, gain_after_commission = extract_server_and_prize(prize)

        if server not in MAPPING_SERVER_FILE:
            try:
                # Récupérer les infos de l'hôte
                host_id = raw_data["giveaway"]["host"]["id"]
                host_username = raw_data["giveaway"]["host"]["username"]
                host = await channel.guild.fetch_member(int(host_id))

                if not host:
                    await channel.send("❌ Impossible de récupérer l'hôte.")
                    return None

                # Créer un menu déroulant pour le choix du serveur
                view = ServerSelectionView(MAPPING_SERVER_FILE.keys())

                # Envoyer une interaction initiale pour l'hôte avec le menu
                if server not in MAPPING_SERVER_FILE:
                    try:
                        # Récupérer les infos de l'hôte
                        host_id = raw_data["giveaway"]["host"]["id"]
                        host_username = raw_data["giveaway"]["host"]["username"]
                        host = await channel.guild.fetch_member(int(host_id))

                        if not host:
                            await channel.send("❌ Impossible de récupérer l'hôte.")
                            return None

                        # Notifier dans le salon du giveaway
                        await channel.send(
                            f"⚠️ Serveur non reconnu : {server}. L'hôte {host.mention}, veuillez sélectionner le serveur correct :"
                        )

                        # Afficher le menu déroulant
                        view = ServerSelectionView(MAPPING_SERVER_FILE.keys())
                        message = await channel.send("Veuillez sélectionner un serveur :", view=view)

                        # Attendre la réponse
                        await view.wait()

                        if not view.selected_server:
                            await channel.send("❌ Aucun serveur sélectionné. Le processus est interrompu.")
                            return None

                        # Mise à jour du serveur corrigé
                        server = view.selected_server
                        raw_data["giveaway"]["prize"] = f"{server} {raw_data['giveaway']['prize'].split(' ')[1]}"
                        await channel.send(f"✅ Serveur corrigé par l'hôte : {server}")

                    except discord.NotFound:
                        await channel.send(f"❌ L'hôte {host_username} n'est pas dans ce serveur.")
                        return None
                    except discord.Forbidden:
                        await channel.send(f"❌ Impossible d'envoyer un message privé à {host_username}.")
                        return None

                # Mise à jour du serveur corrigé
                server = view.selected_server
                raw_data["giveaway"]["prize"] = f"{server} {raw_data['giveaway']['prize'].split(' ')[1]}"
                await channel.send(f"✅ Serveur corrigé par l'hôte : {server}")

            except discord.NotFound:
                await channel.send(f"❌ L'hôte {host_username} n'est pas dans ce serveur.")
                return None
            except discord.Forbidden:
                await channel.send(f"❌ Impossible d'envoyer un message privé à {host_username}.")
                return None



        # **3. Calculs pour le giveaway**
        total_bet_before_commission = int(gain_after_commission / 0.95)
        commission_total = total_bet_before_commission - gain_after_commission

        # Charger ou initialiser les données du serveur
        file_name = f"{server}.json"
        server_data = load_json(file_name, {
            "serveur": server,
            "nombre_de_jeux": 0,
            "mises_totales_avant_commission": "0 jetons",
            "gains_totaux": "0 jetons",
            "commission_totale": "0 jetons",
            "utilisateurs": {},
            "hôtes": {},
            "croupiers": {}
        })

        # **4. Mise à jour des stats globales**
        previous_total_bet = convert_amount_to_float(server_data["mises_totales_avant_commission"])
        server_data["mises_totales_avant_commission"] = format_amount(previous_total_bet + total_bet_before_commission)

        previous_total_gain = convert_amount_to_float(server_data["gains_totaux"])
        server_data["gains_totaux"] = format_amount(previous_total_gain + gain_after_commission)

        previous_total_commission = convert_amount_to_float(server_data["commission_totale"])
        server_data["commission_totale"] = format_amount(previous_total_commission + commission_total)

        server_data["nombre_de_jeux"] += 1

        # **5. Mise à jour des joueurs (gagnants et perdants)**
        for winner in raw_data["winners"]:
            user_id = winner["id"]
            username = winner["username"]

            if user_id not in server_data["utilisateurs"]:
                server_data["utilisateurs"][user_id] = {
                    "username": username,
                    "total_wins": "0 jetons",
                    "total_losses": "0 jetons",
                    "total_bets": "0 jetons",
                    "participation": 0
                }

            # Mise à jour des gains, mises, et participation
            current_wins = convert_amount_to_float(server_data["utilisateurs"][user_id]["total_wins"])
            current_bets = convert_amount_to_float(server_data["utilisateurs"][user_id]["total_bets"])
            server_data["utilisateurs"][user_id]["total_wins"] = format_amount(current_wins + gain_after_commission)
            server_data["utilisateurs"][user_id]["total_bets"] = format_amount(
                current_bets + total_bet_before_commission // len(raw_data["entries"])
            )
            server_data["utilisateurs"][user_id]["participation"] += 1

        for entry in raw_data["entries"]:
            if entry["id"] in [winner["id"] for winner in raw_data["winners"]]:
                continue
            user_id = entry["id"]
            username = entry["username"]

            if user_id not in server_data["utilisateurs"]:
                server_data["utilisateurs"][user_id] = {
                    "username": username,
                    "total_wins": "0 jetons",
                    "total_losses": "0 jetons",
                    "total_bets": "0 jetons",
                    "participation": 0
                }

            current_losses = convert_amount_to_float(server_data["utilisateurs"][user_id]["total_losses"])
            current_bets = convert_amount_to_float(server_data["utilisateurs"][user_id]["total_bets"])
            server_data["utilisateurs"][user_id]["total_losses"] = format_amount(
                current_losses + total_bet_before_commission // len(raw_data["entries"])
            )
            server_data["utilisateurs"][user_id]["total_bets"] = format_amount(
                current_bets + total_bet_before_commission // len(raw_data["entries"])
            )
            server_data["utilisateurs"][user_id]["participation"] += 1

        # **6. Mise à jour des hôtes**
        host_id = giveaway_info["host"]["id"]
        host_username = giveaway_info["host"]["username"]

        if host_id not in server_data["hôtes"]:
            server_data["hôtes"][host_id] = {
                "username": host_username,
                "total_bets": "0 jetons",
                "total_commission": "0 jetons"
            }

        current_host_bets = convert_amount_to_float(server_data["hôtes"][host_id]["total_bets"])
        current_host_commission = convert_amount_to_float(server_data["hôtes"][host_id]["total_commission"])
        server_data["hôtes"][host_id]["total_bets"] = format_amount(current_host_bets + total_bet_before_commission)
        server_data["hôtes"][host_id]["total_commission"] = format_amount(current_host_commission + commission_total)

        # Sauvegarder les données dans le fichier JSON
        save_json(file_name, server_data)
        print(f"✅ Données sauvegardées pour le serveur {server} dans {file_name}.")

        return {
            "server": server,
            "gain_after_commission": gain_after_commission,
            "total_bet_before_commission": total_bet_before_commission,
            "commission_total": commission_total,
        }

    except Exception as e:
        print(f"❌ Une erreur inattendue : {e}")
        return {"error": str(e)}

class ConfirmDataView(View):
    def __init__(self, interaction: Interaction, data):
        super().__init__()
        self.interaction = interaction
        self.data = data
        self.value = None

    @discord.ui.button(label="Valider", style=discord.ButtonStyle.success)
    async def confirm(self, button: Button, interaction: Interaction):
        self.value = True
        await interaction.response.send_message("✅ Données validées par l’hôte.")
        self.stop()

    @discord.ui.button(label="Rejeter", style=discord.ButtonStyle.danger)
    async def reject(self, button: Button, interaction: Interaction):
        self.value = False
        await interaction.response.send_message("❌ Données rejetées par l’hôte.")
        self.stop()