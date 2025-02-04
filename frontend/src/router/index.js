import { createRouter, createWebHistory } from 'vue-router';
import Home from '../components/Home.vue'; 
import FormationDetails from '../components/FormationDetails.vue';
import Profil from '../components/Profil.vue'; 
import Chatbot from '../components/Chatbot.vue';

const routes = [
  { path: '/', component: Home }, 
  { path: '/formation/:id', component: FormationDetails },
  { path: '/profil', component: Profil },
  { path: '/chatbot', component: Chatbot }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;