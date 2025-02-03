<template>
    <div class="profile-container">
      <h1>Mon Profil</h1>
  
      <div v-if="user">
        <p><strong>Email :</strong> {{ user.email }}</p>
        <button @click="signOut" class="logout-button">Se Déconnecter</button>
  
        <h2>📌 Cartes Likées</h2>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
  
        <div v-if="likedCards.length > 0" class="cards-container">
        <div v-for="card in likedCards" :key="card.job_id" class="card">
            <!-- Nom du métier -->
            <h2>{{ card.libelleappellation }}</h2>

            <!-- Image du métier -->
            <div class="image-container">
            <img v-if="card.imageurl" :src="card.imageurl" alt="Image du métier" class="job-image"/>
            <div v-else class="placeholder-image">Image non trouvée</div>
            </div>

            <!-- Boutons -->
            <div class="card-buttons">
            <button class="remove-button" @click="removeLike(card.job_id)">
                ❌ Supprimer
            </button>
            <button class="info-button" @click="toggleDetails(card)">
                ℹ️ {{ selectedCard === card ? "Masquer" : "En savoir plus" }}
            </button>
            </div>
        </div>
        </div>
        <!-- Fenêtre modale pour afficher la carte en plein écran -->
        <div v-if="selectedCard" class="popup-overlay" @click.self="selectedCard = null">
            <div class="popup">
            <!-- Titre du métier en haut à gauche -->
            <h2 class="popup-title">{{ selectedCard.libelleappellation }}</h2>

            <!-- Conteneur de l'image -->
            <div class="popup-image-container">
                <img v-if="selectedCard.imageurl" :src="selectedCard.imageurl" alt="Image du métier" class="popup-job-image"/>
                <div v-else class="placeholder-image">Image non trouvée</div>
            </div>

            <!-- Conteneur du texte -->
            <div class="popup-text-container">
                <h3>Description</h3>
                <p>{{ selectedCard.accroche_metier }}</p>

                <h3>Informations</h3>
                <p>{{ selectedCard.acces_metier }}</p>

                <h3>Compétences</h3>
                <p>{{ selectedCard.centres_interet }}</p>

                <h3>Formations</h3>
                <ul v-if="selectedCard.formations && selectedCard.formations.length">
                <li v-for="formation in cleanFormations(selectedCard.formations)" :key="formation">
                    <router-link :to="'/formation/' + formation.split(':')[0].trim()">
                    {{ formation }}
                    </router-link>
                </li>
                </ul>
            </div>

            <button class="close-btn" @click="selectedCard = null">✖</button>
            </div>
        </div>
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
      const likedCards = ref([]);
      const errorMessage = ref("");
      const selectedCard = ref(null);
  
      // Vérifier l'authentification et charger les likes
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
  
      // Récupérer les métiers likés
      const fetchLikedJobs = async () => {
        if (!user.value) return;
  
        try {
          const { data, error } = await supabase
            .from("liked_cards")
            .select("*")
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
  
      // Supprimer un like
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
  
      const toggleDetails = (card) => {
        selectedCard.value = selectedCard.value === card ? null : card;
        };

      // Nettoyer les formations pour supprimer les caractères inutiles
      const cleanFormations = (formations) => {
        if (!formations) return [];
        return formations.map(f => f.replace(/[\[\]']/g, ''));
      };
  
      // Déconnexion
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
        selectedCard,
        toggleDetails,
        cleanFormations,
      };
    },
  };
  </script>
  
  <style scoped>
.profile-container {
  max-width: 100%; /* 🔥 Augmente la largeur */
  margin: auto;
  padding: 20px;
  background: #222;
  color: white;
  border-radius: 10px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
  text-align: center;
}

.cards-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: center;
  max-width: 1200px; /* 🔥 Ajuste selon ton besoin */
  margin: auto;
}

.card {
  width: 250px;
  background: #222;
  padding: 15px;
  border-radius: 10px;
  text-align: center;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
}
  
  .logout-button {
    background: red;
    color: white;
    padding: 10px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    margin-bottom: 20px;
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
  
  .card h2 {
    margin-bottom: 10px;
  }
  
.image-container {
  width: 100%;
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 8px;
  background: #444;
}
  
  .job-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 8px;
  }
  
  .placeholder-image {
    color: white;
    text-align: center;
    padding: 50px;
  }
  
  .card-buttons {
    display: flex;
    justify-content: space-around;
    margin-top: auto; /* 🔥 Pousse les boutons vers le bas */
  }
  
  .cards-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: center;
  max-width: 1200px;
  margin: auto;
}

