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
  </template>
  
  <script>
  export default {
    data() {
      return {
        formation: null,
        loading: false,
        error: null,
      };
    },
    async created() {
      this.loading = true;
      const id = this.$route.params.id;
      try {
        const response = await fetch(`http://localhost:5000/formation/${id}`);
        if (!response.ok) throw new Error("Erreur lors de la récupération des données.");
        this.formation = await response.json();
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    },
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
  </style>
  