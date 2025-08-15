<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold mb-1">YouTube Scraper</h1>
        <p class="text-medium-emphasis">A collection of scraped videos from YouTube.</p>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-card class="elevation-2">
          <v-card-title class="d-flex flex-column flex-md-row align-center pa-4">
            <span class="text-h6">Scraped Videos</span>
            <v-spacer></v-spacer>
            <v-text-field
              v-model="search"
              density="compact"
              label="Search Videos"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              flat
              hide-details
              single-line
              style="max-width: 320px"
            ></v-text-field>
          </v-card-title>

          <v-divider></v-divider>

          <div class="desktop-only">
            <v-data-table
              :headers="headers"
              :items="videos"
              :loading="isLoading"
              :search="search"
              item-value="id"
              density="comfortable"
              hover
            >
              <template v-slot:loading>
                <v-skeleton-loader type="table-row@10"></v-skeleton-loader>
              </template>

              <template v-slot:[`item.title`]="{ item }">
                <a
                  :href="item.video_url"
                  target="_blank"
                  class="text-decoration-none font-weight-medium"
                >
                  {{ item.title }}
                </a>
              </template>

              <template v-slot:[`item.created_at`]="{ item }">
                <span>{{ formatDateTime(item.created_at) }}</span>
              </template>

              <template v-slot:[`item.video_url`]="{ item }">
                <a :href="item.video_url" target="_blank" class="text-decoration-none">
                  <v-icon size="small">mdi-open-in-new</v-icon>
                </a>
              </template>
            </v-data-table>
          </div>

          <div class="mobile-only">
            <v-list lines="three" class="pa-0">
              <div v-for="(item, index) in filteredVideos" :key="item.id || `video-${index}`">
                <v-list-item :href="item.video_url" target="_blank" class="py-3">
                  <v-list-item-title class="font-weight-bold mb-1" style="white-space: normal">{{
                    item.title
                  }}</v-list-item-title>
                  <v-list-item-subtitle>{{ item.channel_name }}</v-list-item-subtitle>
                  <v-list-item-subtitle class="text-caption mt-2">{{
                    formatDateTime(item.created_at)
                  }}</v-list-item-subtitle>
                </v-list-item>
                <v-divider v-if="index < filteredVideos.length - 1"></v-divider>
              </div>
            </v-list>
          </div>

          <template v-if="isLoading && videos.length === 0">
            <v-skeleton-loader type="list-item-two-line@10"></v-skeleton-loader>
          </template>
          <div v-if="!isLoading && videos.length === 0" class="pa-4 text-center">
            <v-alert type="warning">No video data found. Please run the scraper.</v-alert>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
// import { useVuetify } from 'vuetify' // <-- DIHAPUS, TIDAK DIPERLUKAN LAGI

// State Management
const search = ref('')
const videos = ref([])
const isLoading = ref(true)
// const vuetify = useVuetify() // <-- DIHAPUS, TIDAK DIPERLUKAN LAGI

// Konfigurasi Tabel untuk Desktop
const headers = [
  { title: 'Video Title', key: 'title', width: '40%' },
  { title: 'Channel Name', key: 'channel_name', width: '30%' },
  { title: 'Scraped At', key: 'created_at', width: '20%' },
  { title: 'Link', key: 'video_url', sortable: false, align: 'center', width: '10%' },
]

// Computed property untuk filter di mobile
const filteredVideos = computed(() => {
  if (!search.value) {
    return videos.value
  }
  return videos.value.filter(
    (video) =>
      video.title.toLowerCase().includes(search.value.toLowerCase()) ||
      video.channel_name.toLowerCase().includes(search.value.toLowerCase()),
  )
})

// Fungsi untuk memformat tanggal
const formatDateTime = (isoString) => {
  if (!isoString) return 'N/A'
  const date = new Date(isoString)
  return date.toLocaleString('id-ID', { dateStyle: 'long', timeStyle: 'short' })
}

// Logika Pengambilan Data
onMounted(async () => {
  isLoading.value = true
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/videos/')
    if (Array.isArray(response.data)) {
      videos.value = response.data
    } else if (response.data && Array.isArray(response.data.results)) {
      videos.value = response.data.results
    }
  } catch (error) {
    console.error('CRITICAL ERROR fetching video data:', error)
    videos.value = []
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.desktop-only {
  display: block;
}
.mobile-only {
  display: none;
}

/* Aturan untuk layar kecil (mobile) */
@media (max-width: 960px) {
  .desktop-only {
    display: none;
  }
  .mobile-only {
    display: block;
  }
}
</style>
