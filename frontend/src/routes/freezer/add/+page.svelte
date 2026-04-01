<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { Header, SearchBar, QuantityPicker } from '$lib/components';
	import { freezers, products, inventory } from '$lib/stores';
	import type { Product } from '$lib/types';

	let step: 'select' | 'details' = 'select';
	let searchQuery = '';
	let selectedProduct: Product | null = null;

	// Form fields
	let selectedFreezerId: number | null = null;
	let quantity = 1;
	let containerDescription = '';

	onMount(async () => {
		const freezerList = await freezers.load();
		if (freezerList.length > 0) {
			selectedFreezerId = freezerList[0].id;
		}
		await products.load();
	});

	$: filteredProducts = searchQuery
		? $products.filter(p => p.name.toLowerCase().includes(searchQuery.toLowerCase()))
		: $products.slice(0, 12);

	function handleProductSelect(product: Product) {
		selectedProduct = product;
		quantity = product.default_quantity;
		step = 'details';
	}

	async function handleAdd() {
		if (selectedProduct && selectedFreezerId && quantity > 0) {
			try {
				await inventory.add({
					product_id: selectedProduct.id,
					quantity,
					location: 'freezer',
					freezer_id: selectedFreezerId,
					container_description: containerDescription || undefined
				});
				goto('/freezer');
			} catch (e) {
				console.error('Failed to add to freezer:', e);
			}
		}
	}
</script>

<Header title="Add to Freezer" showBack backHref="/freezer" />

<main class="flex-1 p-4">
	{#if step === 'select'}
		<!-- Product selection -->
		<div class="space-y-4">
			<SearchBar
				bind:value={searchQuery}
				placeholder="Search products..."
				autofocus
			/>

			<div class="grid grid-cols-2 gap-3">
				{#each filteredProducts as product}
					<button
						type="button"
						class="card text-left hover:shadow-md active:shadow-sm transition-shadow"
						on:click={() => handleProductSelect(product)}
					>
						<p class="font-semibold text-gray-900 truncate">{product.name}</p>
						{#if product.category}
							<p class="text-xs text-gray-500">{product.category}</p>
						{/if}
					</button>
				{:else}
					<p class="col-span-full text-center py-8 text-gray-500">
						{searchQuery ? `No products match "${searchQuery}"` : 'No products yet'}
					</p>
				{/each}
			</div>

			{#if searchQuery && filteredProducts.length === 0}
				<a href="/add" class="btn btn-outline w-full text-center">
					Create New Product
				</a>
			{/if}
		</div>

	{:else if step === 'details'}
		<!-- Freezer details -->
		<div class="space-y-6">
			<div class="card">
				<p class="text-lg font-semibold">{selectedProduct?.name}</p>
				<button
					type="button"
					class="text-sm text-primary-600 underline"
					on:click={() => { step = 'select'; selectedProduct = null; }}
				>
					Change
				</button>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Which freezer?</label>
				<div class="grid grid-cols-2 gap-2">
					{#each $freezers as freezer}
						<button
							type="button"
							class="py-3 px-4 rounded-xl border-2 transition-all text-left
								{selectedFreezerId === freezer.id
									? 'border-primary-500 bg-primary-50'
									: 'border-gray-200 hover:border-gray-300'}"
							on:click={() => selectedFreezerId = freezer.id}
						>
							<p class="font-medium">{freezer.name}</p>
							{#if freezer.location}
								<p class="text-xs text-gray-500">{freezer.location}</p>
							{/if}
						</button>
					{/each}
				</div>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Quantity</label>
				<QuantityPicker
					bind:value={quantity}
					min={1}
					max={99}
					unit={selectedProduct?.default_unit || 'unit'}
				/>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1">
					Where is it? <span class="font-normal text-gray-500">(optional)</span>
				</label>
				<input
					type="text"
					bind:value={containerDescription}
					class="input"
					placeholder='e.g., "Blue bag, bottom drawer"'
				/>
				<p class="text-xs text-gray-500 mt-1">Helps you find it later</p>
			</div>

			<button
				class="btn btn-primary w-full"
				on:click={handleAdd}
				disabled={!selectedFreezerId}
			>
				Add to Freezer
			</button>
		</div>
	{/if}
</main>
