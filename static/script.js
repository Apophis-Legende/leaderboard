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

    // Gestionnaire d'événements pour le menu déroulant
    document.getElementById("server-select").addEventListener("change", function () {
        const server = this.value;
        loadLeaderboardData(server);
        updateVipInfo(server);
    });

    function updateVipInfo(server) {
        const serverMapping = {
            "Tiliwan1": "T1.json",
            "Tiliwan2": "T2.json",
            "Oshimo": "O1.json",
            "Herdegrize": "H1.json",
            "Euro": "E1.json"
        };

        const fileName = serverMapping[server];
        if (!fileName) return;

        fetch(`/api/leaderboard?server=${server}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('current-server-name').textContent = server;
                
                // Extraire la commission totale du fichier JSON
                let totalCommission = 0;
                if (data.commission_totale) {
                    const commissionStr = data.commission_totale.toString();
                    totalCommission = parseInt(commissionStr.split(' ')[0]) || 0;
                }
                
                document.getElementById('total-commission').textContent = totalCommission + " jetons";
                
                // Calculer 50% de la commission totale pour la redistribution
                const redistributionTotal = Math.floor(totalCommission * 0.5);
                
                // Calculer les montants pour chaque palier VIP
                const vip1Share = Math.floor(redistributionTotal * 0.20);
                const vip2Share = Math.floor(redistributionTotal * 0.30);
                const vip3Share = Math.floor(redistributionTotal * 0.50);

                document.getElementById('vip1-share').textContent = vip1Share + " jetons";
                document.getElementById('vip2-share').textContent = vip2Share + " jetons";
                document.getElementById('vip3-share').textContent = vip3Share + " jetons";
            })
            .catch(error => console.error('Erreur:', error));
    }

    document.getElementById('server-select').addEventListener('change', function() {
        const server = this.value;
        updateVipInfo(server);
    });

    // Charger les données pour le serveur par défaut au démarrage
    const defaultServer = document.getElementById("server-select").value;
    loadLeaderboardData(defaultServer);
    updateVipInfo(defaultServer);
});