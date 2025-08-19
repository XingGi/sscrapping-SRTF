import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import YoutubeView from '../views/youtube/VideoListView.vue'
import VideoDetailView from '../views/youtube/VideoDetailView.vue'
import CommentsView from '../views/CommentsView.vue'

const router = createRouter({
    history: createWebHistory(
        import.meta.env.BASE_URL),
    routes: [{
            path: '/',
            name: 'home',
            component: HomeView,
        },
        {
            path: '/about',
            name: 'about',
            // route level code-splitting
            // this generates a separate chunk (About.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: () =>
                import ('../views/AboutView.vue'),
        },
        {
            path: '/youtube',
            name: 'youtube',
            component: YoutubeView,
        },
        {
            path: '/comments',
            name: 'comments',
            component: CommentsView,
        },
        {
            path: '/videos/:id', // ':id' adalah parameter dinamis
            name: 'video-detail',
            component: VideoDetailView,
        },
    ],
})

export default router