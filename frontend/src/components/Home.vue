<template>
  <!-- Bouton pour gérer l'authentification et le profil -->
  <div class="auth-container">
    <button class="auth-button" @click="toggleAuthMenu">
      {{ user ? "👤 " + user.email : "Se connecter" }}
    </button>

    <!-- Menu déroulant affiché si authMenuVisible est true -->
    <div v-if="authMenuVisible" class="auth-menu">
      <router-link v-if="user" to="/profil" class="auth-menu-item">👤 Mon Profil</router-link>
      <button v-if="user" class="auth-menu-item" @click="signOut">🚪 Se Déconnecter</button>
      <button v-else class="auth-menu-item" @click="showAuthModal = true">🔑 Se Connecter</button>
    </div>
  </div>

  <!-- Fenêtre modale pour l'authentification -->
  <div v-if="showAuthModal" class="auth-modal">
    <div class="auth-modal-content">
      <button class="close-btn" @click="showAuthModal = false">✖</button>

      <h3 v-if="!user">Connexion / Inscription</h3>
      <h3 v-else>Bienvenue, {{ user.email }} !</h3>

      <div v-if="!user">
        <form @submit.prevent="isSignUp ? signUp() : signIn()">
          <input type="email" v-model="email" placeholder="Email" required />
          <input type="password" v-model="password" placeholder="Mot de passe" required />
          <button type="submit">{{ isSignUp ? "S'inscrire" : "Se connecter" }}</button>
        </form>

        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

        <p @click="isSignUp = !isSignUp" class="switch-auth">
          {{ isSignUp ? "Déjà un compte ? Se connecter" : "Pas encore de compte ? S'inscrire" }}
        </p>
      </div>

      <div v-else>
        <button @click="signOut">Se déconnecter</button>
      </div>
    </div>
  </div>

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
          <div class="popup" 
               :class="{ fullscreen: showDetails }"
               @mousedown="startDrag" 
               @touchstart="startDrag">
            <button class="close-btn" @click="showPopup = false">✖</button>

            <!-- Nom du métier -->
            <h2>{{ results[currentIndex].libelleAppellation }}</h2>

            <!-- Image du métier (masquée si détails affichés) -->
            <div class="image-container" v-if="!showDetails">
              <img v-if="imageUrl" :src="imageUrl" alt="Image du métier" class="job-image"/>
              <div v-else class="placeholder-image">Image non trouvée</div>
            </div>

            <!-- Boutons -->
            <div class="card-buttons">
              <button class="like-button" @click="likeCard(results[currentIndex].codeRome)">
                ❤️ J'aime
              </button>
              <button class="info-button" @click="toggleDetails">
                ℹ️ {{ showDetails ? "Masquer" : "En savoir plus" }}
              </button>
            </div>

            <!-- Détails affichés seulement si showDetails est true -->
            <div v-if="showDetails" class="details-container">
              <h3>Description</h3>
              <p>{{ results[currentIndex].accroche_metier }}</p>

              <h3>Informations</h3>
              <p>{{ results[currentIndex].acces_metier }}</p>

              <h3>Compétences</h3>
              <p>{{ results[currentIndex].centres_interet }}</p>

              <h3>Formations</h3>
              <ul v-if="results[currentIndex].formations.length">
                <li v-for="formation in results[currentIndex].formations" :key="formation">
                  <router-link :to="'/formation/' + formation.replace(/[\[\]']/g, '').split(':')[0].trim()">
                    {{ formation.replace(/[\[\]']/g, '') }}
                  </router-link>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </transition>
    </div>

    <router-view></router-view>

    <button class="chat-button" @click="showChat = !showChat">💬</button>

    <div v-if="showChat" class="chat-window">
      <div class="chat-header">
        <span>Chatbot</span>
        <button class="close-chat" @click="showChat = false">✖</button>
      </div>
      <div class="chat-body">
        <div v-for="(msg, index) in messages" :key="index" class="chat-message">
          <span class="user-message">{{ msg.text }}</span>
        </div>
      </div>
      <div class="chat-input">
        <input type="text" v-model="chatInput" @keyup.enter="sendMessage" placeholder="Écrivez un message..." />
        <button @click="sendMessage">➤</button>
      </div>
    </div>
  </div>
</template>


<script>
import { ref, onMounted, nextTick } from "vue";
import { supabase } from "../supabase";

export default {
  setup() {
    // 🔷 Variables de recherche de métiers
    const intitule = ref('');
    const contexte = ref('');
    const results = ref([]);
    const error = ref(null);
    const currentIndex = ref(0);
    const showPopup = ref(false);
    const showDetails = ref(false);


    // 🔷 Variables pour le chat
    const showChat = ref(false);
    const chatInput = ref("");
    const messages = ref([]);

    // 🔷 Variables pour le swipe
    const animating = ref(false);
    const decisionVal = 80;
    const pullDeltaX = ref(0);
    const deg = ref(0);
    let card;

    // 🔷 Variables d'authentification
    const email = ref("");
    const password = ref("");
    const user = ref(null);
    const errorMessage = ref("");
    const showAuthModal = ref(false);
    const isSignUp = ref(false);
    const authMenuVisible = ref(false);

    // google moteur de recherche
    const googleApiKey = "AIzaSyALaDmNqgh1pm9gh9RbIYPVO-mu5LK9GgE"; // 🔥 Remplace par ta clé API
    const searchEngineId = "64a394dee20f849b9"; // 🔥 Ton ID de moteur de recherche
    const imageUrl = ref(""); // Pour stocker l'image récupérée

    const toggleDetails = () => {
      showDetails.value = !showDetails.value;
    };

    const toggleAuthMenu = () => {
      authMenuVisible.value = !authMenuVisible.value;
    };

    const likeCard = async (jobId) => {
      if (!user.value) {
        alert("Vous devez être connecté pour liker un métier.");
        return;
      }

      try {
        const { data, error } = await supabase
          .from("liked_cards")
          .insert([
            { user_id: user.value.id, job_id: jobId }
          ]);

        if (error) {
          console.error("Erreur lors du like :", error.message);
        } else {
          console.log("Métier liké avec succès :", data);
        }
      } catch (err) {
        console.error("Erreur :", err);
      }
    };

    const fetchImage = async (query) => {
      try {
        console.log("🔍 Recherche d'image pour :", query); // Ajoute ce log

        const response = await fetch(
          `https://www.googleapis.com/customsearch/v1?q=${query}&cx=${searchEngineId}&searchType=image&num=1&key=${googleApiKey}`
        );
        
        const data = await response.json();
        console.log("📸 Résultat API Google :", data); // Ajoute ce log

        if (data.items && data.items.length > 0) {
          imageUrl.value = data.items[0].link; // Stocke la première image trouvée
          console.log("✅ Image trouvée :", imageUrl.value);
        } else {
          imageUrl.value = ""; // Aucun résultat trouvé
          console.log("❌ Aucune image trouvée !");
        }
      } catch (error) {
        console.error("❌ Erreur lors de la récupération de l'image :", error);
        imageUrl.value = "";
      }
    };
    const handleImage = async () => {
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
        results.value = data;
        showPopup.value = true;

        // 🔥 Ajoute cet appel pour récupérer l'image
        await fetchImage(results.value[0].libelleAppellation);
      } catch (err) {
        error.value = err.message;
      }
    };


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
    results.value = data;
    showPopup.value = true;

    // 🔥 Ajoute cet appel pour récupérer l'image immédiatement
    if (results.value.length > 0) {
      await fetchImage(results.value[0].libelleAppellation);
    }
  } catch (err) {
    error.value = err.message;
  }
};


    // 🟢 Fonction pour tronquer le texte
    const truncateText = (text, length) => {
      if (!text) return 'Non disponible';
      return text.length > length ? text.substring(0, length) + '...' : text;
    };

    // 🔵 Fonctions de navigation entre résultats
    const nextResult = async () => {
      if (currentIndex.value < results.value.length - 1) {
        card.style.transition = "transform 0.3s ease-out, opacity 0.3s ease-out";
        card.style.transform = "translateX(100vw) rotate(30deg)";
        card.style.opacity = "0";
        await new Promise(resolve => setTimeout(resolve, 300));
        currentIndex.value++;
        await nextTick();
        resetCardPosition();
      }
    };

    const prevResult = async () => {
      if (currentIndex.value > 0) {
        card.style.transition = "transform 0.3s ease-out, opacity 0.3s ease-out";
        card.style.transform = "translateX(-100vw) rotate(-30deg)";
        card.style.opacity = "0";
        await new Promise(resolve => setTimeout(resolve, 300));
        currentIndex.value--;
        await nextTick();
        resetCardPosition();
      }
    };

    // 🔵 Fonction pour gérer le swipe
    function pullChange() {
      animating.value = true;
      deg.value = pullDeltaX.value / 10;
      card.style.transform = `translateX(${pullDeltaX.value}px) rotate(${deg.value}deg)`;
    }

    function release() {
      if (pullDeltaX.value >= decisionVal) {
        nextResult();
      } else if (pullDeltaX.value <= -decisionVal) {
        prevResult();
      } else {
        resetCardPosition();
      }
      pullDeltaX.value = 0;
      animating.value = false;
    }

    function resetCardPosition() {
      if (card) {
        card.style.transition = "transform 0.3s ease-out, opacity 0.3s ease-out";
        card.style.transform = "translateX(0) rotate(0)";
        card.style.opacity = "1";
        setTimeout(() => {
          card.style.transition = "";
        }, 300);
      }
    }

    function startDrag(event) {
      if (animating.value) return;

      card = event.currentTarget;
      card.style.zIndex = "2";
      const nextCard = document.querySelectorAll(".popup")[currentIndex.value + 1];
      if (nextCard) {
        nextCard.style.zIndex = "1";
        nextCard.style.opacity = "0.5";
        nextCard.style.transform = "scale(0.95)";
      }
      
      const startX = event.pageX || event.touches[0].pageX;

      function onMove(e) {
        const x = e.pageX || e.touches[0].pageX;
        pullDeltaX.value = x - startX;
        pullChange();
      }

      function onEnd() {
        document.removeEventListener("mousemove", onMove);
        document.removeEventListener("mouseup", onEnd);
        document.removeEventListener("touchmove", onMove);
        document.removeEventListener("touchend", onEnd);
        release();
      }

      document.addEventListener("mousemove", onMove);
      document.addEventListener("mouseup", onEnd);
      document.addEventListener("touchmove", onMove);
      document.addEventListener("touchend", onEnd);
    }

    onMounted(() => {
      document.querySelectorAll(".popup").forEach((el, index) => {
        el.style.zIndex = `${results.value.length - index}`;
        el.style.position = "absolute";
        el.style.top = "0";
        el.style.left = "50%";
        el.style.transform = "translateX(-50%) scale(1)";
        el.addEventListener("mousedown", startDrag);
        el.addEventListener("touchstart", startDrag);
      });
    });

    // 🟢 Fonction pour envoyer un message dans le chat
    const sendMessage = () => {
      if (chatInput.value.trim() !== "") {
        messages.value.push({ text: chatInput.value, sender: "user" });
        chatInput.value = ""; // Vider le champ de texte après envoi
      }
    };

    // Vérifier si un utilisateur est connecté au chargement de l'application
    onMounted(async () => {
      const { data: session } = await supabase.auth.getSession();
      if (session && session.user) {
        user.value = session.user;
      }

      // Écoute les changements de session (connexion/déconnexion)
      supabase.auth.onAuthStateChange((event, session) => {
        user.value = session ? session.user : null;
      });
    });


    // 🟠 Authentification avec Supabase
    const signUp = async () => {
      errorMessage.value = "";
      const { data, error } = await supabase.auth.signUp({
        email: email.value,
        password: password.value,
      });

      if (error) {
        errorMessage.value = error.message;
      } else {
        user.value = data.user;
      }
    };

    const signIn = async () => {
      errorMessage.value = "";
      const { data, error } = await supabase.auth.signInWithPassword({
        email: email.value,
        password: password.value,
      });

      if (error) {
        errorMessage.value = error.message;
      } else {
        user.value = data.user;
      }
    };

    const signOut = async () => {
      await supabase.auth.signOut();
      user.value = null;
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
      startDrag,
      showChat,
      chatInput,
      messages,
      sendMessage,
      email,
      password,
      user,
      errorMessage,
      showAuthModal,
      isSignUp,
      signUp,
      signIn,
      signOut,
      imageUrl,
      fetchImage,
      handleImage,
      showDetails, 
      toggleDetails,
      toggleAuthMenu,
      authMenuVisible,
      likeCard,
    };
  },
};
</script>


<style lang="scss" scoped>
*, *:before, *:after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body {
  font-size: 62.5%;
}
body {
  background: #63BDF7;
  overflow: hidden;
}

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
  width: 30%;
  height: auto;
  text-align: center;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease-in-out;
  cursor: grab;
  position: relative;
}

