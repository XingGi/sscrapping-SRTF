<template>
  <v-app>
    <v-navigation-drawer v-model="drawer">
      <v-list dense>
        <v-list-item link to="/" prepend-icon="mdi-home">
          <v-list-item-title>Home</v-list-item-title>
        </v-list-item>
        <v-list-item link to="/youtube" prepend-icon="mdi-youtube">
          <v-list-item-title>YouTube Scraper</v-list-item-title>
        </v-list-item>
        <v-list-item link to="/comments" prepend-icon="mdi-database-search">
          <v-list-item-title>Sumber Data</v-list-item-title>
        </v-list-item>
        <v-list-item link to="/about" prepend-icon="mdi-information">
          <v-list-item-title>About</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-app-bar color="primary" density="compact">
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title class="font-weight-medium">Sscrapping Dashboard</v-toolbar-title>
    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup>
import { ref } from 'vue'
const drawer = ref(true) // Secara default, menu samping akan terbuka
</script>

<style>
/* CSS Global untuk memastikan layout dasar yang bersih */
html,
body,
#app {
  height: 100%;
  margin: 0;
  padding: 0;
  overflow-x: hidden; /* Mencegah scroll horizontal yang tidak perlu */
}
</style>
