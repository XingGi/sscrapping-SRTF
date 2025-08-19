<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card class="mb-6 elevation-2">
          <v-card-title>Control Panel</v-card-title>
          <v-card-text class="d-flex flex-column flex-md-row ga-4">
            <v-text-field
              v-model="scrapeKeyword"
              label="Masukkan Keyword YouTube"
              variant="outlined"
              density="compact"
              hide-details
              placeholder="contoh: belajar django"
              @keyup.enter="startScrape"
            ></v-text-field>
            <v-btn
              @click="startScrape"
              :loading="isScraping"
              :disabled="!scrapeKeyword || isScraping"
              color="primary"
              size="large"
              prepend-icon="mdi-magnify-scan"
            >
              Mulai Scrape
            </v-btn>
            <v-btn
              @click="startCommentUpdate"
              :loading="isUpdatingComments"
              color="teal"
              size="large"
              prepend-icon="mdi-comment-sync"
            >
              Update Komentar
            </v-btn>
          </v-card-text>
        </v-card>
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
                  >{{ item.title }}</a
                >
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
        </v-card>
      </v-col>
    </v-row>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="4000">
      {{ snackbar.text }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const scrapeKeyword = ref('')
const isScraping = ref(false)
const snackbar = ref({ show: false, text: '', color: 'success' })
const search = ref('')
const videos = ref([])
const isLoading = ref(true)

const headers = [
  { title: 'Video Title', key: 'title', width: '40%' },
  { title: 'Channel Name', key: 'channel_name', width: '30%' },
  { title: 'Scraped At', key: 'created_at', width: '20%' },
  { title: 'Link', key: 'video_url', sortable: false, align: 'center', width: '10%' },
]

const startScrape = async () => {
  if (!scrapeKeyword.value) return
  isScraping.value = true
  snackbar.value = { show: false, text: '' }
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/scrape/youtube/', {
      keyword: scrapeKeyword.value,
    })
    snackbar.value = { show: true, text: response.data.message, color: 'success' }
    scrapeKeyword.value = ''

    // --- FITUR AUTO-REFRESH ---
    // Tunggu beberapa detik untuk memberi waktu scraper bekerja, lalu refresh data
    setTimeout(() => {
      snackbar.value = { show: true, text: 'Refreshing data...', color: 'info' }
      fetchVideos()
    }, 5000) // Tunggu 5 detik sebelum refresh
  } catch (error) {
    console.error('Error starting scrape job:', error)
    snackbar.value = { show: true, text: 'Failed to start scraping job.', color: 'error' }
  } finally {
    isScraping.value = false
  }
}

const fetchVideos = async () => {
  isLoading.value = true
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/videos/')

    // --- PERBAIKAN BUG API ---
    // Logika ini sekarang menangani kedua jenis respons (array langsung atau objek)
    if (Array.isArray(response.data)) {
      videos.value = response.data
    } else if (response.data && Array.isArray(response.data.results)) {
      videos.value = response.data.results
    } else {
      videos.value = [] // Fallback jika format tidak dikenali
    }
  } catch (error) {
    console.error('CRITICAL ERROR fetching video data:', error)
    videos.value = []
  } finally {
    isLoading.value = false
  }
}

const formatDateTime = (isoString) => {
  if (!isoString) return 'N/A'
  const date = new Date(isoString)
  return date.toLocaleString('id-ID', { dateStyle: 'long', timeStyle: 'short' })
}

const filteredVideos = computed(() => {
  if (!search.value) return videos.value
  return videos.value.filter(
    (video) =>
      video.title.toLowerCase().includes(search.value.toLowerCase()) ||
      video.channel_name.toLowerCase().includes(search.value.toLowerCase()),
  )
})

const isUpdatingComments = ref(false)

const startCommentUpdate = async () => {
  isUpdatingComments.value = true
  snackbar.value = { show: false, text: '' }
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/scrape/comments/')
    snackbar.value = { show: true, text: response.data.message, color: 'success' }

    // Refresh halaman 'Sumber Data' setelah beberapa saat
    setTimeout(() => {
      // Di sini kita bisa menambahkan logika untuk auto-refresh halaman komentar jika diperlukan
      snackbar.value = {
        show: true,
        text: 'Cek halaman Sumber Data untuk hasilnya.',
        color: 'info',
      }
    }, 5000)
  } catch (error) {
    console.error('Error starting comment update job:', error)
    snackbar.value = { show: true, text: 'Gagal memulai update komentar.', color: 'error' }
  } finally {
    isUpdatingComments.value = false
  }
}

onMounted(fetchVideos)
</script>

<style scoped>
.desktop-only {
  display: block;
}
.mobile-only {
  display: none;
}
@media (max-width: 960px) {
  .desktop-only {
    display: none;
  }
  .mobile-only {
    display: block;
  }
}
</style>
