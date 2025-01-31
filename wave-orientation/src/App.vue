<template>
  <div class="container">
    <h1>FORMAGO</h1>
    <input v-model="action" placeholder="Entrez une action" />
    
    <!-- Choisir entre compétence ou métier -->
    <select v-model="searchType">
      <option value="competence">Compétence</option>
      <option value="metier">Métier</option>
    </select>
    
    <button @click="search">Rechercher</button>

    <div v-if="resultat">
      <h2>Résultat :</h2>
      <pre>{{ resultat }}</pre>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      action: '',   // Action saisie par l'utilisateur
      searchType: 'competence',  // Type de recherche (compétence ou métier)
      resultat: null,   // Résultat de la recherche
    };
  },
  methods: {
    async search() {
      if (!this.action) {
        alert('Veuillez entrer une action.');
        return;
      }

      // URL de l'API en fonction du type de recherche
      const url = this.searchType === 'competence' 
        ? 'http://localhost:5000/search' 
        : 'http://localhost:5000/predict_metier';

      try {
        const response = await axios.post(url, { action: this.action });

        if (this.searchType === 'competence') {
          // Si c'est une recherche de compétence, extraire les libellés
          this.resultat = response.data.flatMap(item =>
            item.competencesRome.map(comp => comp.libelleCompetence)
          );
        } else {
          // Si c'est une recherche de métier, afficher les résultats du métier
          this.resultat = response.data;
        }

      } catch (error) {
        console.error('Erreur lors de la recherche', error);
      }
    },
  }
};
</script>

<style>
.container {
  max-width: 600px;
  margin: auto;
  text-align: center;
  padding: 20px;
}
input {
  padding: 10px;
  margin: 10px;
  width: 80%;
}
select {
  padding: 10px;
  margin: 10px;
}
button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
}
button:hover {
  background-color: #0056b3;
}
</style>
