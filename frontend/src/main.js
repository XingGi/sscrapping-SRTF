// src/main.js

// Assets
import './assets/main.css'

// Vue Core
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Plugins
import vuetify from './plugins/vuetify'

const app = createApp(App)

app.use(router)
app.use(vuetify)

app.mount('#app')
