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
          <div 
            class="popup"
            @mousedown="startDrag"
            @touchstart="startDrag"
          >
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
            <button class="like-button">
              ❤️ J'aime
            </button>
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

export default {
  setup() {
    // Variables pour la recherche de métiers
    const intitule = ref('');
    const contexte = ref('');
    const results = ref([]);
    const error = ref(null);
    const currentIndex = ref(0);
    const showPopup = ref(false);


    // Variables pour le chat
    const showChat = ref(false);
    const chatInput = ref("");
    const messages = ref([]);

    // Variables pour le swipe
    const animating = ref(false);
    const decisionVal = 80;
    const pullDeltaX = ref(0);
    const deg = ref(0);
    let card;

    // Fonction pour gérer la soumission du formulaire
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
      } catch (err) {
        error.value = err.message;
      }
    };

    const truncateText = (text, length) => {
      if (!text) return 'Non disponible';
      return text.length > length ? text.substring(0, length) + '...' : text;
    };

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

    // Fonctions pour le swipe
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

        // Fonction pour envoyer un message
      const sendMessage = () => {
        if (chatInput.value.trim() !== "") {
          messages.value.push({ text: chatInput.value, sender: "user" });
          chatInput.value = ""; // Vider le champ de texte après envoi
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
      startDrag,
      showChat,
      chatInput,
      messages,
      sendMessage,
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
  width: 80%;
  text-align: center;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
  transition: transform 0.3s ease-out;
  cursor: grab;
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

.like-button:hover {
  background: #cc0000;
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
</style>
