<template>
  <div class="formation-details">
    <h1 class="title">Détails de la Formation</h1>
    <div v-if="loading" class="loading">Chargement...</div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="formation" class="content">
      <h2 class="formation-title">{{ formation.libelle_complet }}</h2>
      <div class="info-grid">
        <div class="info-box">
          <h3>Durée</h3>
          <p>{{ formation.duree_formation }}</p>
        </div>
        <div class="info-box">
          <h3>Niveau de certification</h3>
          <p>{{ formation.niveau_certification || "Non disponible" }}</p>
        </div>
      </div>
      
      <div class="description">
        <h3>Description</h3>
        <p>{{ formation.descriptif_format_court || "Non disponible" }}</p>
      </div>
      
      <div class="access-study">
        <div class="info-box">
          <h3>Accès</h3>
          <p>{{ formation.descriptif_acces || "Non disponible" }}</p>
        </div>
        <div class="info-box">
          <h3>Poursuite d'études</h3>
          <p>{{ formation.descriptif_poursuite_etudes || "Non disponible" }}</p>
        </div>
      </div>
      
      <div class="type-formation">
        <h3>Type de formation</h3>
        <p>{{ formation.type_formation_libelle || "Non disponible" }}</p>
      </div>
      
      <div v-if="formation.url" class="more-info">
        <h3>Plus d'infos</h3>
        <a :href="formation.url" target="_blank">Consulter le site officiel</a>
      </div>
    </div>
  </div>

  <!-- ✅ Section des écoles associées -->
  <div v-if="ecoles.length > 0" class="ecoles-section">
    <div class="ecoles-header">
      <h3>Écoles associées</h3>
    </div>

    <div class="ecoles-container">
    <div v-for="ecole in ecoles" :key="ecole.id" class="ecole-card">
      <h4>🏫 {{ ecole["Lieu d'enseignement (ENS) libellé"] }}</h4>
      <p><strong>📍 Adresse :</strong> {{ ecole["ENS adresse"] || "Non renseignée" }}</p>
      <p><strong>📜 Statut :</strong> {{ ecole["ENS statut"] || "Non renseigné" }}</p>
      <p><strong>♿ Accessibilité :</strong> {{ ecole["ENS accessibilité"] || "Non renseignée" }}</p>
      <p><strong>📚 Modalité :</strong> {{ ecole["AF modalités scolarité"] || "Non renseignée" }}</p>
      <p><strong>💰 Coût :</strong> {{ ecole["AF coût scolarité"] || "Non renseigné" }}</p>
      <p v-if="distances[ecole['Lieu d\'enseignement (ENS) libellé']]">
        🚗 Distance : {{ distances[ecole["Lieu d'enseignement (ENS) libellé"]] }} km
      </p>
      <p>
        <strong>🔗 Lien :</strong> 
        <a :href="ecole['ENS site web']" target="_blank">
          Voir l'établissement
        </a>
      </p>
    </div>
  </div>
<div class="map-container">
  <h3>📍 Localisation des établissements</h3>
  <button @click="getUserLocation" class="location-button">
    📍 Activer ma localisation
  </button>
  <iframe v-if="showMap && mapUrl" :src="mapUrl" width="100%" height="400px" frameborder="0"></iframe>
  <button @click="toggleMap" class="map-button">
    {{ showMap ? "Masquer la carte" : "Voir la carte" }}
  </button>
</div>


  </div>
</template>

<script>import { ref, onMounted } from "vue";
import { supabase } from "../supabase";

