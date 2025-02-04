<template>
    <div class="metier-details">
      <h1 class="title">Fiche métier</h1>
      <div v-if="loading" class="loading">Chargement...</div>
      <div v-if="error" class="error">{{ error }}</div>
      <div v-if="metier" class="content">
        <h2 class="metier-title">{{ metier.libelleAppellation }}</h2>
        <div class="info-grid">
          <div class="info-box">
            <h3>Code ROME</h3>
            <p>{{ metier.codeRome }}</p>
          </div>
          <div class="info-box">
            <h3>Accès au métier</h3>
            <p>{{ metier.acces_metier || "Non disponible" }}</p>
          </div>
        </div>
  
        <div class="description">
          <h3>Description</h3>
          <p>{{ metier.accroche_metier || "Non disponible" }}</p>
        </div>
  
        <div class="competences">
          <h3>Compétences</h3>
          <p>{{ metier.centres_interet || "Non disponible" }}</p>
        </div>
  
        <div class="formations">
          <h3>Formations recommandées</h3>
          <ul>
            <li v-for="formation in metier.formations" :key="formation">
              <router-link :to="'/formation/' + formation.replace(/[\[\]']/g, '').split(':')[0].trim()">
                {{ formation.replace(/[\[\]']/g, '') }}
              </router-link>
            </li>
          </ul>
        </div>
  
        <div v-if="metier.url" class="more-info">
          <h3>Plus d'infos</h3>
          <a :href="metier.url" target="_blank">Consulter le site officiel</a>
        </div>
      </div>
    </div>
  
    <router-link to="/">⬅ Retour</router-link>
  </template>
  
  <script>
  import { ref, onMounted } from "vue";
  import { useRoute } from "vue-router";
  import { supabase } from "../supabase";
  
  export default {
    setup() {
      const route = useRoute();
      const metier = ref(null);
      const loading = ref(true);
      const error = ref(null);
  
      onMounted(async () => {
        try {
          const { data, error: fetchError } = await supabase
            .from("metiers_id") // ⚠️ Vérifie que ta table s'appelle bien "metiers"
            .select("*")
            .eq("identifiant", route.params.id)
            .single();
  
          if (fetchError) throw fetchError;
          metier.value = data;
        } catch (err) {
          error.value = "Erreur lors de la récupération du métier.";
          console.error("❌ Erreur récupération métier:", err.message);
        } finally {
          loading.value = false;
        }
      });
  
      return { metier, loading, error };
    }
  };
  </script>
  
  <style scoped>
  .metier-details {
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
  
  .metier-title {
    text-align: center;
    font-size: 1.8em;
    color: #f5a623;
  }
  
  .info-grid {
    display: flex;
    justify-content: space-between;
    gap: 20px;
    margin-bottom: 20px;
  }
  
  .info-box {
    flex: 1;
    background: #2e2e2e;
    padding: 15px;
    border-radius: 8px;
    text-align: center;
  }
  
  .description, .competences, .formations, .more-info {
    background: #2e2e2e;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
  }
  
  h3 {
    color: #f5a623;
    margin-bottom: 10px;
  }
  
  .more-info a {
    color: #2331f5;
    text-decoration: none;
    font-weight: bold;
  }
  
  .more-info a:hover {
    text-decoration: underline;
  }
  </style>
  