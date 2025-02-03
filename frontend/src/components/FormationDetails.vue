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

  <!-- ✅ Ajout de l'affichage des écoles associées -->
  <div v-if="ecoles.length > 0" class="ecoles-section">
    <h3>Écoles associées</h3>
    <div class="ecoles-container">
      <div v-for="ecole in ecoles" :key="ecole.id" class="ecole-card">
        <h4>{{ ecole['Lieu d\'enseignement (ENS) libellé'] }}</h4>
        <p><strong>Statut :</strong> {{ ecole['ENS statut'] }}</p>
        <p><strong>Adresse :</strong> {{ ecole['ENS adresse'] }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { supabase } from "../supabase";

export default {
  data() {
    return {
      formation: null,
      ecoles: [], // Stocker les écoles associées
      loading: false,
      error: null,
      errorMessage: null,
    };
  },
  async created() {
    this.loading = true;
    const id = this.$route.params.id;
    try {
      // 🔹 Récupération des données de la formation depuis l'API locale
      const response = await fetch(`http://localhost:5000/formation/${id}`);
      if (!response.ok) throw new Error("Erreur lors de la récupération des données.");
      this.formation = await response.json();

      // 🔹 Extraction du FOR_ID depuis l'URL locale
      const forId = this.extractCodeFOR(id);
      console.log("🔎 Code FOR extrait depuis l'URL de la route :", forId);

      // 🔹 Si un FOR_ID est trouvé, récupérer les écoles correspondantes
      if (forId) {
        await this.fetchEcoles(forId);
      }
    } catch (err) {
      this.error = err.message;
    } finally {
      this.loading = false;
    }
  },
  methods: {
    // 🔍 Extraire le Code FOR depuis l'URL locale (en gardant "FOR.")
    extractCodeFOR(id) {
      if (!id) return null;
      const match = id.match(/(FOR\.\d+)/); // Recherche "FOR.XXXX"
      return match ? match[1] : null;
    },

    // 📚 Fonction pour récupérer les écoles associées au FOR_ID (en comparant avec formation_id)
    async fetchEcoles(forId) {
      if (!forId) return; // Évite une requête inutile

      try {
        console.log(`🔍 Recherche des écoles avec formation_id="${forId}"`);

        const { data, error } = await supabase
          .from("ecoles") // Table Supabase
          .select("*")
          .eq("formation_id", forId); // 🔍 Filtrer avec formation_id

        if (error) {
          console.error("❌ Erreur lors de la récupération des écoles :", error.message);
          this.errorMessage = error.message;
        } else {
          this.ecoles = data;

          // 📌 Vérification en console
          console.log(`✅ ${this.ecoles.length} écoles trouvées avec formation_id="${forId}"`);
          this.ecoles.forEach(ecole => {
            console.log(`🏫 École : ${ecole['Lieu d\'enseignement (ENS) libellé']}, Formation ID: ${ecole.formation_id}`);
          });
        }
      } catch (err) {
        console.error("❌ Erreur :", err);
        this.errorMessage = "Impossible de charger les écoles.";
      }
    }
  }
};
</script>


<style scoped>
.formation-details {
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

.formation-title {
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

.description, .type-formation, .more-info {
background: #2e2e2e;
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

.ecoles-section {
  max-width: 90%;
  margin: 20px auto;
  padding: 15px;
  background: #2e2e2e;
  border-radius: 10px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.ecoles-container {
  max-height: 200px; /* Hauteur limitée */
  overflow-y: auto; /* Ajoute le scroll si nécessaire */
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding-right: 10px; /* Évite le chevauchement du scrollbar */
}

.ecole-card {
  background: #3a3a3a;
  padding: 10px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
}

.ecole-card h4 {
  font-size: 1.2em;
  color: #f5a623;
}

.ecole-card p {
  font-size: 0.9em;
  color: #ddd;
}

</style>
