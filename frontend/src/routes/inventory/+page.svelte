<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { Header, SearchBar, InventoryItem as InventoryItemComponent, Modal, QuantityPicker } from '$lib/components';
	import { inventory, inventoryByCategory, lowStockItems } from '$lib/stores';
	import type { InventoryItem } from '$lib/types';

	let searchQuery = '';
	let selectedLocation: string | null = null;
	let showLowStock = false;

	let selectedItem: InventoryItem | null = null;
	let showModal = false;
	let useQuantity = 1;

	// Check URL params for initial filter
	onMount(() => {
		const filter = $page.url.searchParams.get('filter');
		if (filter === 'low') {
			showLowStock = true;
		}
	});

	$: filteredCategories = (() => {
		let items = showLowStock ? $lowStockItems : Object.values($inventoryByCategory).flat();

		if (selectedLocation) {
			items = items.filter(i => i.location === selectedLocation);
		}

		if (searchQuery) {
			const query = searchQuery.toLowerCase();
			items = items.filter(i =>
				i.product.name.toLowerCase().includes(query) ||
				i.product.category?.toLowerCase().includes(query)
			);
		}

		// Re-group by category
		const grouped: Record<string, InventoryItem[]> = {};
		for (const item of items) {
			const category = item.product.category || 'Other';
			if (!grouped[category]) grouped[category] = [];
			grouped[category].push(item);
		}
		return grouped;
	})();

	function handleItemClick(item: InventoryItem) {
		selectedItem = item;
		useQuantity = 1;
		showModal = true;
	}

	async function handleUse() {
		if (selectedItem && useQuantity > 0) {
			try {
				await inventory.use({
					product_id: selectedItem.product_id,
					quantity: useQuantity
				});
				showModal = false;
				selectedItem = null;
			} catch (e) {
				console.error('Failed to use item:', e);
			}
		}
	}

	async function handleRemove() {
		if (selectedItem) {
			try {
				await inventory.remove(selectedItem.id);
				showModal = false;
				selectedItem = null;
			} catch (e) {
				console.error('Failed to remove item:', e);
			}
		}
	}
</script>

<Header title="Inventory" showBack backHref="/" />

