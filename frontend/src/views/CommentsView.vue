<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold mb-1">Sumber Data</h1>
        <p class="text-medium-emphasis">Kumpulan semua komentar dari berbagai platform.</p>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-card class="elevation-2">
          <v-card-title class="d-flex flex-column flex-md-row align-center pa-4">
            <span class="text-h6">Semua Komentar</span>
            <v-spacer></v-spacer>
            <v-text-field
              v-model="search"
              density="compact"
              label="Cari komentar atau username..."
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              flat
              hide-details
              single-line
              style="max-width: 400px"
            ></v-text-field>
          </v-card-title>

          <v-divider></v-divider>

          <v-data-table
            :headers="headers"
            :items="comments"
            :loading="isLoading"
            :search="search"
            item-value="id"
            density="comfortable"
            hover
          >
            <template v-slot:loading>
              <v-skeleton-loader type="table-row@10"></v-skeleton-loader>
            </template>

            <template v-slot:[`item.text`]="{ item }">
              <div class="text-truncate" style="max-width: 350px" :title="item.text">
                {{ item.text }}
              </div>
            </template>

            <template v-slot:[`item.platform`]="{ item }">
              <v-chip :color="getPlatformColor(item.platform)" size="small">
                {{ item.platform }}
              </v-chip>
            </template>

            <template v-slot:[`item.scraped_at`]="{ item }">
              <span>{{ formatDateTime(item.scraped_at) }}</span>
            </template>

            <template v-slot:[`item.comment_url`]="{ item }">
              <a
                :href="item.comment_url"
                target="_blank"
                class="text-decoration-none"
                v-if="item.comment_url"
              >
                <v-icon size="small">mdi-open-in-new</v-icon>
              </a>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const search = ref('')
const comments = ref([])
const isLoading = ref(true)

const headers = [
  { title: 'Username', key: 'username', width: '15%' },
  { title: 'Isi Komentar', key: 'text', width: '45%' },
  { title: 'Tanggal Scrape', key: 'scraped_at', width: '20%' },
  { title: 'Platform', key: 'platform', align: 'center', width: '10%' },
  { title: 'Link', key: 'comment_url', sortable: false, align: 'center', width: '10%' },
]

const getPlatformColor = (platform) => {
  if (platform === 'YT') return 'red'
  if (platform === 'IG') return 'pink'
  if (platform === 'TT') return 'blue-grey'
  return 'grey'
}

const formatDateTime = (isoString) => {
  if (!isoString) return 'N/A'
  const date = new Date(isoString)
  return date.toLocaleString('id-ID', { dateStyle: 'long', timeStyle: 'short' })
}

onMounted(async () => {
  isLoading.value = true
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/comments/')
    comments.value = response.data
  } catch (error) {
    console.error('CRITICAL ERROR fetching comment data:', error)
    comments.value = []
  } finally {
    isLoading.value = false
  }
})
</script>
