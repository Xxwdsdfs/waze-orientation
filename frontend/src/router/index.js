import { createRouter, createWebHistory } from 'vue-router';
import Home from '../components/Home.vue'; // Nouveau composant pour la recherche
import FormationDetails from '../components/FormationDetails.vue';

const routes = [
  { path: '/', component: Home }, // Remplace App.vue par Home.vue
  { path: '/formation/:id', component: FormationDetails }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
