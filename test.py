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

    # Vérifier les VIP pour les utilisateurs après un giveaway
    raw_data = ...  # Récupérez les données JSON du giveaway
    await handle_giveaway(raw_data, message.channel)


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

    # Détection d'une mise à jour des données
    if "🎉 Données du giveaway traitées et envoyées à Flask avec succès" in message.content:
        print("🔄 Détection d'une mise à jour des données du giveaway...")

        # Chargez le fichier data.json pour récupérer le dernier serveur traité
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            # Récupérez le nom du serveur depuis les données
            server_name = data.get("giveaway", {}).get("prize", "").split(" ")[0]  # Exemple : T2 9500
            if not server_name:
                await message.channel.send("⚠️ Impossible de déterminer le serveur pour la mise à jour.")
                return

            # Mise à jour automatique des VIP pour le serveur
            await message.channel.send(f"🔄 Mise à jour automatique des statuts VIP pour le serveur **{server_name}** en cours...")
            await check_vip_status(server_name, message.channel)

        except FileNotFoundError:
            print("❌ Fichier data.json introuvable.")
            await message.channel.send("⚠️ Fichier data.json introuvable. Impossible de mettre à jour les statuts VIP.")
        except Exception as e:
            print(f"❌ Une erreur est survenue : {e}")
            await message.channel.send(f"⚠️ Une erreur est survenue lors de la mise à jour des statuts VIP : {e}")

    # Assurez-vous que les commandes continuent de fonctionner
    await bot.process_commands(message)