/* Mode "plein écran" pour afficher les détails */
.popup.fullscreen {
  width: 70%; /* 🔥 Augmente la largeur */
  height: 80vh; /* 🔥 Augmente en hauteur */
  max-height: 90vh;
  overflow-y: auto;
  padding: 40px;
}

.image-container.hidden {
  display: none; /* 🔥 Cache l'image */
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

.demo {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 30.6rem;
  height: 54rem;
  margin-left: calc(30.6rem / -2);
  margin-top: calc(54rem / -2);
  background: #F6F6F5;
  box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.2);
  
  &__card {
    z-index: 2;
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    transform-origin: 50% 100%;
    transition: transform 0.3s ease-out;
    
    &.to-left {
      transform: translateX(-30rem) rotate(-30deg) !important;
    }
    
    &.to-right {
      transform: translate(30rem) rotate(30deg) !important;
    }
  }
  
  &__drag {
    z-index: 5;
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    cursor: grab;
  }
}
.like-button {
  background: #ff4d4d;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1.2em;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 10px;
}

.chat-button {
  position: fixed;
  bottom: 20px;
  left: 20px;
  background: #e59400;
  color: white;
  border: none;
  padding: 15px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.5em;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
}

.chat-button:hover {
  background: #0056b3;
}

.chat-window {
  position: fixed;
  bottom: 80px;
  left: 20px;
  width: 300px;
  background: white;
  border-radius: 10px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
}

