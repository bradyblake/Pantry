<script lang="ts">
	import { goto } from '$app/navigation';
	import { Header, SearchBar, Modal, QuantityPicker } from '$lib/components';
	import { inventory, products, categories } from '$lib/stores';
	import { systemApi } from '$lib/api';
	import type { Product } from '$lib/types';
	import { onMount } from 'svelte';

	let mode: 'select' | 'search' | 'create' = 'select';
	let searchQuery = '';
	let selectedProduct: Product | null = null;
	let showModal = false;

	// Add form
	let addQuantity = 1;
	let addLocation = 'pantry';

	// Create product form
	let newProductName = '';
	let newProductCategory = '';
	let newProductUnit = 'unit';
	let defaultCategories: string[] = [];

	onMount(async () => {
		defaultCategories = await systemApi.getDefaultCategories();
		await categories.load();
	});

	$: filteredProducts = searchQuery
		? $products.filter(p => p.name.toLowerCase().includes(searchQuery.toLowerCase()))
		: $products;

	$: allCategories = [...new Set([...defaultCategories, ...$categories])];

	function handleProductSelect(product: Product) {
		selectedProduct = product;
		addQuantity = product.default_quantity;
		addLocation = 'pantry';
		showModal = true;
	}

	async function handleAdd() {
		if (selectedProduct && addQuantity > 0) {
			try {
				await inventory.add({
					product_id: selectedProduct.id,
					quantity: addQuantity,
					location: addLocation
				});
				showModal = false;
				selectedProduct = null;
				searchQuery = '';
				mode = 'select';
			} catch (e) {
				console.error('Failed to add:', e);
			}
		}
	}

	async function handleCreateProduct() {
		if (newProductName.trim()) {
			try {
				const product = await products.add({
					name: newProductName.trim(),
					category: newProductCategory || null,
					default_unit: newProductUnit
				});
				// Now add to inventory
				selectedProduct = product;
				addQuantity = 1;
				addLocation = 'pantry';
				showModal = true;
				mode = 'search';
				newProductName = '';
				newProductCategory = '';
			} catch (e) {
				console.error('Failed to create product:', e);
			}
		}
	}
</script>

<Header title="Add Stock" showBack backHref="/" />