.card {
  width: 250px;
  background: #222;
  padding: 15px;
  border-radius: 10px;
  text-align: center;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  justify-content: space-between; /* 🔥 Assure que tout est bien réparti */
}

.image-container {
  width: 100%;
  height: 150px; /* 🔥 Fixe une hauteur identique */
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 8px;
  background: #444;
}

.job-image {
  width: 100%;
  height: 100%;
  object-fit: cover; /* 🔥 Ajuste l'image sans la déformer */
  border-radius: 8px;
}

.card-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: auto; /* 🔥 Pousse les boutons vers le bas */
}

.remove-button, .info-button {
  flex: 1; /* 🔥 Pour qu'ils aient la même largeur */
  margin: 5px;
  padding: 8px 10px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  color: white;
}

.remove-button {
  background: #ff4d4d;
}

.info-button {
  background: #007bff;
}

.remove-button:hover {
  background: #cc0000;
}

.info-button:hover {
  background: #0056b3;
}

  
  .details-container {
    margin-top: 15px;
    padding: 10px;
    background: #2e2e2e;
    border-radius: 8px;
    text-align: left;
  }
  
  .details-container h3 {
    margin-bottom: 5px;
  }
  .card:hover {
  transform: scale(1.05);
  transition: transform 0.3s ease-in-out;
}
.remove-button:hover {
  background: #cc0000;
}

.info-button:hover {
  background: #0056b3;
}

.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.popup {
  display: flex;
  flex-direction: row; /* 🔥 Place l'image à gauche et le texte à droite */
  align-items: center;
  justify-content: space-between;
  background: #2e2e2e;
  padding: 20px;
  border-radius: 10px;
  max-width: 90vw; /* 🔥 Plus large */
  max-height: 80vh;
  overflow: auto;
  gap: 20px; /* 🔥 Espace entre l'image et le texte */
}


.popup-image-container {
  flex: 1;
  display: flex;
  align-items: flex-start; /* 🔥 Place l'image en haut */
  justify-content: flex-start; /* 🔥 La colle à gauche */
  background: #444;
  border-radius: 8px;
  overflow: hidden;
  max-width: 45%; /* 🔥 Augmente légèrement la largeur de l'image */
  height: auto;
}


.popup-job-image {
  width: 30%; /* 🔥 Prend toute la largeur du conteneur */
  height: auto; /* 🔥 S’adapte à la hauteur */
  object-fit: cover; /* 🔥 Ajuste sans déformer */
  border-radius: 8px;
  position: absolute;
  top: 25%;
  
}


.popup-details {
  flex: 2;
  padding-left: 10px;
  overflow-y: auto;
  color: white;
  margin-top: 60px;
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 20px;
  color: white;
  cursor: pointer;
}

.popup-text-container {
  flex: 2; /* 🔥 Prend plus d’espace que l’image */
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: left;
  color: white;
  max-width: 60%; /* 🔥 Pour équilibrer avec l'image */
  margin-top: 15%;
}
.popup-title {
  position: absolute;
  top: 6%; /* 🔥 Ajuste l'espace au-dessus */
  left: 10%; /* 🔥 Décale à gauche */
  font-size: 1.8em;
  font-weight: bold;
  color: white;
}


  </style>
  