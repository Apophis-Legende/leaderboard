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
            Object.values(data.utilisateurs).forEach((user) => {
                const row = `
                    <tr>
                        <td>${user.username || "Inconnu"}</td>
                        <td>${user.total_wins || 0}</td>
                        <td>${user.total_losses || 0}</td>
                        <td>${user.total_bets || 0}</td>
                        <td>${user.participation || 0}</td>
                    </tr>`;
                tbody.innerHTML += row;
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

    async function getTotalCommissions(serverName) {
        // Simuler une requête pour récupérer les données du serveur
        const data = {
            Tiliwan1: { totalCommission: 10000 },
            Tiliwan2: { totalCommission: 5000 },
        };
        return data[serverName].totalCommission || 0;
    }

    function calculateVIPShares(totalCommission) {
        return {
            vip1: totalCommission * 0.2,
            vip2: totalCommission * 0.3,
            vip3: totalCommission * 0.5,
        };
    }

    function updateVIPValues(vipShares) {
        document.getElementById('vip1-share').textContent = `${vipShares.vip1.toFixed(2)} jetons`;
        document.getElementById('vip2-share').textContent = `${vipShares.vip2.toFixed(2)} jetons`;
        document.getElementById('vip3-share').textContent = `${vipShares.vip3.toFixed(2)} jetons`;

        const totalRedistributed = vipShares.vip1 + vipShares.vip2 + vipShares.vip3;
        document.getElementById('total-commission').textContent = `${totalRedistributed.toFixed(2)} jetons`;
    }

    function loadUserDetails(serverName) {
        // Simuler une requête pour récupérer les utilisateurs
        const users = {
            Tiliwan1: [
                { username: 'apophislegende', profit: '-500K Kamas', bets: '10M Kamas', vip: '---' },
            ],
            Tiliwan2: [
                { username: 'player2', profit: '300K Kamas', bets: '5M Kamas', vip: 'VIP 2' },
            ],
        };

        const tbody = document.querySelector('#user-table tbody');
        tbody.innerHTML = ''; // Effacer les anciennes données

        users[serverName].forEach((user) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${user.username}</td>
                <td>${user.profit}</td>
                <td>${user.bets}</td>
                <td>${user.vip}</td>
            `;
            tbody.appendChild(row);
        });
    }

    async function loadServerData(serverName) {
        const totalCommission = await getTotalCommissions(serverName);
        const vipShares = calculateVIPShares(totalCommission);
        updateVIPValues(vipShares);
        loadUserDetails(serverName);
    }

    document.getElementById('server-select').addEventListener('change', (event) => {
        const selectedServer = event.target.value;
        document.getElementById('current-server-name').textContent = selectedServer;
        loadServerData(selectedServer);
    });

    // Charger les données par défaut au démarrage
    loadServerData('Tiliwan1');



    // Gestionnaire d'événements pour le menu déroulant
    document.getElementById("server-select").addEventListener("change", function () {
        const server = this.value;
        loadLeaderboardData(server);
    });

    // Charger les données pour le serveur par défaut au démarrage
    const defaultServer = document.getElementById("server-select").value;
    loadLeaderboardData(defaultServer);
});