<main class="flex-1 p-4 flex flex-col overflow-hidden">
	{#if mode === 'select'}
		<!-- Main selection screen - go straight to search -->
		<button
			class="flex-1 flex items-center justify-center gap-6 rounded-3xl bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-xl active:scale-[0.98] transition-transform"
			on:click={() => mode = 'search'}
		>
			<svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
			</svg>
			<div class="text-left">
				<span class="text-4xl font-bold block">Manual Entry</span>
				<span class="text-xl text-green-100">Search and add items</span>
			</div>
		</button>

	{:else if mode === 'search'}
		<!-- Search/select product -->
		<div class="mb-4">
			<SearchBar
				bind:value={searchQuery}
				placeholder="Search products..."
				autofocus
			/>
		</div>

		<h3 class="text-lg font-bold text-gray-700 mb-3">Select product to add</h3>

		<div class="flex-1 overflow-y-auto">
			<div class="grid grid-cols-2 gap-3">
				{#each filteredProducts as product}
					<button
						type="button"
						class="p-4 rounded-2xl text-left bg-white border-2 border-gray-100 shadow-sm active:scale-95 transition-transform"
						on:click={() => handleProductSelect(product)}
					>
						<p class="text-xl font-bold text-gray-800 truncate">{product.name}</p>
						{#if product.category}
							<p class="text-sm text-gray-400 mt-1">{product.category}</p>
						{/if}
					</button>
				{:else}
					<div class="col-span-full text-center py-12">
						{#if searchQuery}
							<p class="text-xl text-gray-500 mb-4">No products match "{searchQuery}"</p>
							<button class="px-8 py-4 rounded-2xl bg-green-500 text-white text-xl font-bold shadow-lg" on:click={() => { mode = 'create'; newProductName = searchQuery; }}>
								Create "{searchQuery}"
							</button>
						{:else}
							<p class="text-xl text-gray-400">Start typing to search</p>
						{/if}
					</div>
				{/each}
			</div>
		</div>

		<div class="flex gap-3 pt-4 shrink-0">
			<button class="flex-1 py-4 rounded-2xl bg-gray-200 text-gray-700 text-xl font-bold active:scale-95 transition-transform" on:click={() => mode = 'select'}>
				Back
			</button>
			<button class="flex-1 py-4 rounded-2xl bg-blue-500 text-white text-xl font-bold active:scale-95 transition-transform" on:click={() => mode = 'create'}>
				+ New Product
			</button>
		</div>

	{:else if mode === 'create'}
		<!-- Create new product form -->
		<h2 class="text-2xl font-bold text-gray-800 mb-6">Create New Product</h2>

		<div class="flex-1 space-y-5 overflow-y-auto">
			<div>
				<label class="block text-lg font-semibold text-gray-700 mb-2">Product Name *</label>
				<input
					type="text"
					bind:value={newProductName}
					class="w-full px-4 py-4 text-xl border-2 border-gray-200 rounded-xl focus:border-green-500 focus:outline-none"
					placeholder="e.g., Cheerios"
				/>
			</div>

			<div>
				<label class="block text-lg font-semibold text-gray-700 mb-2">Category</label>
				<select bind:value={newProductCategory} class="w-full px-4 py-4 text-xl border-2 border-gray-200 rounded-xl focus:border-green-500 focus:outline-none">
					<option value="">Select category...</option>
					{#each allCategories as cat}
						<option value={cat}>{cat}</option>
					{/each}
				</select>
			</div>

			<div>
				<label class="block text-lg font-semibold text-gray-700 mb-2">Unit</label>
				<select bind:value={newProductUnit} class="w-full px-4 py-4 text-xl border-2 border-gray-200 rounded-xl focus:border-green-500 focus:outline-none">
					<option value="unit">unit</option>
					<option value="box">box</option>
					<option value="bag">bag</option>
					<option value="can">can</option>
					<option value="bottle">bottle</option>
					<option value="jar">jar</option>
					<option value="packet">packet</option>
					<option value="lb">lb</option>
					<option value="oz">oz</option>
					<option value="g">g</option>
					<option value="ml">ml</option>
					<option value="L">L</option>
				</select>
			</div>
		</div>

		<div class="flex gap-3 pt-4 shrink-0">
			<button class="flex-1 py-5 rounded-2xl bg-gray-200 text-gray-700 text-xl font-bold active:scale-95 transition-transform" on:click={() => mode = 'search'}>
				Cancel
			</button>
			<button
				class="flex-1 py-5 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-600 text-white text-xl font-bold shadow-lg active:scale-95 transition-transform disabled:opacity-50"
				on:click={handleCreateProduct}
				disabled={!newProductName.trim()}
			>
				Create & Add
			</button>
		</div>
	{/if}
</main>

<!-- Add quantity modal -->
<Modal bind:open={showModal} title={`Add ${selectedProduct?.name || ''}`} on:close={() => showModal = false}>
	{#if selectedProduct}
		<div class="space-y-5">
			<div>
				<label class="block text-lg font-semibold text-gray-700 mb-4">Quantity</label>
				<QuantityPicker
					bind:value={addQuantity}
					min={1}
					max={99}
					unit={selectedProduct.default_unit}
				/>
			</div>

			<div>
				<label class="block text-lg font-semibold text-gray-700 mb-4">Location</label>
				<div class="grid grid-cols-3 gap-3">
					{#each [
						{ id: 'pantry', icon: '&#127968;', label: 'Pantry', color: 'amber' },
						{ id: 'fridge', icon: '&#129482;', label: 'Fridge', color: 'cyan' },
						{ id: 'freezer', icon: '&#10052;', label: 'Freezer', color: 'indigo' }
					] as loc}
						<button
							type="button"
							class="py-5 px-3 rounded-2xl border-2 transition-all text-center active:scale-95
								{addLocation === loc.id
									? `border-${loc.color}-500 bg-${loc.color}-50 shadow-lg`
									: 'border-gray-200 bg-white'}"
							on:click={() => addLocation = loc.id}
						>
							<span class="text-3xl block mb-2">{@html loc.icon}</span>
							<span class="text-lg font-bold">{loc.label}</span>
						</button>
					{/each}
				</div>
			</div>

			<button class="w-full py-5 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-600 text-white text-xl font-bold shadow-lg active:scale-95 transition-transform" on:click={handleAdd}>
				Add {addQuantity} to {addLocation}
			</button>
		</div>
	{/if}
</Modal>
