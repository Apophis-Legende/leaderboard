// Fonction pour charger les données du serveur
function loadServerData(server) {
    fetch(`/api/leaderboard?server=${server}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('current-server-name').textContent = server;

            // Récupération et calcul des VIP
            fetch(`/api/vip_status?server=${server}&user_id=0`)
                .then(response => response.json())
                .then(vipData => {
                    if (vipData && typeof vipData === 'object') {
                        document.getElementById('vip1-share').textContent = vipData.vip1 || '0 jetons';
                        document.getElementById('vip2-share').textContent = vipData.vip2 || '0 jetons';
                        document.getElementById('vip3-share').textContent = vipData.vip3 || '0 jetons';
                        document.getElementById('total-commission').textContent = 
                            `${parseInt(vipData.vip1 || 0) + parseInt(vipData.vip2 || 0) + parseInt(vipData.vip3 || 0)} jetons`;
                    }
                })
                .catch(error => {
                    console.error('Erreur VIP:', error);
                    resetVipDisplays();
                });

            updateLeaderboard(data);
        })
        .catch(error => {
            console.error('Erreur:', error);
            resetVipDisplays();
        });
}

function resetVipDisplays() {
    document.getElementById('vip1-share').textContent = '0 jetons';
    document.getElementById('vip2-share').textContent = '0 jetons';
    document.getElementById('vip3-share').textContent = '0 jetons';
    document.getElementById('total-commission').textContent = '0 jetons';
}

function updateLeaderboard(data) {
    const tbody = document.getElementById('leaderboard-body');
    tbody.innerHTML = '';

    const users = data.utilisateurs || {};
    Object.entries(users).forEach(([userId, userData]) => {
        const row = document.createElement('tr');

        const nameCell = document.createElement('td');
        nameCell.textContent = userData.username;

        const benefitCell = document.createElement('td');
        const benefit = calculateBenefit(userData.total_wins, userData.total_bets);
        benefitCell.textContent = formatKamas(benefit);

        const betsCell = document.createElement('td');
        betsCell.textContent = formatKamas(userData.total_bets);

        const vipCell = document.createElement('td');
        vipCell.textContent = calculateVipLevel(userData.total_bets);

        row.appendChild(nameCell);
        row.appendChild(benefitCell);
        row.appendChild(betsCell);
        row.appendChild(vipCell);
        tbody.appendChild(row);
    });
}

function calculateBenefit(wins, bets) {
    const winAmount = parseInt(wins?.split(' ')[0]) || 0;
    const betAmount = parseInt(bets?.split(' ')[0]) || 0;
    return `${winAmount - betAmount} jetons`;
}

function formatKamas(jetons) {
    const amount = parseInt(jetons?.split(' ')[0]) || 0;
    const kamas = amount * 10000;
    if (kamas >= 1000000) {
        return `${(kamas / 1000000).toFixed(1)}M`;
    }
    return `${(kamas / 1000).toFixed(0)}K`;
}

function calculateVipLevel(totalBets) {
    const bets = parseInt(totalBets?.split(' ')[0]) || 0;
    if (bets >= 20000) return 'VIP 3';
    if (bets >= 10000) return 'VIP 2';
    if (bets >= 4000) return 'VIP 1';
    return '---';
}

document.getElementById('server-select').addEventListener('change', function() {
    loadServerData(this.value);
});

// Chargement initial
loadServerData(document.getElementById('server-select').value);