import discord
from discord.ext import commands
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import asyncio

# Configuration du bot
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")

@bot.event
async def on_message(message):
    if "giveaway" in message.content.lower():
        print("Message de giveaway détecté.")
        if hasattr(message, "components") and message.components:
            for component in message.components:
                for button in component.children:
                    print(f"Bouton détecté avec custom_id : {button.custom_id}")
                    await message.channel.send("Giveaway détecté avec un bouton !")

@bot.event
async def on_interaction(interaction):
    if interaction.type.name == "component":
        if interaction.data.get("custom_id") == "giveaway_button_id":  # Remplacez par l'ID du bouton
            button_url = interaction.message.components[0].children[0].url
            print(f"URL récupérée : {button_url}")
            await interaction.response.send_message(f"URL récupérée : {button_url}")

            giveaway_data = await open_page_with_selenium(button_url)
            await interaction.followup.send(f"Données du giveaway : {giveaway_data}")

async def open_page_with_selenium(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    chrome_bin = os.getenv("CHROME_BIN", "/usr/bin/chromium")
    chrome_options.binary_location = chrome_bin

    service = Service("/nix/store/.../chromedriver")  # Remplacez par le chemin réel si nécessaire
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        await asyncio.sleep(5)
        element = driver.find_element(By.ID, "element_id")  # Modifiez en fonction de la page
        giveaway_data = element.text
        print(f"Données extraites : {giveaway_data}")
    except Exception as e:
        print(f"Erreur lors de l'extraction des données : {e}")
        giveaway_data = "Impossible d'extraire les données."
    finally:
        driver.quit()

    return giveaway_data

bot.run(os.getenv("DISCORD_TOKEN"))
