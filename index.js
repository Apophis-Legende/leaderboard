const express = require('express');
const path = require('path');
const { initializeApp } = require('firebase/app');
const { getDatabase, ref, get } = require('firebase/database');

const app = express();
const port = 3000;

// Configuration Firebase
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  databaseURL: "https://leaderboard-ef986-default-rtdb.europe-west1.firebasedatabase.app",
  projectId: "leaderboard-ef986",
  storageBucket: "leaderboard-ef986.firebasestorage.app",
  messagingSenderId: "524253229167",
  appId: "1:524253229167:web:a3bb0f032d08e7676a9d9a",
  measurementId: "G-G6H7N880Q6"
};

// Initialiser Firebase
const firebaseApp = initializeApp(firebaseConfig);

// Initialiser la base de données
const db = getDatabase(firebaseApp);

// Route pour récupérer les données du leaderboard
app.get('/leaderboard', async (req, res) => {
  try {
    const dbRef = ref(db, 'leaderboard/Tiliwan1'); // Référence à "leaderboard/Tiliwan1"
    const snapshot = await get(dbRef); // Récupérer les données
    if (snapshot.exists()) {
      res.json(snapshot.val()); // Retourner les données en format JSON
    } else {
      res.status(404).send("Aucune donnée trouvée pour le leaderboard.");
    }
  } catch (error) {
    console.error("Erreur lors de la récupération des données : ", error);
    res.status(500).send("Erreur lors de la récupération des données.");
  }
});

// Servir les fichiers statiques (HTML, CSS, JS) du dossier 'public'
app.use(express.static(path.join(__dirname, 'public')));

// Route par défaut pour envoyer index.html
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html')); // Envoie le fichier HTML du dossier 'public'
});

// Démarrer le serveur
app.listen(port, () => {
  console.log(`Serveur en cours d'exécution sur http://localhost:${port}`);
});
