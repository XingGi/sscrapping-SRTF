<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-btn to="/youtube" color="grey" prepend-icon="mdi-arrow-left" variant="text" class="mb-4">
          Kembali ke Daftar Video
        </v-btn>

        <div v-if="isLoadingVideo">
          <v-skeleton-loader type="article"></v-skeleton-loader>
        </div>

        <div v-if="video">
          <h1 class="text-h4 font-weight-bold mb-1">{{ video.title }}</h1>
          <p class="text-h6 text-medium-emphasis">{{ video.channel_name }}</p>
        </div>

        <v-alert v-if="error" type="error" class="mt-4">
          Gagal memuat detail video. Silakan coba lagi.
        </v-alert>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-card class="mt-4 elevation-2">
          <v-card-title class="d-flex align-center pa-4">
            <span class="text-h6">Komentar</span>
            <v-spacer></v-spacer>
            <v-text-field
              v-model="search"
              density="compact"
              label="Cari komentar..."
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              flat
              hide-details
              single-line
              style="max-width: 320px"
            ></v-text-field>
          </v-card-title>

          <v-divider></v-divider>

          <v-data-table
            :headers="commentHeaders"
            :items="comments"
            :loading="isLoadingComments"
            :search="search"
            item-value="id"
            density="comfortable"
            hover
          >
            <template v-slot:loading>
              <v-skeleton-loader type="table-row@5"></v-skeleton-loader>
            </template>

            <template v-slot:[`item.text`]="{ item }">
              <div style="max-width: 600px; white-space: normal">{{ item.text }}</div>
            </template>

            <template v-slot:[`item.scraped_at`]="{ item }">
              <span>{{ formatDateTime(item.scraped_at) }}</span>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

// State Management
const video = ref(null)
const comments = ref([])
const search = ref('')
const isLoadingVideo = ref(true)
const isLoadingComments = ref(true)
const error = ref(null)

// Mengambil parameter ID dari URL
const route = useRoute()
const videoId = route.params.id

// Konfigurasi Tabel Komentar
const commentHeaders = [
  { title: 'Username', key: 'username', width: '25%' },
  { title: 'Isi Komentar', key: 'text', width: '55%' },
  { title: 'Tanggal Scrape', key: 'scraped_at', width: '20%' },
]

// Fungsi format tanggal
const formatDateTime = (isoString) => {
  if (!isoString) return 'N/A'
  const date = new Date(isoString)
  return date.toLocaleString('id-ID', { dateStyle: 'long', timeStyle: 'short' })
}

// Fungsi untuk mengambil data
const fetchVideoDetails = async () => {
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/videos/${videoId}/`)
    video.value = response.data
  } catch (err) {
    error.value = 'Failed to load video details.'
    console.error(err)
  } finally {
    isLoadingVideo.value = false
  }
}

const fetchVideoComments = async () => {
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/videos/${videoId}/comments/`)
    comments.value = response.data // Asumsi API mengembalikan array langsung
  } catch (err) {
    error.value = 'Failed to load comments.'
    console.error(err)
  } finally {
    isLoadingComments.value = false
  }
}

// Panggil kedua fungsi saat komponen dimuat
onMounted(() => {
  fetchVideoDetails()
  fetchVideoComments()
})
</script>
