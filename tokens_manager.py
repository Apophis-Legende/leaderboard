import json
import os

# Vérifie si le fichier existe, sinon le crée avec 1000 jetons par défaut
def init_tokens_file():
    if not os.path.exists('tokens.json'):
        with open('tokens.json', 'w') as f:
            json.dump({'stock': 1000}, f)

def get_bot_tokens():
    with open('tokens.json', 'r') as f:
        data = json.load(f)
    return data['stock']

def update_bot_tokens(amount_change):
    # Met à jour le stock des jetons en ajoutant ou en retirant des jetons
    current_tokens = get_bot_tokens()
    new_amount = current_tokens + amount_change
    with open('tokens.json', 'w') as f:
        json.dump({'stock': new_amount}, f)

# Appeler cette fonction au démarrage du bot pour s'assurer que le fichier existe
init_tokens_file()
