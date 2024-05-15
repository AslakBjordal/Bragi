import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		proxy: {
			'/api': {
				target: 'http://localhost:8000',
				rewrite: (path) => path.replace(/^\/api/, ''),
			},
			'/ws': {
				target: 'ws://localhost:8000/ws',
				ws: true,
				rewrite: (path) => path.replace(/^\/ws/, ''),
			}
		},
	},
});
