<script lang="ts">
	import { Header } from '$lib/components';
	import { lowStockItems, uncheckedCount } from '$lib/stores';
	import { rfidApi } from '$lib/api';
	import type { PutItBackAlert as PutItBackAlertType } from '$lib/types';
	import { onMount } from 'svelte';

	let itemsOut: PutItBackAlertType[] = [];

	onMount(async function() {
		loadItemsOut();
		var interval = setInterval(loadItemsOut, 30000);
		return function() { clearInterval(interval); };
	});

	async function loadItemsOut() {
		try {
			itemsOut = await rfidApi.getItemsOut();
		} catch (e) {
			console.error('Failed to load items out:', e);
		}
	}
</script>

<Header title="PantryPal" />

<!-- Alert Banner -->
{#if $lowStockItems.length > 0 || itemsOut.length > 0}
	<div class="flex gap-2 px-4 py-2 bg-gray-100 border-b border-gray-200">
		{#if $lowStockItems.length > 0}
			<a href="/inventory?filter=low" class="flex items-center gap-2 py-2 px-4 rounded-xl bg-amber-100 border border-amber-300 active:scale-95 transition-transform">
				<span class="text-xl">&#9888;</span>
				<span class="font-bold text-amber-800">{$lowStockItems.length} Low Stock</span>
			</a>
		{/if}
		{#if itemsOut.length > 0}
			<button class="flex items-center gap-2 py-2 px-4 rounded-xl bg-blue-100 border border-blue-300 active:scale-95 transition-transform" on:click={() => {}}>
				<span class="text-xl">&#128205;</span>
				<span class="font-bold text-blue-800">{itemsOut.length} Put Back</span>
			</button>
		{/if}
	</div>
{/if}

<main class="flex-1 p-4 flex flex-col overflow-hidden">
	<!-- 6 Tile Grid: 2 columns x 3 rows -->
	<div class="grid grid-cols-2 gap-4 flex-1">
		<!-- Left Column -->
		<!-- Add Stock - GREEN -->
		<a href="/add" class="flex flex-col items-center justify-center gap-3 rounded-3xl bg-gradient-to-br from-green-500 to-emerald-600 text-white shadow-lg active:scale-[0.97] transition-transform">
			<svg class="w-14 h-14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
			</svg>
			<span class="text-3xl font-bold">Add</span>
		</a>

		<!-- Right Column -->
		<!-- Recipes - PURPLE -->
		<a href="/recipes" class="flex flex-col items-center justify-center gap-3 rounded-3xl bg-gradient-to-br from-purple-500 to-violet-600 text-white shadow-lg active:scale-[0.97] transition-transform">
			<span class="text-5xl">&#128214;</span>
			<span class="text-3xl font-bold">Recipes</span>
		</a>

		<!-- Use Item - RED -->
		<a href="/use" class="flex flex-col items-center justify-center gap-3 rounded-3xl bg-gradient-to-br from-red-500 to-rose-600 text-white shadow-lg active:scale-[0.97] transition-transform">
			<svg class="w-14 h-14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M20 12H4" />
			</svg>
			<span class="text-3xl font-bold">Use</span>
		</a>

		<!-- Shopping - ORANGE -->
		<a href="/shopping" class="flex flex-col items-center justify-center gap-3 rounded-3xl bg-gradient-to-br from-orange-500 to-amber-600 text-white shadow-lg active:scale-[0.97] transition-transform relative">
			<span class="text-5xl">&#128722;</span>
			<span class="text-3xl font-bold">Shopping</span>
			{#if $uncheckedCount > 0}
				<span class="absolute top-4 right-4 bg-white text-orange-600 text-lg font-bold rounded-full min-w-[32px] h-8 px-2 flex items-center justify-center shadow">{$uncheckedCount}</span>
			{/if}
		</a>

		<!-- Inventory - BLUE -->
		<a href="/inventory" class="flex flex-col items-center justify-center gap-3 rounded-3xl bg-gradient-to-br from-blue-500 to-indigo-600 text-white shadow-lg active:scale-[0.97] transition-transform">
			<svg class="w-14 h-14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
			</svg>
			<span class="text-3xl font-bold">Inventory</span>
		</a>

		<!-- Settings - GRAY -->
		<a href="/settings" class="flex flex-col items-center justify-center gap-3 rounded-3xl bg-gradient-to-br from-gray-500 to-gray-600 text-white shadow-lg active:scale-[0.97] transition-transform">
			<span class="text-5xl">&#9881;</span>
			<span class="text-3xl font-bold">Settings</span>
		</a>
	</div>
</main>
