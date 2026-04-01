import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	build: {
		target: 'es2015'  // iOS 10 Safari compatibility
	},
	server: {
		port: 5173,
		host: true
	}
});
