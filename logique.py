import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.common.by import By
import asyncio

# Configuration du bot
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True  # Nécessaire pour lire les messages dans Discord
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")

# Détection des giveaways
@bot.event
async def on_message(message):
    # Si le message contient "giveaway"
    if "giveaway" in message.content.lower():
        print("Message de giveaway détecté.")

        # Vérifier si le message contient des composants (boutons)
        if hasattr(message, "components") and message.components:
            for component in message.components:
                for button in component.children:
                    print(f"Bouton détecté avec custom_id : {button.custom_id}")
                    # Exemple de message envoyé pour confirmer
                    await message.channel.send("Giveaway détecté avec un bouton !")

# Interaction avec le bouton
@bot.event
async def on_interaction(interaction):
    if interaction.type.name == "component":  # Vérifie si c'est une interaction avec un bouton
        if interaction.data.get("custom_id") == "giveaway_button_id":  # Remplacez par l'ID exact du bouton
            # Récupérer l'URL associée au bouton (si disponible)
            button_url = interaction.message.components[0].children[0].url  # Suppose que le bouton a une URL
            print(f"URL récupérée : {button_url}")
            await interaction.response.send_message(f"URL récupérée : {button_url}")

            # Ouvrir la page avec Selenium
            giveaway_data = await open_page_with_selenium(button_url)

            # Envoyer les données extraites à Discord
            await interaction.followup.send(f"Données du giveaway : {giveaway_data}")

# Fonction pour ouvrir la page avec Selenium et extraire des données
async def open_page_with_selenium(url):
    # Initialiser Selenium (assurez-vous que le driver Chrome est installé)
    driver = webdriver.Chrome()  # Remplacez par le chemin de votre driver si nécessaire
    driver.get(url)

    try:
        # Attendre que la page charge (par exemple 5 secondes)
        await asyncio.sleep(5)

        # Exemple : Trouver un élément avec un ID spécifique
        element = driver.find_element(By.ID, "element_id")  # Remplacez par un ID existant
        giveaway_data = element.text
        print(f"Données extraites : {giveaway_data}")
    except Exception as e:
        print(f"Erreur lors de l'extraction des données : {e}")
        giveaway_data = "Impossible d'extraire les données."
    finally:
        driver.quit()

    return giveaway_data

# Lancer le bot
bot.run("YOUR_BOT_TOKEN")
