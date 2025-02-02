<template>
  <div class="home-container">
    <h1 class="title">Recherche de Métiers</h1>
    <div class="form-container">
      <form @submit.prevent="handleSubmit">
        <div class="input-group">
          <label>Intitulé du métier ou mot clé :</label>
          <input type="text" v-model="intitule" required />
        </div>
        <div class="input-group">
          <label>Contexte (facultatif) :</label>
          <input type="text" v-model="contexte" />
        </div>
        <button type="submit" class="search-button">Rechercher</button>
      </form>
    </div>

    <div v-if="error" class="error">{{ error }}</div>
    
    <div v-if="results.length > 0">
      <transition name="fade">
        <div class="overlay" v-if="showPopup">
          <div class="popup">
            <button class="close-btn" @click="showPopup = false">✖</button>
            <h2>{{ results[currentIndex].libelleAppellation }} ({{ results[currentIndex].codeRome }})</h2>
            <p><strong>Description :</strong> {{ truncateText(results[currentIndex].accroche_metier, 150) }}</p>
            <p><strong>Informations :</strong> {{ truncateText(results[currentIndex].acces_metier, 100) }}</p>
            <p><strong>Compétences :</strong> {{ truncateText(results[currentIndex].competences, 100) }}</p>
            <ul v-if="results[currentIndex].formations.length">
              <li v-for="formation in results[currentIndex].formations" :key="formation">
                <router-link :to="'/formation/' + formation.split(':')[0].replace(/[\[\]']/g, '').trim()">
                  {{ formation.replace(/[\[\]']/g, '') }}
                </router-link>
              </li>
            </ul>
            <div class="swipe-buttons">
              <button @click="prevResult">⏪ Précédent</button>
              <button @click="nextResult">Suivant ⏩</button>
            </div>
          </div>
        </div>
      </transition>
    </div>
    
    <router-view></router-view>
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
    const currentIndex = ref(0);
    const showPopup = ref(false);

    const handleSubmit = async () => {
      error.value = null;
      results.value = [];
      currentIndex.value = 0;

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
        results.value = data.map(metier => ({
          ...metier,
          showDetails: false,
        }));
        showPopup.value = true;
      } catch (err) {
        error.value = err.message;
      }
    };

    const truncateText = (text, length) => {
      if (!text) return 'Non disponible';
      return text.length > length ? text.substring(0, length) + '...' : text;
    };

    const nextResult = () => {
      if (currentIndex.value < results.value.length - 1) {
        currentIndex.value++;
      }
    };

    const prevResult = () => {
      if (currentIndex.value > 0) {
        currentIndex.value--;
      }
    };

    return {
      intitule,
      contexte,
      results,
      error,
      handleSubmit,
      currentIndex,
      nextResult,
      prevResult,
      showPopup,
      truncateText,
    };
  },
};
</script>


<style scoped>
.home-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background: #1e1e1e;
  color: #fff;
  border-radius: 10px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
}

.title {
  text-align: center;
  font-size: 2em;
  margin-bottom: 20px;
}

.form-container {
  background: #2e2e2e;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.input-group {
  margin-bottom: 10px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 8px;
  border-radius: 5px;
  border: none;
}

.search-button {
  background: #f5a623;
  color: #fff;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  cursor: pointer;
  width: 100%;
}

.search-button:hover {
  background: #e59400;
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
}

.popup {
  background: #2e2e2e;
  padding: 20px;
  border-radius: 10px;
  width: 80%;
  text-align: center;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  position: absolute;
  top: 20px;
  right: 20px;
}

.swipe-buttons {
  margin-top: 15px;
  display: flex;
  justify-content: space-between;
}

.swipe-buttons button {
  background: #f5a623;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  cursor: pointer;
}

.swipe-buttons button:hover {
  background: #e59400;
}
</style>
