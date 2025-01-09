import json
import os
import requests

# MAPPING_SERVER_FILE doit être défini ici ou importé depuis un fichier global
MAPPING_SERVER_FILE = {
    "T1": "T1.json",
    "T2": "T2.json",
    "O1": "O1.json",
    "H1": "H1.json",
    "E1": "E1.json"
}

def load_json(filename):
    """
    Charge un fichier JSON ou retourne None si le fichier est introuvable ou corrompu.
    """
    try:
        absolute_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        if not os.path.exists(absolute_path):
            print(f"❌ Le fichier {absolute_path} n'existe pas.")
            return None
        with open(absolute_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            if not data:
                print(f"⚠️ Le fichier {filename} est vide.")
                return None
            return data
    except json.JSONDecodeError:
        print(f"❌ Erreur : le fichier {filename} est corrompu.")
        return None

def save_json(filename, data):
    """Sauvegarde des données dans un fichier JSON."""
    absolute_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(absolute_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f"✅ Fichier sauvegardé : {absolute_path}")

def format_amount(amount):
    """
    Convertit un float en une chaîne au format "123 jetons".
    """
    return f"{int(amount)} jetons"

def convert_amount_to_int(amount_str):
    """
    Convertit une chaîne au format "123 jetons" en un entier.
    """
    return int(amount_str.split(" ")[0])


def delete_giveaway_data(giveaway_id, server_data):
  """
  Supprime les données associées à un giveaway spécifique depuis un fichier JSON.
  """
  try:
      utilisateurs = server_data.get("utilisateurs", {})
      hôtes = server_data.get("hôtes", {})
      croupiers = server_data.get("croupiers", {})
      total_bets = int(server_data["mises_totales_avant_commission"].split()[0])
      total_gains = int(server_data["gains_totaux"].split()[0])
      total_commission = int(server_data["commission_totale"].split()[0])

      # Parcourir les utilisateurs et ajuster leurs statistiques
      for user_id, user_data in utilisateurs.items():
          if user_id == giveaway_id:  # Comparer avec l'ID du giveaway
              bets = int(user_data["total_bets"].split()[0])
              wins = int(user_data["total_wins"].split()[0])
              losses = int(user_data["total_losses"].split()[0])

              # Soustraire les valeurs
              total_bets -= bets
              total_gains -= wins
              total_commission -= losses

              # Supprimer l'utilisateur
              del utilisateurs[user_id]
              break

      # Supprimer les données de l'hôte et du croupier
      hôtes.pop(giveaway_id, None)
      croupiers.pop(giveaway_id, None)

      # Mettre à jour les totaux
      server_data["mises_totales_avant_commission"] = f"{total_bets} jetons"
      server_data["gains_totaux"] = f"{total_gains} jetons"
      server_data["commission_totale"] = f"{total_commission} jetons"
      server_data["nombre_de_jeux"] -= 1

      return True
  except Exception as e:
      print(f"❌ Erreur lors de la suppression des données : {e}")
      return False


async def delete_giveaway(interaction, link):
    try:
        await interaction.response.defer()

        # Étape 1 : Télécharger et analyser le JSON
        response = requests.get(link)
        if response.status_code != 200:
            await interaction.followup.send("⚠️ Impossible de récupérer les données depuis le lien fourni.")
            return

        giveaway_data = response.json()
        prize = giveaway_data.get("giveaway", {}).get("prize", "")
        if not prize:
            await interaction.followup.send("⚠️ Le lien ne contient pas les informations nécessaires.")
            return

        # Identifier le serveur et le fichier JSON
        server = prize.split()[0]
        filename = MAPPING_SERVER_FILE.get(server)
        if not filename:
            await interaction.followup.send(f"⚠️ Le serveur {server} n'est pas pris en charge.")
            return

        # Charger les données JSON
        server_data = load_json(filename)
        if not server_data:
            await interaction.followup.send(f"⚠️ Le fichier {filename} est introuvable ou vide.")
            return

        # Suppression des données
        winners = giveaway_data.get("winners", [])
        entries = giveaway_data.get("entries", [])
        gain_after_commission = int(prize.split()[1])
        total_bet_before_commission = int(gain_after_commission / 0.95)
        commission_total = total_bet_before_commission - gain_after_commission

        for winner in winners:
            user_id = winner["id"]
            if user_id in server_data["utilisateurs"]:
                user = server_data["utilisateurs"][user_id]
                user["total_wins"] = format_amount(convert_amount_to_int(user["total_wins"]) - gain_after_commission)
                user["total_bets"] = format_amount(convert_amount_to_int(user["total_bets"]) - total_bet_before_commission / len(entries))
                user["participation"] = max(0, user["participation"] - 1)

        for entry in entries:
            if entry["id"] not in [winner["id"] for winner in winners]:
                user_id = entry["id"]
                if user_id in server_data["utilisateurs"]:
                    user = server_data["utilisateurs"][user_id]
                    user["total_losses"] = format_amount(convert_amount_to_int(user["total_losses"]) - total_bet_before_commission / len(entries))
                    user["total_bets"] = format_amount(convert_amount_to_int(user["total_bets"]) - total_bet_before_commission / len(entries))
                    user["participation"] = max(0, user["participation"] - 1)

        # Mise à jour des hôtes et croupiers
        host_id = giveaway_data["giveaway"]["host"]["id"]
        if host_id in server_data["hôtes"]:
            host = server_data["hôtes"][host_id]
            host["total_bets"] = format_amount(convert_amount_to_int(host["total_bets"]) - total_bet_before_commission)
            host["total_commission"] = format_amount(convert_amount_to_int(host["total_commission"]) - commission_total)

        if host_id in server_data["croupiers"]:
            croupier = server_data["croupiers"][host_id]
            croupier["total_giveaways"] = max(0, croupier["total_giveaways"] - 1)
            croupier["total_kamas_managed"] = format_amount(convert_amount_to_int(croupier["total_kamas_managed"]) - total_bet_before_commission)
            croupier["total_commission"] = format_amount(convert_amount_to_int(croupier["total_commission"]) - commission_total)

        # Mise à jour globale
        server_data["nombre_de_jeux"] = max(0, server_data["nombre_de_jeux"] - 1)
        server_data["mises_totales_avant_commission"] = format_amount(
            convert_amount_to_int(server_data["mises_totales_avant_commission"]) - total_bet_before_commission
        )
        server_data["gains_totaux"] = format_amount(
            convert_amount_to_int(server_data["gains_totaux"]) - gain_after_commission
        )
        server_data["commission_totale"] = format_amount(
            convert_amount_to_int(server_data["commission_totale"]) - commission_total
        )

        # Sauvegarder les données
        save_json(filename, server_data)
        await interaction.followup.send(f"✅ Les données associées au giveaway ont été supprimées dans {filename}.")

    except Exception as e:
        print(f"❌ Erreur : {e}")
        await interaction.followup.send(f"❌ Une erreur est survenue : {e}")