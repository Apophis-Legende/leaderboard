import json
import os
from os import path, makedirs

def generate_html_table(data, filename="web/leaderboard.html"):
    """
    Génère une page HTML contenant un tableau basé sur les données fournies.
    """
    # Vérifier et créer le répertoire `web` si nécessaire
    directory = path.dirname(filename)
    if not path.exists(directory):
        makedirs(directory)
        print(f"📁 Dossier '{directory}' créé pour les fichiers HTML.")

    table_rows = ""
    for user_id, user_data in data["utilisateurs"].items():
        table_rows += f"""
        <tr>
            <td>{user_data['username']}</td>
            <td>{user_data['total_wins']}</td>
            <td>{user_data['total_losses']}</td>
            <td>{user_data['total_bets']}</td>
            <td>{user_data['participation']}</td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Leaderboard - {data["serveur"]}</title>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f4f4f4; }}
        </style>
    </head>
    <body>
        <h1>Leaderboard - Serveur {data["serveur"]}</h1>
        <table>
            <thead>
                <tr>
                    <th>Nom d'utilisateur</th>
                    <th>Gains Totaux</th>
                    <th>Pertes Totales</th>
                    <th>Mises Totales</th>
                    <th>Participation</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </body>
    </html>
    """

    # Sauvegarder dans un fichier
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html_content)
    print(f"✅ Fichier HTML généré : {filename}")
    return filename
