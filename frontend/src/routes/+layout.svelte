<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { shopping, freezers, inventory, products } from '$lib/stores';

	// Load initial data
	onMount(async () => {
		try {
			await Promise.all([
				shopping.load(),
				freezers.load(),
				inventory.load(),
				products.load()
			]);
		} catch (e) {
			console.error('Failed to load initial data:', e);
		}
	});
</script>

<div class="min-h-screen flex flex-col">
	<slot />
</div>
