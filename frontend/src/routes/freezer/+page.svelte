<script lang="ts">
	import { onMount } from 'svelte';
	import { Header, FreezerItemCard, Modal, QuantityPicker } from '$lib/components';
	import {
		freezers,
		selectedFreezerId,
		freezerContents,
		freezerContentsByCategory,
		oldestFrozenItems,
		inventory
	} from '$lib/stores';
	import type { InventoryItem } from '$lib/types';
	import { getDaysFrozen } from '$lib/types';

	let selectedItem: InventoryItem | null = null;
	let showModal = false;
	let useQuantity = 1;

	onMount(async () => {
		const freezerList = await freezers.load();
		if (freezerList.length > 0 && !$selectedFreezerId) {
			$selectedFreezerId = freezerList[0].id;
		}
		if ($selectedFreezerId) {
			await freezerContents.load($selectedFreezerId);
		}
		await oldestFrozenItems.load(undefined, 90, 5);
	});

	$: if ($selectedFreezerId) {
		freezerContents.load($selectedFreezerId);
	}

	function handleItemClick(item: InventoryItem) {
		selectedItem = item;
		useQuantity = Math.min(1, item.quantity);
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
				// Refresh freezer contents
				if ($selectedFreezerId) {
					await freezerContents.load($selectedFreezerId);
				}
				await oldestFrozenItems.load();
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
				if ($selectedFreezerId) {
					await freezerContents.load($selectedFreezerId);
				}
				await oldestFrozenItems.load();
			} catch (e) {
				console.error('Failed to remove:', e);
			}
		}
	}
</script>

<Header title="Freezer" showBack backHref="/" />

<main class="flex-1 flex flex-col overflow-hidden">
	<!-- Freezer tabs -->
	<div class="p-4 pb-3 flex gap-2 overflow-x-auto shrink-0">
		{#each $freezers as freezer}
			<button
				class="px-5 py-3 rounded-xl text-lg font-semibold whitespace-nowrap transition-all {$selectedFreezerId === freezer.id ? 'bg-cyan-500 text-white shadow-lg' : 'bg-white text-gray-600 border border-gray-200'}"
				on:click={() => $selectedFreezerId = freezer.id}
			>
				&#129482; {freezer.name}
			</button>
		{/each}
	</div>

	<div class="flex-1 p-4 pt-0 overflow-y-auto space-y-4">
		<!-- Oldest items warning -->
		{#if $oldestFrozenItems.length > 0}
			<section class="p-4 rounded-2xl border-2 border-amber-300 bg-amber-50">
				<h3 class="text-xl font-bold text-amber-800 mb-3">&#9888; Use Soon</h3>
				<div class="space-y-2">
					{#each $oldestFrozenItems.slice(0, 3) as item}
						{@const days = getDaysFrozen(item.frozen_date)}
						<button
							type="button"
							class="w-full flex items-center justify-between p-3 rounded-xl bg-white border border-amber-200 text-left active:scale-95 transition-transform"
							on:click={() => handleItemClick(item)}
						>
							<span class="text-lg font-semibold text-amber-900">{item.product.name}</span>
							<span class="text-lg font-bold text-amber-600">{days}d</span>
						</button>
					{/each}
				</div>
			</section>
		{/if}

		<!-- Freezer contents by category -->
		{#each Object.entries($freezerContentsByCategory) as [category, items]}
			<section>
				<h3 class="text-lg font-bold text-gray-700 mb-3">{category}</h3>
				<div class="grid grid-cols-2 gap-3">
					{#each items as item}
						{@const days = getDaysFrozen(item.frozen_date)}
						{@const isOld = days !== null && days > 90}
						<button
							on:click={() => handleItemClick(item)}
							class="p-4 rounded-2xl text-left transition-all active:scale-95
								{isOld ? 'bg-amber-50 border-2 border-amber-200' : 'bg-white border-2 border-gray-100 shadow-sm'}"
						>
							<p class="text-xl font-bold text-gray-800 truncate">{item.product.name}</p>
							<div class="flex items-center justify-between mt-2">
								<span class="text-lg text-gray-600">{item.quantity} {item.product.default_unit}</span>
								{#if days !== null}
									<span class="text-lg font-bold {isOld ? 'text-amber-600' : 'text-cyan-600'}">{days}d</span>
								{/if}
							</div>
						</button>
					{/each}
				</div>
			</section>
		{:else}
			<div class="text-center py-16">
				{#if $freezers.length === 0}
					<p class="text-xl text-gray-500">No freezers configured</p>
					<a href="/settings" class="inline-block mt-4 px-8 py-4 rounded-2xl bg-cyan-500 text-white text-xl font-bold">Add Freezer</a>
				{:else}
					<p class="text-xl text-gray-500">This freezer is empty</p>
				{/if}
			</div>
		{/each}
	</div>

	<!-- Add to freezer button -->
	<div class="p-4 border-t border-gray-100 shrink-0">
		<a href="/freezer/add" class="block w-full py-5 rounded-2xl bg-gradient-to-r from-cyan-500 to-cyan-600 text-white text-xl font-bold shadow-lg text-center active:scale-95 transition-transform">
			+ Add to Freezer
		</a>
	</div>
</main>

<!-- Item modal -->
<Modal bind:open={showModal} title={selectedItem?.product.name || ''} on:close={() => showModal = false}>
	{#if selectedItem}
		{@const days = getDaysFrozen(selectedItem.frozen_date)}
		<div class="space-y-4">
			<div class="grid grid-cols-2 gap-3">
				<div class="py-3 px-4 bg-gray-50 rounded-xl">
					<span class="text-sm text-gray-500">Quantity</span>
					<p class="text-xl font-bold">{selectedItem.quantity} {selectedItem.product.default_unit}</p>
				</div>
				{#if days !== null}
					<div class="py-3 px-4 bg-cyan-50 rounded-xl">
						<span class="text-sm text-cyan-600">Days Frozen</span>
						<p class="text-xl font-bold text-cyan-700">{days} days</p>
					</div>
				{/if}
			</div>

			{#if selectedItem.container_description}
				<div class="py-3 px-4 bg-gray-50 rounded-xl">
					<span class="text-sm text-gray-500">Container</span>
					<p class="text-lg font-semibold">{selectedItem.container_description}</p>
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

			<div class="flex gap-3">
				<button class="flex-1 py-5 rounded-2xl bg-gradient-to-r from-red-500 to-rose-600 text-white text-xl font-bold shadow-lg active:scale-95 transition-transform" on:click={handleUse}>
					Use {useQuantity}
				</button>
				<button class="py-5 px-6 rounded-2xl bg-gray-200 text-gray-700 text-xl font-bold active:scale-95 transition-transform" on:click={handleRemove}>
					Remove
				</button>
			</div>
		</div>
	{/if}
</Modal>
