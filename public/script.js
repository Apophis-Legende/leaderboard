async function loadLeaderboardData(server) {
    try {
        const response = await fetch(`/api/leaderboard?server=${server}`);
        const data = await response.json();
        const tbody = document.getElementById('leaderboard-body');
        tbody.innerHTML = '';  // Vider les lignes existantes

        // Vérifie si des données existent avant de les afficher
        if (data && data.utilisateurs) {
            for (const userId in data.utilisateurs) {
                const user = data.utilisateurs[userId];
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${user.username}</td>
                    <td>${user.total_wins} jetons</td>
                    <td>${user.total_losses} jetons</td>
                    <td>${user.total_bets} jetons</td>
                    <td>${user.participation}</td>
                `;
                tbody.appendChild(row);
            }
        } else {
            const row = document.createElement('tr');
            row.innerHTML = `<td colspan="5">Aucune donnée disponible</td>`;
            tbody.appendChild(row);
        }
    } catch (error) {
        console.error('Erreur lors de la récupération des données :', error);
    }
}

// Charger les données pour le serveur par défaut au démarrage
loadLeaderboardData('Tiliwan1');

// Écouter le changement de sélection dans le menu déroulant
document.getElementById('server-select').addEventListener('change', function(event) {
    const selectedServer = event.target.value;
    loadLeaderboardData(selectedServer);  // Charger les données du serveur sélectionné
});
