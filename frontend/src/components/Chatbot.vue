<template>
    <div>
      <router-link to="/">
      <img :src="logo" alt="Logo" class="logo">
    </router-link>
    <router-view />
  </div>
    <div class="chatbot-container">
      <h1>💬 Mon conseiller</h1>
      <div class="chat-box">
        <div class="chat-messages">
          <div v-for="(message, index) in messages" :key="index" :class="message.role">
            <strong>{{ message.role === 'user' ? '👤 Toi' : '🤖 Mme Pichon' }} :</strong>
            {{ message.content }}
          </div>
        </div>
        <div class="chat-input">
          <input
            v-model="userInput"
            type="text"
            placeholder="Tapez votre message ici..."
            @keyup.enter="sendMessage"
          />
          <button @click="sendMessage">Envoyer</button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import logo from '../assets/logo.png';
  export default {
    data() {
      return {
        userInput: "", // Message saisi par l'utilisateur
        messages: [], // Historique des messages
        logo
      };
    },
    methods: {
        async sendMessage() {
  if (this.userInput.trim() === "") return; // Ignore les messages vides

  // Ajoute le message utilisateur à l'historique
  this.messages.push({ role: "user", content: this.userInput });

  try {
    const response = await fetch("http://localhost:5002/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: this.userInput }),
    });

    const data = await response.json();
    console.log("Réponse API :", data);

    if (data.response) {
      this.messages.push({ role: "assistant", content: data.response });
    } else {
      console.error("Réponse API incorrecte :", data);
      alert("Erreur : la réponse de l'API est invalide.");
    }

    // 🔹 Efface le champ de saisie après l'envoi
    this.userInput = "";

  } catch (error) {
    console.error("Erreur lors de l'envoi du message :", error);

    if (!this.messages.some(msg => msg.role === "assistant")) {
      alert("Une erreur s'est produite. Veuillez réessayer.");
    }
  }
}

    },
  };
  </script>
  
  <style scoped>
  .chatbot-container {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 10px;
    background-color: #25307c;
  }
  
  .chat-box {
    display: flex;
    flex-direction: column;
    height: 500px;
    background: #1576ba;
  }
  
  .chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    margin-bottom: 10px;
    background-color: #fff;
  }
  
  .chat-messages .user {
    color: #333;
    margin-bottom: 10px;
  }
  
  .chat-messages .assistant {
    color: #555;
    margin-bottom: 10px;
  }
  
  .chat-input {
    display: flex;
    gap: 10px;
  }
  
  .chat-input input {
    flex: 1;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
  }
  
  .chat-input button {
    padding: 10px 20px;
    background-color: #ff4d4d;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }
  
  .chat-input button:hover {
    background-color: #cc0000;
  }
  .navbar {
  position: fixed;
  top: 10px;
  left: 10px;
  z-index: 1000;
}

.logo {
  position: fixed;  /* Fixe le logo en haut à gauche de l'écran */
  top: -10px;        /* Distance par rapport au haut */
  left: -10px;       /* Distance par rapport à la gauche */
  width: 200px;      /* Ajuste la taille du logo selon tes besoins */
  height: auto;
  cursor: pointer;  /* Change le curseur pour montrer que c'est cliquable */
  z-index: 1000;    /* S'assure que le logo reste au-dessus des autres éléments */
}

  </style>