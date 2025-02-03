<template>
    <div class="profile-container">
      <h1>Mon Profil</h1>
  
      <div v-if="user">
        <p><strong>Email :</strong> {{ user.email }}</p>
        <button @click="signOut" class="logout-button">Se Déconnecter</button>
  
        <h2>📌 Cartes Likées</h2>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
  
        <div v-if="likedJobs.length > 0">
          <div v-for="(job, index) in likedJobs" :key="job.romesV3_value" class="job-card">
            <h3 @click="openPopup(index)">{{ job.libelleAppellation }}</h3>
            
            <div class="image-container">
              <img :src="job.imageUrl" alt="Image du métier" class="job-image" />
            </div>
  
            <div class="card-buttons">
              <button class="remove-button" @click="removeLike(job.romesV3_value)">❌ Supprimer</button>
              <button class="info-button" @click="openPopup(index)">ℹ️ En savoir plus</button>
            </div>
          </div>
        </div>
  
        <p v-else>Aucun métier liké pour l'instant.</p>
      </div>
  
      <div v-else>
        <p>Veuillez vous connecter pour voir votre profil.</p>
      </div>
  
      <!-- POPUP POUR AFFICHER LES DÉTAILS DU MÉTIER -->
      <div v-if="showPopup" class="overlay">
        <div class="popup">
          <button class="close-btn" @click="showPopup = false">✖</button>
          <h2>{{ selectedJob?.libelleAppellation }}</h2>
  
          <div class="image-container">
            <img v-if="selectedJob?.imageUrl" :src="selectedJob.imageUrl" alt="Image du métier" class="job-image" />
            <div v-else class="placeholder-image">Image non trouvée</div>
          </div>
  
          <div class="details-container">
            <h3>Description</h3>
            <p>{{ selectedJob?.accroche_metier }}</p>
  
            <h3>Informations</h3>
            <p>{{ selectedJob?.acces_metier }}</p>
  
            <h3>Compétences</h3>
            <p>{{ selectedJob?.centres_interet }}</p>
  
            <h3>Formations</h3>
            <ul v-if="selectedJob?.formations.length">
              <li v-for="formation in selectedJob.formations" :key="formation">
                <router-link :to="'/formation/' + formation.replace(/[\[\]']/g, '').split(':')[0].trim()">
                  {{ formation.replace(/[\[\]']/g, '') }}
                </router-link>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from "vue";
  import { supabase } from "../supabase";
  
  export default {
    setup() {
      const user = ref(null);
      const likedJobs = ref([]);
      const errorMessage = ref("");
      const showPopup = ref(false);
      const selectedJob = ref(null);
      const googleApiKey = "TA_CLE_GOOGLE"; // 🔥 Remplace par ta clé API
      const searchEngineId = "TON_ID_MOTEUR"; // 🔥 Remplace par ton ID de moteur
  
      // Vérifier l'authentification et charger les likes
      onMounted(async () => {
        const { data: session } = await supabase.auth.getSession();
        if (session?.user) {
          user.value = session.user;
          await fetchLikedJobs();
        }
  
        supabase.auth.onAuthStateChange((event, session) => {
          user.value = session ? session.user : null;
          if (user.value) fetchLikedJobs();
        });
      });
  
      // Récupérer les métiers likés
      const fetchLikedJobs = async () => {
        if (!user.value) return;
  
        try {
          const { data, error } = await supabase
            .from("liked_cards")
            .select("job_id")
            .eq("user_id", user.value.id);
  
          if (error) {
            console.error("❌ Erreur lors du chargement des likes :", error.message);
            errorMessage.value = error.message;
            return;
          }
  
          const jobIds = data.map((item) => item.job_id);
          const jobDetails = await Promise.all(jobIds.map(fetchJobDetails));
          likedJobs.value = jobDetails.filter(job => job !== null);
        } catch (err) {
          console.error("❌ Erreur :", err);
          errorMessage.value = "Impossible de charger les métiers likés.";
        }
      };
  
      // Récupérer les détails d'un métier
      const fetchJobDetails = async (jobId) => {
        try {
          const { data, error } = await supabase
            .from("metiers_id")
            .select("*")
            .eq("romesV3_value", jobId)
            .single();
  
          if (error) {
            console.error(`❌ Erreur pour le métier ${jobId} :`, error);
            return null;
          }
  
          data.imageUrl = await fetchImage(data.libelleAppellation);
          return data;
        } catch (err) {
          console.error("❌ Erreur lors de la récupération du métier :", err);
          return null;
        }
      };
  
      // Récupérer une image associée au métier
      const fetchImage = async (query) => {
        try {
          const response = await fetch(
            `https://www.googleapis.com/customsearch/v1?q=${query}&cx=${searchEngineId}&searchType=image&num=1&key=${googleApiKey}`
          );
          const data = await response.json();
          return data.items?.[0]?.link || "";
        } catch (error) {
          console.error("❌ Erreur lors de la récupération de l'image :", error);
          return "";
        }
      };
  
      // Supprimer un like
      const removeLike = async (jobId) => {
        try {
          const { error } = await supabase
            .from("liked_cards")
            .delete()
            .eq("user_id", user.value.id)
            .eq("job_id", jobId);
  
          if (error) {
            console.error("❌ Erreur lors de la suppression du like :", error);
          } else {
            likedJobs.value = likedJobs.value.filter((job) => job.romesV3_value !== jobId);
            console.log("🗑️ Métier supprimé des likes :", jobId);
          }
        } catch (err) {
          console.error("❌ Erreur :", err);
        }
      };
  
      // Ouvrir la pop-up
      const openPopup = (index) => {
        selectedJob.value = likedJobs.value[index];
        showPopup.value = true;
      };
  
      // Déconnexion
      const signOut = async () => {
        await supabase.auth.signOut();
        user.value = null;
        likedJobs.value = [];
      };
  
      return {
        user,
        likedJobs,
        errorMessage,
        signOut,
        removeLike,
        showPopup,
        selectedJob,
        openPopup,
      };
    },
  };
  </script>
  
  <style scoped>
  /* Ajoute ici le style similaire à Home.vue */
  </style>
  