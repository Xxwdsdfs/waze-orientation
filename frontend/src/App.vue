<template>
  <div class="app">
    <h1>Recherche de Métiers</h1>
    <form @submit.prevent="handleSubmit">
      <div>
        <label>
          Intitulé du métier ou mot clé :
          <input type="text" v-model="intitule" required />
        </label>
      </div>
      <div>
        <label>
          Contexte (facultatif) :
          <input type="text" v-model="contexte" />
        </label>
      </div>
      <button type="submit">Rechercher</button>
    </form>

    <div v-if="error" class="error">
      {{ error }}
    </div>

    <div v-if="results.length > 0" class="results">
      <h2>Résultats :</h2>
      <ul>
        <li v-for="metier in results" :key="metier.codeRome" class="metier-box">
          <strong>{{ metier.libelleAppellation }}</strong> ({{ metier.codeRome }})
          <button @click="toggleDetails(metier.codeRome)">
            {{ metier.showDetails ? 'Réduire' : 'En savoir plus' }}
          </button>

          <!-- Affichage conditionnel des détails -->
          <div v-if="metier.showDetails" class="metier-details">
            <p><strong>Description :</strong> {{ metier.accroche_metier }}</p>
            <p><strong>Informations :</strong> {{ metier.acces_metier }}</p>
            <p><strong>Compétences :</strong> {{ metier.competences }}</p>
            <p><strong>Formations :</strong> {{ metier.formations }}</p>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';

export default {
  setup() {
    const intitule = ref('');
    const contexte = ref('');
    const results = ref([]);
    const error = ref(null);

    const handleSubmit = async () => {
      error.value = null;
      results.value = [];

      try {
        const response = await fetch('http://localhost:5000/call_api', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            intitule: intitule.value,
            contexte: contexte.value,
          }),
        });

        if (!response.ok) {
          throw new Error('Erreur lors de la récupération des données');
        }

        const data = await response.json();
        
        // Ajout de showDetails pour gérer l'affichage dynamique
        results.value = data.map(metier => ({
          ...metier,
          showDetails: false, // Initialement caché
        }));
      } catch (err) {
        error.value = err.message;
      }
    };

    const toggleDetails = (codeRome) => {
      const metier = results.value.find(m => m.codeRome === codeRome);
      if (metier) {
        metier.showDetails = !metier.showDetails;
      }
    };

    return {
      intitule,
      contexte,
      results,
      error,
      handleSubmit,
      toggleDetails,
    };
  },
};
</script>


<style>
.app {
  text-align: center;
  padding: 20px;
}

form {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 10px;
}

input {
  margin-left: 10px;
}

.error {
  color: red;
}

.results {
  margin-top: 20px;
  text-align: left;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  margin-bottom: 10px;
}

.metier-box {
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 15px;
  margin-bottom: 10px;
  background-color: #f9f9f9;
  color: #003366;
  font-weight: bold;
  position: relative;
}

.metier-details {
  margin-top: 10px;
  padding: 10px;
  background-color: #e6f7ff;
  border-radius: 5px;
}

button {
  margin-top: 10px;
  padding: 5px 10px;
  border: none;
  background-color: #007bff;
  color: white;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}

</style>