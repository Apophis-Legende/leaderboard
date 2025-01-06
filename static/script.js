<script>
    // Fonction pour charger les données du leaderboard via AJAX
    function loadLeaderboardData(server) {
        $.get(`/api/leaderboard?server=${server}`, function(data) {
            const tbody = $('#leaderboard-body');
            tbody.empty(); // Vider le tableau existant

            // Vérifie si des données existent avant de les afficher
            if (data && data.utilisateurs) {
                for (const userId in data.utilisateurs) {
                    const user = data.utilisateurs[userId];
                    const row = `<tr>
                        <td>${user.username}</td>
                        <td>${user.total_wins}</td>
                        <td>${user.total_losses}</td>
                        <td>${user.total_bets}</td>
                        <td>${user.participation}</td>
                    </tr>`;
                    tbody.append(row);
                }
            } else {
                const row = `<tr><td colspan="5">Aucune donnée disponible</td></tr>`;
                tbody.append(row);
            }
        }).fail(function() {
            alert('Erreur lors de la récupération des données.');
        });
    }

    // Lorsque l'utilisateur choisit un serveur
    $('#server-select').on('change', function() {
        const selectedServer = $(this).val();
        loadLeaderboardData(selectedServer);  // Charger les données du serveur sélectionné
    });

    // Charger les données du serveur par défaut au démarrage
    loadLeaderboardData('Tiliwan1');
</script>