.chat-header {
  background: #e59400;
  color: white;
  padding: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
}

.chat-body {
  padding: 10px;
  height: 200px;
  overflow-y: auto;
}


.chat-input {
  display: flex;
  padding: 10px;
  border-top: 1px solid #ccc;
}

.chat-input input {
  flex: 1;
  padding: 8px;
  border: none;
  border-radius: 5px;
}

.chat-input button {
  background: #e59400;
  color: white;
  border: none;
  padding: 8px 10px;
  cursor: pointer;
  margin-left: 5px;
  border-radius: 5px;
}

.chat-message {
  background: #e1f5fe;
  padding: 8px;
  border-radius: 5px;
  margin-bottom: 5px;
  color: rgba(0, 0, 0);
}

.close-chat {
  background: none;
  border: none;
  color: white;
  font-size: 1.2em;
  cursor: pointer;
}
.auth-button {
  position: fixed;
  top: 20px;
  right: 20px;
  background: #e59400;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 1em;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
}

.auth-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
}

.auth-modal-content {
  background: #1e1e1e;
  padding: 20px;
  border-radius: 10px;
  width: 350px;
  text-align: center;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
  color: white;
  position: relative;
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 1.2em;
  cursor: pointer;
}
.card-image {
  width: 100%;
  height: 250px;
  background: #444;
  border-radius: 8px;
  margin: 15px 0;
}

