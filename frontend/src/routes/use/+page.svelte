<script lang="ts">
	import { Header, SearchBar, Modal, QuantityPicker } from '$lib/components';
	import { inventory, products } from '$lib/stores';
	import type { InventoryItem, Product } from '$lib/types';

	let searchQuery = '';
	let selectedProduct: Product | null = null;
	let showModal = false;
	let useQuantity = 1;
	let currentStock = 0;

	$: filteredProducts = searchQuery
		? $products.filter(p => p.name.toLowerCase().includes(searchQuery.toLowerCase()))
		: $products.slice(0, 12); // Show recent/common items

	$: inventoryForProduct = selectedProduct
		? $inventory.filter(i => i.product_id === selectedProduct?.id)
		: [];

	function handleProductClick(product: Product) {
		selectedProduct = product;
		const invItems = $inventory.filter(i => i.product_id === product.id);
		currentStock = invItems.reduce((sum, i) => sum + i.quantity, 0);
		useQuantity = Math.min(1, currentStock);
		showModal = true;
	}

	async function handleUse() {
		if (selectedProduct && useQuantity > 0) {
			try {
				await inventory.use({
					product_id: selectedProduct.id,
					quantity: useQuantity
				});
				showModal = false;
				selectedProduct = null;
				searchQuery = '';
			} catch (e) {
				console.error('Failed to use item:', e);
			}
		}
	}
</script>

<Header title="Use Item" showBack backHref="/" />

<main class="flex-1 flex flex-col overflow-hidden p-4">
	<!-- Search -->
	<div class="mb-4">
		<SearchBar
			bind:value={searchQuery}
			placeholder="Search products..."
			autofocus
		/>
	</div>

	<!-- Title -->
	<h3 class="text-lg font-bold text-gray-700 mb-3">
		{searchQuery ? 'Search Results' : 'Select item to use'}
	</h3>

	<!-- Product grid - larger cards -->
	<div class="flex-1 overflow-y-auto">
		<div class="grid grid-cols-2 gap-3">
			{#each filteredProducts as product}
				{@const invItems = $inventory.filter(i => i.product_id === product.id)}
				{@const totalQty = invItems.reduce((sum, i) => sum + i.quantity, 0)}
				<button
					type="button"
					on:click={() => handleProductClick(product)}
					class="p-4 rounded-2xl text-left transition-all active:scale-95
						{totalQty <= 0 ? 'bg-gray-100 border-2 border-gray-200 opacity-50' :
						 'bg-white border-2 border-gray-100 shadow-sm'}"
					disabled={totalQty <= 0}
				>
					<p class="text-xl font-bold text-gray-800 truncate">{product.name}</p>
					<div class="flex items-center justify-between mt-2">
						<span class="text-2xl font-bold {totalQty > 0 ? 'text-green-600' : 'text-red-400'}">
							{totalQty}
						</span>
						<span class="text-gray-500">in stock</span>
					</div>
				</button>
			{:else}
				<div class="col-span-full text-center py-16">
					<p class="text-xl text-gray-500">
						{searchQuery ? `No products match "${searchQuery}"` : 'No products yet'}
					</p>
				</div>
			{/each}
		</div>
	</div>
</main>

<!-- Use modal -->
<Modal bind:open={showModal} title={selectedProduct?.name || ''} on:close={() => showModal = false}>
	{#if selectedProduct}
		<div class="space-y-5">
			<div class="flex justify-between items-center py-3 px-4 bg-gray-50 rounded-xl">
				<span class="text-lg text-gray-600">Current stock:</span>
				<span class="text-2xl font-bold {currentStock > 0 ? 'text-green-600' : 'text-red-500'}">
					{currentStock} {selectedProduct.default_unit}
				</span>
			</div>

			{#if currentStock > 0}
				<div class="py-4">
					<label class="block text-lg font-semibold text-gray-700 mb-4">How many did you use?</label>
					<QuantityPicker
						bind:value={useQuantity}
						min={1}
						max={currentStock}
						unit={selectedProduct.default_unit}
					/>
				</div>

				<button class="w-full py-5 rounded-2xl bg-gradient-to-r from-red-500 to-rose-600 text-white text-xl font-bold shadow-lg active:scale-95 transition-transform" on:click={handleUse}>
					Use {useQuantity} {selectedProduct.default_unit}
				</button>
			{:else}
				<p class="text-center py-6 text-xl text-gray-500">This item is out of stock</p>
				<a href="/add" class="block w-full py-5 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-600 text-white text-xl font-bold shadow-lg text-center">Add Stock</a>
			{/if}
		</div>
	{/if}
</Modal>
