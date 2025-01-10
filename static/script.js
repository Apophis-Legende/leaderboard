document.addEventListener("DOMContentLoaded", function () {
    // Fonction pour charger les données du leaderboard via l'API Flask
    function loadLeaderboardData(server) {
        console.log(`🔄 Chargement des données pour le serveur : ${server}`);
        fetch(`/api/leaderboard?server=${server}`)
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`Erreur API : ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                console.log("📥 Données reçues :", data);
                updateLeaderboardTable(data);
            })
            .catch((error) => {
                console.error("❌ Erreur lors de la récupération des données :", error);
                displayErrorMessage("Erreur lors du chargement des données. Veuillez réessayer.");
            });
    }

    // Met à jour le tableau avec les données reçues
    function updateLeaderboardTable(data) {
        const tbody = document.getElementById("leaderboard-body");
        tbody.innerHTML = ""; // Vide le tableau existant

        if (data.utilisateurs && Object.keys(data.utilisateurs).length > 0) {
            Object.entries(data.utilisateurs).forEach(([userId, user]) => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${user.username || "Inconnu"}</td>
                    <td>${user.total_wins || 0}</td>
                    <td>${user.total_losses || 0}</td>
                    <td>${user.total_bets || 0}</td>
                    <td>${user.participation || 0}</td>
                    <td id="vip-${userId}">Chargement...</td>
                `;
                tbody.appendChild(row);
                
                // Charger le statut VIP
                fetch(`/api/vip_status?user_id=${userId}&server=${currentServer}`)
                    .then(response => response.json())
                    .then(vipData => {
                        const vipCell = document.getElementById(`vip-${userId}`);
                        vipCell.textContent = vipData.vipLevel ? `VIP ${vipData.vipLevel}` : '---';
                    })
                    .catch(() => {
                        const vipCell = document.getElementById(`vip-${userId}`);
                        vipCell.textContent = '---';
                    });
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="5">Aucune donnée disponible</td></tr>';
        }
    }

    // Affiche un message d'erreur dans le tableau
    function displayErrorMessage(message) {
        const tbody = document.getElementById("leaderboard-body");
        tbody.innerHTML = `<tr><td colspan="5" class="error">${message}</td></tr>`;
    }

    // Gestionnaire d'événements pour le menu déroulant
    document.getElementById("server-select").addEventListener("change", function () {
        const server = this.value;
        loadLeaderboardData(server);
    });

    // Charger les données pour le serveur par défaut au démarrage
    const defaultServer = document.getElementById("server-select").value;
    loadLeaderboardData(defaultServer);
});
