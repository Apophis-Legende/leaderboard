
// Fonction pour charger les données du serveur
function loadServerData(server) {
    fetch(`/api/leaderboard?server=${server}`)
        .then(response => response.json())
        .then(data => {
            // Mise à jour du nom du serveur
            document.getElementById('current-server-name').textContent = server;
            
            // Extraction et calcul de la redistribution VIP
            const commissionStr = data.commission_totale || "0 jetons";
            const totalCommission = parseInt(commissionStr.split(' ')[0]) || 0;
            const redistributionTotal = Math.floor(totalCommission / 2); // 50% du total
            
            // Calcul des parts VIP
            const vip1Share = Math.floor(redistributionTotal * 0.20); // 20%
            const vip2Share = Math.floor(redistributionTotal * 0.30); // 30%
            const vip3Share = Math.floor(redistributionTotal * 0.50); // 50%
            
            // Mise à jour de l'affichage
            document.getElementById('vip1-share').textContent = vip1Share;
            document.getElementById('vip2-share').textContent = vip2Share;
            document.getElementById('vip3-share').textContent = vip3Share;
            document.getElementById('total-commission').textContent = totalCommission;
            
            // Mise à jour du tableau
            updateLeaderboard(data);
        })
        .catch(error => {
            console.error('Erreur:', error);
        });
}

// Mise à jour du tableau des joueurs
function updateLeaderboard(data) {
    const tbody = document.getElementById('leaderboard-body');
    tbody.innerHTML = '';
    
    const users = data.utilisateurs || {};
    Object.entries(users).forEach(([userId, userData]) => {
        const row = document.createElement('tr');
        
        // Nom d'utilisateur
        const nameCell = document.createElement('td');
        nameCell.textContent = userData.username;
        
        // Bénéfice
        const benefitCell = document.createElement('td');
        const benefit = calculateBenefit(userData.total_wins, userData.total_bets);
        benefitCell.textContent = formatKamas(benefit);
        
        // Mises totales
        const betsCell = document.createElement('td');
        betsCell.textContent = formatKamas(userData.total_bets);
        
        // Niveau VIP
        const vipCell = document.createElement('td');
        vipCell.textContent = calculateVipLevel(userData.total_bets);
        
        row.appendChild(nameCell);
        row.appendChild(benefitCell);
        row.appendChild(betsCell);
        row.appendChild(vipCell);
        tbody.appendChild(row);
    });
}

// Calcul du bénéfice
function calculateBenefit(wins, bets) {
    const winAmount = parseInt(wins?.split(' ')[0]) || 0;
    const betAmount = parseInt(bets?.split(' ')[0]) || 0;
    return `${winAmount - betAmount} jetons`;
}

// Formatage des kamas
function formatKamas(jetons) {
    const amount = parseInt(jetons?.split(' ')[0]) || 0;
    const kamas = amount * 10000;
    if (kamas >= 1000000) {
        return `${(kamas / 1000000).toFixed(1)}M`;
    }
    return `${(kamas / 1000).toFixed(0)}K`;
}

// Calcul du niveau VIP
function calculateVipLevel(totalBets) {
    const bets = parseInt(totalBets?.split(' ')[0]) || 0;
    if (bets >= 20000) return 'VIP 3';
    if (bets >= 10000) return 'VIP 2';
    if (bets >= 4000) return 'VIP 1';
    return '---';
}

// Écouteur d'événements pour le changement de serveur
document.getElementById('server-select').addEventListener('change', function() {
    loadServerData(this.value);
});

// Chargement initial
loadServerData(document.getElementById('server-select').value);
