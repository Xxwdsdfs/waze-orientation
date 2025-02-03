<template>
    <div class="profile-container">
      <h1>Mon Profil</h1>
  
      <div v-if="user">
        <p><strong>Email :</strong> {{ user.email }}</p>
        <button @click="signOut" class="logout-button">Se Déconnecter</button>
  
        <h2>📌 Cartes Likées</h2>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
  
        <ul v-if="likedCards.length > 0">
          <li v-for="card in likedCards" :key="card.job_id">
            <p><strong>Nom du métier :</strong> {{ card.job_id }}</p>
            <button @click="removeLike(card.job_id)" class="remove-button">❌ Supprimer</button>
          </li>
        </ul>
  
        <p v-else>Aucun métier liké pour l'instant.</p>
      </div>
  
      <div v-else>
        <p>Veuillez vous connecter pour voir votre profil.</p>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from "vue";
  import { supabase } from "../supabase";
  
  export default {
    setup() {
      const user = ref(null);
      const likedCards = ref([]); // 🔥 Assure-toi qu'il est initialisé
      const errorMessage = ref("");
  
      // 🔥 Vérifie l'authentification et charge les likes
      onMounted(async () => {
        const { data: session } = await supabase.auth.getSession();
        if (session?.user) {
          user.value = session.user;
          await fetchLikedJobs();
        }
  
        // Écoute les changements de session
        supabase.auth.onAuthStateChange((event, session) => {
          user.value = session ? session.user : null;
          if (user.value) fetchLikedJobs();
        });
      });
  
      // 🔥 Récupérer les métiers likés
      const fetchLikedJobs = async () => {
        if (!user.value) return;
  
        try {
          const { data, error } = await supabase
            .from("liked_cards")
            .select("job_id") // 🔥 Vérifie que `job_title` existe bien
            .eq("user_id", user.value.id);
  
          if (error) {
            console.error("❌ Erreur lors du chargement des likes :", error.message);
            errorMessage.value = error.message;
          } else {
            likedCards.value = data;
            console.log("✅ Cartes likées récupérées :", likedCards.value);
          }
        } catch (err) {
          console.error("❌ Erreur :", err);
          errorMessage.value = "Impossible de charger les métiers likés.";
        }
      };
  
      // 🔥 Supprimer un like
      const removeLike = async (job_id) => {
        try {
          const { error } = await supabase
            .from("liked_cards")
            .delete()
            .eq("user_id", user.value.id)
            .eq("job_id", job_id);
  
          if (error) {
            console.error("❌ Erreur lors de la suppression du like :", error);
          } else {
            likedCards.value = likedCards.value.filter((job) => job.job_id !== job_id);
            console.log("🗑️ Métier supprimé des likes :", job_id);
          }
        } catch (err) {
          console.error("❌ Erreur :", err);
        }
      };
  
      // 🔥 Déconnexion
      const signOut = async () => {
        await supabase.auth.signOut();
        user.value = null;
        likedCards.value = [];
      };
  
      return {
        user,
        likedCards,
        errorMessage,
        signOut,
        removeLike,
      };
    },
  };
  </script>
  
  <style scoped>
  .profile-container {
    max-width: 600px;
    margin: auto;
    padding: 20px;
    background: #222;
    color: white;
    border-radius: 10px;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
    text-align: center;
  }
  
  .logout-button {
    background: red;
    color: white;
    padding: 10px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }
  
  .remove-button {
    background: #ff4d4d;
    color: white;
    padding: 5px 10px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }
  
  .error-message {
    color: red;
    font-weight: bold;
  }
  </style>
  