<main class="flex-1 flex flex-col overflow-hidden">
	<!-- Search -->
	<div class="p-4 pb-3">
		<SearchBar
			bind:value={searchQuery}
			placeholder="Search inventory..."
		/>
	</div>

	<!-- Filters - larger touch targets -->
	<div class="px-4 pb-3 flex gap-2 overflow-x-auto">
		<button
			class="px-5 py-3 rounded-xl text-lg font-semibold whitespace-nowrap transition-all {!selectedLocation && !showLowStock ? 'bg-blue-500 text-white shadow-lg' : 'bg-white text-gray-600 border border-gray-200'}"
			on:click={() => { selectedLocation = null; showLowStock = false; }}
		>
			All
		</button>
		<button
			class="px-5 py-3 rounded-xl text-lg font-semibold whitespace-nowrap transition-all {selectedLocation === 'pantry' ? 'bg-amber-500 text-white shadow-lg' : 'bg-white text-gray-600 border border-gray-200'}"
			on:click={() => { selectedLocation = 'pantry'; showLowStock = false; }}
		>
			&#127968; Pantry
		</button>
		<button
			class="px-5 py-3 rounded-xl text-lg font-semibold whitespace-nowrap transition-all {selectedLocation === 'fridge' ? 'bg-cyan-500 text-white shadow-lg' : 'bg-white text-gray-600 border border-gray-200'}"
			on:click={() => { selectedLocation = 'fridge'; showLowStock = false; }}
		>
			&#129482; Fridge
		</button>
		<button
			class="px-5 py-3 rounded-xl text-lg font-semibold whitespace-nowrap transition-all {selectedLocation === 'freezer' ? 'bg-indigo-500 text-white shadow-lg' : 'bg-white text-gray-600 border border-gray-200'}"
			on:click={() => { selectedLocation = 'freezer'; showLowStock = false; }}
		>
			&#10052; Freezer
		</button>
		<button
			class="px-5 py-3 rounded-xl text-lg font-semibold whitespace-nowrap transition-all {showLowStock ? 'bg-red-500 text-white shadow-lg' : 'bg-white text-gray-600 border border-gray-200'}"
			on:click={() => { showLowStock = true; selectedLocation = null; }}
		>
			&#9888; Low
		</button>
	</div>

	<!-- Inventory list - larger items -->
	<div class="flex-1 p-4 pt-2 overflow-y-auto">
		{#each Object.entries(filteredCategories) as [category, items], i}
			<div class="mb-5">
				<h3 class="text-lg font-bold text-gray-700 mb-3">{category}</h3>
				<div class="grid grid-cols-2 gap-3">
					{#each items as item}
						{@const stockLevel = item.quantity <= 0 ? 'out' : item.quantity <= 1 ? 'low' : 'high'}
						<button
							on:click={() => handleItemClick(item)}
							class="p-4 rounded-2xl text-left transition-all active:scale-95
								{stockLevel === 'out' ? 'bg-red-50 border-2 border-red-200' :
								 stockLevel === 'low' ? 'bg-amber-50 border-2 border-amber-200' :
								 'bg-white border-2 border-gray-100 shadow-sm'}"
						>
							<p class="text-xl font-bold text-gray-800 truncate">{item.product.name}</p>
							<div class="flex items-center justify-between mt-2">
								<span class="text-2xl font-bold {stockLevel === 'out' ? 'text-red-500' : stockLevel === 'low' ? 'text-amber-500' : 'text-green-600'}">
									{item.quantity}
								</span>
								<span class="text-gray-500">{item.product.default_unit}{item.quantity !== 1 ? 's' : ''}</span>
							</div>
							{#if item.location}
								<p class="text-sm text-gray-400 mt-1 capitalize">{item.location}</p>
							{/if}
						</button>
					{/each}
				</div>
			</div>
		{:else}
			<div class="text-center py-16">
				<div class="w-24 h-24 mx-auto mb-4 rounded-2xl bg-gray-100 flex items-center justify-center">
					<svg class="w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
					</svg>
				</div>
				{#if searchQuery}
					<p class="text-xl text-gray-500 font-medium">No items match "{searchQuery}"</p>
					<p class="text-gray-400 mt-1">Try a different search term</p>
				{:else}
					<p class="text-xl text-gray-500 font-medium">No items in inventory</p>
					<p class="text-gray-400 mt-1">Add items to get started</p>
					<a href="/add" class="inline-flex mt-6 px-8 py-4 rounded-2xl bg-green-500 text-white text-xl font-bold shadow-lg">Add Items</a>
				{/if}
			</div>
		{/each}
	</div>
</main>

<!-- Item detail modal -->
<Modal bind:open={showModal} title={selectedItem?.product.name || ''} on:close={() => showModal = false}>
	{#if selectedItem}
		<div class="space-y-5">
			<div class="flex justify-between items-center py-3 px-4 bg-gray-50 rounded-xl">
				<span class="text-lg text-gray-600">Current stock:</span>
				<span class="text-2xl font-bold text-gray-800">{selectedItem.quantity} {selectedItem.product.default_unit}</span>
			</div>

			{#if selectedItem.location}
				<div class="flex justify-between items-center py-3 px-4 bg-gray-50 rounded-xl">
					<span class="text-lg text-gray-600">Location:</span>
					<span class="text-xl font-semibold capitalize">{selectedItem.location}</span>
				</div>
			{/if}

			<div class="py-4">
				<label class="block text-lg font-semibold text-gray-700 mb-4">Use quantity:</label>
				<QuantityPicker
					bind:value={useQuantity}
					min={0}
					max={selectedItem.quantity}
					unit={selectedItem.product.default_unit}
				/>
			</div>

			<div class="flex gap-3 pt-2">
				<button class="flex-1 py-5 rounded-2xl bg-gradient-to-r from-red-500 to-rose-600 text-white text-xl font-bold shadow-lg active:scale-95 transition-transform" on:click={handleUse}>
					Use {useQuantity}
				</button>
				<button class="py-5 px-6 rounded-2xl bg-gray-200 text-gray-700 text-xl font-bold active:scale-95 transition-transform" on:click={handleRemove}>
					Remove All
				</button>
			</div>
		</div>
	{/if}
</Modal>