export default {
  data() {
    return {
      formation: null,
      ecoles: [],
      loading: false,
      error: null,
      errorMessage: null,
      showMap: false,  // ✅ Ajout de l'état pour afficher/masquer la carte
      mapUrl: "",  // ✅ URL sera mise à jour dynamiquement
      formationId: "",  // ✅ Stocke le formation_id récupéré
      userLocation: null, // ✅ Stocke la localisation du user
      distances: {}, // ✅ Stocke les distances entre le user et chaque école
    };
  },
  async created() {
    this.loading = true;
    const id = this.$route.params.id;
    try {
      const response = await fetch(`http://localhost:5000/formation/${id}`);
      if (!response.ok) throw new Error("Erreur lors de la récupération des données.");
      this.formation = await response.json();

      this.formationId = this.extractCodeFOR(id);  // ✅ Stocke le formation_id

      if (this.formationId) {
        await this.fetchEcoles(this.formationId);
        this.updateMapUrl();  // ✅ Mise à jour de l'URL après récupération du formation_id
      }
    } catch (err) {
      this.error = err.message;
    } finally {
      this.loading = false;
    }
  },
  methods: {
    extractCodeFOR(id) {
      if (!id) return null;
      const match = id.match(/(FOR\.\d+)/);
      return match ? match[1] : null;
    },

    async fetchEcoles(forId) {
      if (!forId) return;
      try {
        const { data, error } = await supabase
          .from("ecoles")
          .select("*")
          .eq("formation_id", forId);

        if (error) throw error;
        this.ecoles = data;
        
        // ✅ Met à jour les distances si la localisation du user est déjà connue
        if (this.userLocation) {
          this.calculateDistances();
        }
      } catch (err) {
        this.error = err.message;
      }
    },

    updateMapUrl() {
      if (this.formationId) {
        this.mapUrl = `http://localhost:5001/generate_map?formation_id=${this.formationId}`;
        console.log("URL de la carte mise à jour :", this.mapUrl);
      }
    },

    toggleMap() {
      this.showMap = !this.showMap;
      if (this.showMap) {
        this.updateMapUrl();  // ✅ Mise à jour de l'URL avant affichage
      }
    },

    // ✅ Récupération de la localisation du user
    getUserLocation() {
      if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            this.userLocation = {
              lat: position.coords.latitude,
              lon: position.coords.longitude,
            };
            console.log("📍 Localisation utilisateur :", this.userLocation);
            this.calculateDistances(); // ✅ Calcul des distances après récupération
          },
          (error) => {
            console.error("❌ Erreur de géolocalisation :", error.message);
          }
        );
      } else {
        console.error("❌ Géolocalisation non supportée par ce navigateur.");
      }
    },

    // ✅ Calcul des distances entre le user et les écoles
    calculateDistances() {
      if (!this.userLocation || !this.ecoles.length) return;

      this.distances = {}; // Réinitialisation

      this.ecoles.forEach((ecole) => {
        if (ecole["ENS latitude"] && ecole["ENS longitude"]) {
          const lat1 = this.userLocation.lat;
          const lon1 = this.userLocation.lon;
          const lat2 = parseFloat(ecole["ENS latitude"]);
          const lon2 = parseFloat(ecole["ENS longitude"]);

          const R = 6371; // Rayon de la Terre en km
          const dLat = ((lat2 - lat1) * Math.PI) / 180;
          const dLon = ((lon2 - lon1) * Math.PI) / 180;
          const a =
            Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos((lat1 * Math.PI) / 180) *
              Math.cos((lat2 * Math.PI) / 180) *
              Math.sin(dLon / 2) *
              Math.sin(dLon / 2);
          const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
          const distance = R * c; // Distance en km

          this.distances[ecole["Lieu d'enseignement (ENS) libellé"]] = distance.toFixed(2);
          ecole.distance = distance; // ✅ Ajoute la distance à chaque école
        }
      });

      console.log("📏 Distances calculées :", this.distances);
      this.ecoles.sort((a, b) => a.distance - b.distance);
    }
  }
};
</script>

<style scoped>
.formation-details {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background: #25307c;
  color: #fff;
  border-radius: 10px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
}

.title {
  text-align: center;
  font-size: 2em;
  margin-bottom: 20px;
}

.h3 {
  color: #f9efe3;
}

.formation-title {
  text-align: center;
  font-size: 1.8em;
  color: #fff;
}

.info-grid {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 20px;
}

.info-box {
  flex: 1;
  background: #1576ba;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  color: #f9efe3;
}

.description, .type-formation, .more-info {
  background: #1576ba;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
}

.access-study {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 20px;
}

h3 {
  color: #25307c;
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

.ecoles-section {
  max-width: 90%;
  margin: 20px auto;
  padding: 15px;
  background: #25307c;
  border-radius: 10px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.ecoles-section h3{
  color: #fff;
}

.ecoles-container {
  max-height: 200px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding-right: 10px;
}

.ecole-card {
  background: #1576ba;
  padding: 10px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
}

.ecole-card h4 {
  font-size: 1.2em;
  color: #25307c;
}

.ecole-card p {
  font-size: 0.9em;
  color: #fff;
}

.ecoles-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.location-button {
  background: #007bff;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1em;
  display: block;
  margin: 10px auto;
}

.location-button:hover {
  background: #0056b3;
}
.map-button{
  background: #ff4d4d;
}
.map-button:hover{
  background: #cc0000;
}
</style>
