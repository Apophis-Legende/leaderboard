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

    // Récupérer les données VIP depuis l'API
    async function getVIPCommissions(serverName) {
        try {
            const response = await fetch(`/api/vip_commissions?server=${serverName}`);
            if (!response.ok) {
                console.error("Erreur lors de la récupération des commissions VIP");
                return null;
            }
            const data = await response.json();
            console.log("Données reçues depuis l'API :", data); // LOG pour vérifier les données
            return data;
        } catch (error) {
            console.error("Erreur de communication avec l'API :", error);
            return null;
        }
    }

    function loadVIPCommissions(server) {
        console.log(`🔄 Chargement des données VIP pour le serveur : ${server}`);

        $.ajax({
            url: `/api/vip_commissions`,
            type: "GET",
            data: { server: server },
            success: function (data) {
                console.log("📥 Données VIP reçues :", data);

                // Mettre à jour les éléments HTML avec les données reçues
                $('#vip1-share').text(`${data.vip1.toFixed(2)} jetons`);
                $('#vip2-share').text(`${data.vip2.toFixed(2)} jetons`);
                $('#vip3-share').text(`${data.vip3.toFixed(2)} jetons`);
                $('#total-commission').text(`${data.total.toFixed(2)} jetons`);
            },
            error: function (error) {
                console.error("❌ Erreur lors de la récupération des données VIP :", error);

                // Gérer les erreurs d'affichage
                $('#vip1-share').text("Erreur");
                $('#vip2-share').text("Erreur");
                $('#vip3-share').text("Erreur");
                $('#total-commission').text("Erreur");
            }
        });
    }

    // Exemple d'appel
    loadVIPCommissions('Tiliwan1');


    // Charger les données automatiquement au démarrage
    document.addEventListener("DOMContentLoaded", loadDefaultServerData);


    // Mettre à jour les données lorsqu'un serveur est sélectionné
    document.getElementById('server-select').addEventListener('change', (event) => {
        const selectedServer = event.target.value;
        document.getElementById('current-server-name').textContent = selectedServer;
        loadServerData(selectedServer);
    });


    // Gestionnaire d'événements pour le menu déroulant
    document.getElementById("server-select").addEventListener("change", function () {
        const server = this.value;
        loadLeaderboardData(server);
    });

    // Charger les données pour le serveur par défaut au démarrage
    const defaultServer = document.getElementById("server-select").value;
    loadLeaderboardData(defaultServer);
});
