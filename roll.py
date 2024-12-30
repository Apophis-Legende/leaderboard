import random
from tokens_manager import get_bot_tokens, update_bot_tokens

async def roll_dice(interaction, bet_amount, user_id):
    bot_tokens = get_bot_tokens()  # Récupérer le stock actuel de jetons
    print(f"Jetons du bot avant la mise : {bot_tokens}")

    # Lancer le dé
    roll_result = random.randint(1, 6)
    print(f"Résultat du dé : {roll_result}")

    if roll_result in [1, 2, 3]:  # Condition de perte
        await interaction.response.send_message("Tu as perdu, Ecaflip n'était pas à tes côtés cette fois-ci.")
        # Ajouter la mise au stock du bot (le bot gagne les jetons misés)
        update_bot_tokens(bet_amount)  
        print(f"Jetons du bot après gain de la mise : {get_bot_tokens()}")
        return False  # Indiquer que le joueur a perdu
    else:  # Condition de gain
        winnings = bet_amount * 5  
        await interaction.response.send_message(f"Félicitations ! Tu as gagné {winnings} jetons.")

        # Vérifier si le bot a suffisamment de jetons pour payer le joueur
        if bot_tokens >= winnings:
            update_bot_tokens(-winnings)  # Déduire les gains du bot
            print(f"Jetons du bot après paiement des gains : {get_bot_tokens()}")
        else:
            # Si le bot n'a pas assez de jetons, rendre la mise et informer l'utilisateur
            update_bot_tokens(bet_amount)  # Rendre la mise au joueur
            await interaction.response.send_message("Le bot n'a pas assez de jetons pour payer cette victoire, la mise a été remboursée.")

        return True  # Indiquer que le joueur a gagné
