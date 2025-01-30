<template>
  <div class="container">
    <h1>Recherche de Compétence</h1>
    <input v-model="action" placeholder="Entrez une action" />
    <button @click="searchCompetence">Rechercher</button>
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
      action: '',
      resultat: null,
    };
  },
  methods: {
    async searchCompetence() {
      if (!this.action) {
        alert('Veuillez entrer une action.');
        return;
      }
      try {
        const response = await axios.post('http://localhost:5000/search', { action: this.action });
        this.resultat = response.data;
      } catch (error) {
        console.error('Erreur lors de la recherche de compétence', error);
      }
    },
  },
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