.card-buttons {
  display: flex;
  justify-content: space-around;
  margin-top: 50px;
}
.info-button {
  background: #007bff;
}

.like-button:hover {
  background: #cc0000;
}

.info-button:hover {
  background: #0056b3;
}

/* Masquer l'image lorsqu'on affiche les détails */
.image-container {
  width: 100%;
  height: 250px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 8px;
  margin-top: 30px;
  background: #444;
}


.job-image {
  width: 100%; /* Prend toute la largeur */
  height: 100%; /* Prend toute la hauteur */
  object-fit: cover; /* Ajuste l'image sans la déformer */
  border-radius: 8px; /* Arrondi les bords */
}

.details-section {
  margin-top: 15px;
  padding: 10px;
  background: #2e2e2e;
  border-radius: 8px;
  text-align: left;
  color: white;
}

.details-section p {
  margin: 5px 0;
}

.details-section ul {
  list-style-type: none;
  padding: 0;
}

.details-section li {
  background: #444;
  padding: 5px;
  border-radius: 5px;
  margin-top: 5px;
}
.auth-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 100;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.auth-button {
  background: #e59400;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 1em;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
  transition: background 0.3s ease-in-out;
}

.auth-button:hover {
  background: #d48400;
}

.auth-menu {
  position: absolute;
  top: 110%; /* Ajustement pour éviter le chevauchement */
  right: 0;
  background: #d48400;
  border-radius: 8px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  min-width: 180px;
  padding: 5px 0;
  opacity: 0;
  transform: translateY(-5px);
  transition: opacity 0.2s ease-in-out, transform 0.2s ease-in-out;
  visibility: hidden;
}

.auth-container:hover .auth-menu {
  opacity: 1;
  transform: translateY(0);
  visibility: visible;
}

.auth-menu-item {
  padding: 12px 15px;
  text-align: left;
  color: black;
  text-decoration: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9em;
  background: #d48400;
  transition: background 0.2s ease-in-out;
}

.auth-menu-item:hover {
  background: #d48400;
}

.auth-menu-item i {
  font-size: 1.2em;
}


</style>
