// Fonction pour charger les données du serveur
function loadServerData(server) {
    fetch(`/api/leaderboard?server=${server}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('current-server-name').textContent = server;

            // Récupération et calcul des VIP
            console.log(`Fetching VIP data for server: ${server}`);
            fetch(`/api/vip_status?server=${server}&user_id=0`)
                .then(response => {
                    console.log('VIP Response status:', response.status);
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(vipData => {
                    console.log('VIP Data received:', vipData);
                    console.log('VIP Data received:', vipData);
                    const vip1 = vipData.vip1.split(' ')[0];
                    const vip2 = vipData.vip2.split(' ')[0];
                    const vip3 = vipData.vip3.split(' ')[0];
                    
                    document.getElementById('vip1-share').textContent = `${vip1} jetons`;
                    document.getElementById('vip2-share').textContent = `${vip2} jetons`;
                    document.getElementById('vip3-share').textContent = `${vip3} jetons`;
                    const total = parseInt(vip1) + parseInt(vip2) + parseInt(vip3);
                    document.getElementById('total-commission').textContent = `${total} jetons`;
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