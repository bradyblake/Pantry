<script lang="ts">
	import { onMount } from 'svelte';
	import { Header, SearchBar, Modal } from '$lib/components';
	import { shopping, uncheckedItems, checkedItems, products } from '$lib/stores';
	import type { ShoppingItem, Product } from '$lib/types';

	let showAddModal = false;
	let searchQuery = '';
	let customItemName = '';
	let selectedProduct: Product | null = null;

	onMount(async () => {
		await shopping.load();
		await products.load();
	});

	$: filteredProducts = searchQuery
		? $products.filter(p => p.name.toLowerCase().includes(searchQuery.toLowerCase()))
		: [];

	async function toggleItem(item: ShoppingItem) {
		await shopping.toggle(item.id);
	}

	async function removeItem(item: ShoppingItem) {
		await shopping.remove(item.id);
	}

	async function clearChecked() {
		await shopping.clearChecked();
	}

	async function addFromProduct(product: Product) {
		await shopping.add({
			product_id: product.id,
			quantity: product.default_quantity,
			unit: product.default_unit
		});
		showAddModal = false;
		searchQuery = '';
		selectedProduct = null;
	}

	async function addCustomItem() {
		if (customItemName.trim()) {
			await shopping.add({
				custom_item_name: customItemName.trim()
			});
			showAddModal = false;
			customItemName = '';
		}
	}

	async function generateFromLowStock() {
		const added = await shopping.generateFromLowStock();
		if (added.length === 0) {
			alert('No low-stock items to add');
		}
	}
</script>

<Header title="Shopping List" showBack backHref="/" />

<main class="flex-1 flex flex-col overflow-hidden">
	<div class="flex-1 p-4 overflow-y-auto space-y-4">
		<!-- Unchecked items -->
		{#if $uncheckedItems.length > 0}
			<section>
				<h3 class="text-lg font-bold text-gray-700 mb-3">
					&#128722; To Buy ({$uncheckedItems.length})
				</h3>
				<div class="space-y-2">
					{#each $uncheckedItems as item}
						<div class="flex items-center gap-4 p-4 bg-white rounded-2xl border-2 border-gray-100 shadow-sm">
							<button
								type="button"
								class="w-10 h-10 rounded-full border-3 border-gray-300 flex-shrink-0 active:scale-90 transition-transform"
								on:click={() => toggleItem(item)}
							></button>
							<div class="flex-1 min-w-0">
								<p class="text-xl font-semibold text-gray-800">
									{item.product?.name || item.custom_item_name}
								</p>
								{#if item.quantity}
									<p class="text-sm text-gray-400">
										{item.quantity} {item.unit || item.product?.default_unit || ''}
									</p>
								{/if}
							</div>
							<button
								type="button"
								class="p-3 text-gray-300 hover:text-red-500 rounded-xl active:scale-90 transition-all"
								on:click={() => removeItem(item)}
							>
								<svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
								</svg>
							</button>
						</div>
					{/each}
				</div>
			</section>
		{/if}

		<!-- Checked items -->
		{#if $checkedItems.length > 0}
			<section>
				<div class="flex items-center justify-between mb-3">
					<h3 class="text-lg font-bold text-gray-400">
						&#9989; Done ({$checkedItems.length})
					</h3>
					<button
						type="button"
						class="px-4 py-2 text-sm font-semibold text-red-500 bg-red-50 rounded-lg"
						on:click={clearChecked}
					>
						Clear all
					</button>
				</div>
				<div class="space-y-2 opacity-60">
					{#each $checkedItems as item}
						<div class="flex items-center gap-4 p-4 bg-gray-50 rounded-2xl">
							<button
								type="button"
								class="w-10 h-10 rounded-full bg-green-500 flex-shrink-0 flex items-center justify-center active:scale-90 transition-transform"
								on:click={() => toggleItem(item)}
							>
								<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
								</svg>
							</button>
							<p class="flex-1 text-xl line-through text-gray-400">
								{item.product?.name || item.custom_item_name}
							</p>
						</div>
					{/each}
				</div>
			</section>
		{/if}

		{#if $uncheckedItems.length === 0 && $checkedItems.length === 0}
			<div class="text-center py-16">
				<div class="w-24 h-24 mx-auto mb-4 rounded-2xl bg-rose-100 flex items-center justify-center">
					<span class="text-5xl">&#128203;</span>
				</div>
				<p class="text-xl text-gray-600 font-semibold mb-2">Shopping list is empty</p>
				<p class="text-gray-400 mb-6">Add items or generate from low stock</p>
				<button class="px-8 py-4 rounded-2xl bg-amber-500 text-white text-xl font-bold shadow-lg" on:click={generateFromLowStock}>
					+ Add Low-Stock Items
				</button>
			</div>
		{/if}
	</div>

	<!-- Bottom actions -->
	<div class="p-4 border-t border-gray-100 flex gap-3 shrink-0">
		<button class="flex-1 py-5 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-600 text-white text-xl font-bold shadow-lg active:scale-95 transition-transform" on:click={() => showAddModal = true}>
			+ Add Item
		</button>
		<button class="flex-1 py-5 rounded-2xl bg-amber-500 text-white text-xl font-bold shadow-lg active:scale-95 transition-transform" on:click={generateFromLowStock}>
			&#9888; Low Stock
		</button>
	</div>
</main>

<!-- Add item modal -->
<Modal bind:open={showAddModal} title="Add to Shopping List" on:close={() => showAddModal = false}>
	<div class="space-y-4">
		<SearchBar
			bind:value={searchQuery}
			placeholder="Search products..."
			autofocus
		/>

		{#if filteredProducts.length > 0}
			<div class="max-h-64 overflow-y-auto space-y-2">
				{#each filteredProducts as product}
					<button
						type="button"
						class="w-full p-4 rounded-xl text-left bg-gray-50 active:bg-gray-100 transition-colors"
						on:click={() => addFromProduct(product)}
					>
						<p class="text-lg font-semibold text-gray-800">{product.name}</p>
						{#if product.category}
							<p class="text-sm text-gray-400">{product.category}</p>
						{/if}
					</button>
				{/each}
			</div>
		{/if}

		<div class="h-px bg-gray-200 my-4"></div>

		<div>
			<label class="block text-lg font-semibold text-gray-700 mb-3">Or add custom item:</label>
			<div class="flex gap-3">
				<input
					type="text"
					bind:value={customItemName}
					class="flex-1 px-4 py-4 text-xl border-2 border-gray-200 rounded-xl focus:border-green-500 focus:outline-none"
					placeholder="Item name..."
				/>
				<button
					class="px-6 py-4 rounded-xl bg-green-500 text-white text-xl font-bold disabled:opacity-50 active:scale-95 transition-transform"
					on:click={addCustomItem}
					disabled={!customItemName.trim()}
				>
					Add
				</button>
			</div>
		</div>
	</div>
</Modal>
