const express = require("express");
const path = require("path");

const app = express();
const port = 3000;

// Servir les fichiers statiques (HTML, CSS, JS) du dossier 'public'
app.use(express.static(path.join(__dirname, "public")));

// Simuler des données spécifiques à chaque serveur
const leaderboardData = {
  Tiliwan1: {
    utilisateurs: {
      user1: { username: "User1", total_wins: 100, total_losses: 50, total_bets: 150, participation: 10 },
      user2: { username: "User2", total_wins: 80, total_losses: 40, total_bets: 120, participation: 8 },
    },
  },
  Tiliwan2: {
    utilisateurs: {
      user3: { username: "User3", total_wins: 200, total_losses: 100, total_bets: 300, participation: 20 },
      user4: { username: "User4", total_wins: 50, total_losses: 25, total_bets: 75, participation: 5 },
    },
  },
  Oshimo: {
    utilisateurs: {
      user5: { username: "User5", total_wins: 150, total_losses: 70, total_bets: 220, participation: 15 },
      user6: { username: "User6", total_wins: 60, total_losses: 30, total_bets: 90, participation: 7 },
    },
  },
  Herdegrize: {
    utilisateurs: {
      user7: { username: "User7", total_wins: 300, total_losses: 120, total_bets: 420, participation: 25 },
      user8: { username: "User8", total_wins: 40, total_losses: 20, total_bets: 60, participation: 5 },
    },
  },
  Euro: {
    utilisateurs: {
      user9: { username: "User9", total_wins: 500, total_losses: 250, total_bets: 750, participation: 30 },
      user10: { username: "User10", total_wins: 120, total_losses: 60, total_bets: 180, participation: 10 },
    },
  },
};

// Route pour récupérer les données du leaderboard
app.get("/api/leaderboard", (req, res) => {
  const server = req.query.server; // Récupérer le paramètre 'server' de la requête
  const data = leaderboardData[server] || { utilisateurs: {} }; // Retourne les données du serveur ou un objet vide
  res.json(data); // Retourner les données en format JSON
});

// Route par défaut pour envoyer index.html
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

// Démarrer le serveur
app.listen(port, () => {
  console.log(`✅ Serveur en cours d'exécution sur http://localhost:${port}`);
});
