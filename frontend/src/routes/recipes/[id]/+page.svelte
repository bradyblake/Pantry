<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount, onDestroy } from 'svelte';
	import Header from '$lib/components/Header.svelte';
	import Modal from '$lib/components/Modal.svelte';
	import QuantityPicker from '$lib/components/QuantityPicker.svelte';
	import { recipesApi, inventoryApi, zonesApi } from '$lib/api';
	import type { Recipe, InventoryItem, FindIngredientsResponse } from '$lib/types';
	import { parseTags } from '$lib/types';

	let recipe: Recipe | null = null;
	let inventory: Map<number, number> = new Map();
	let inventoryItems: InventoryItem[] = [];
	let loading = true;
	let error = '';

	// Cooking mode state
	let cookingMode = false;
	let servingsToMake = 1;
	let checkedIngredients: Set<number> = new Set();
	let making = false;
	let cookingComplete = false;
	let makeResult: { decremented: object[]; skipped: string[] } | null = null;

	let showDeleteModal = false;
	let deleting = false;

	// Ingredient finder state
	let showFinderModal = false;
	let finding = false;
	let finderResult: FindIngredientsResponse | null = null;

	$: recipeId = parseInt($page.params.id);

	// Parse instructions into steps
	$: instructionSteps = recipe?.instructions
		? recipe.instructions
			.split(/\n/)
			.map(s => s.trim())
			.filter(s => s.length > 0)
		: [];

	onMount(function() {
		loadData();
	});

	async function loadData() {
		loading = true;
		error = '';
		try {
			const results = await Promise.all([
				recipesApi.get(recipeId),
				inventoryApi.list()
			]);
			recipe = results[0];
			servingsToMake = recipe.servings || 1;

			// Build inventory map and store raw items
			var inv = results[1] as InventoryItem[];
			inventoryItems = inv;
			for (var i = 0; i < inv.length; i++) {
				var item = inv[i];
				var current = inventory.get(item.product_id) || 0;
				inventory.set(item.product_id, current + item.quantity);
			}
			inventory = inventory;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load recipe';
		} finally {
			loading = false;
		}
	}

	function getIngredientStatus(productId: number | null, needed: number | null): string {
		if (!productId) return 'untracked';
		var have = inventory.get(productId) || 0;
		var need = needed || 1;
		if (have >= need) return 'have';
		if (have > 0) return 'partial';
		return 'missing';
	}

	function getIngredientStatusIcon(status: string): string {
		if (status === 'have') return '✓';
		if (status === 'partial') return '½';
		if (status === 'missing') return '✗';
		return '?';
	}

	function getInventoryEntriesForProduct(productId: number | null): InventoryItem[] {
		if (!productId) return [];
		return inventoryItems.filter(item => item.product_id === productId && item.quantity > 0);
	}

	function startCooking() {
		cookingMode = true;
		checkedIngredients = new Set();
		cookingComplete = false;
		makeResult = null;
	}

	function exitCooking() {
		cookingMode = false;
		checkedIngredients = new Set();
		cookingComplete = false;
		makeResult = null;
	}

	function toggleIngredient(index: number) {
		if (checkedIngredients.has(index)) {
			checkedIngredients.delete(index);
		} else {
			checkedIngredients.add(index);
		}
		checkedIngredients = checkedIngredients;
	}

	async function handleFinishCooking() {
		if (!recipe) return;
		making = true;
		try {
			var result = await recipesApi.make(recipe.id, servingsToMake);
			makeResult = result;
			cookingComplete = true;
			// Reload inventory
			var inv = await inventoryApi.list();
			inventoryItems = inv;
			inventory = new Map();
			for (var i = 0; i < inv.length; i++) {
				var item = inv[i];
				var current = inventory.get(item.product_id) || 0;
				inventory.set(item.product_id, current + item.quantity);
			}
			inventory = inventory;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to update inventory';
		} finally {
			making = false;
		}
	}

	async function handleDelete() {
		if (!recipe) return;
		deleting = true;
		try {
			await recipesApi.delete(recipe.id);
			goto('/recipes');
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to delete recipe';
			deleting = false;
		}
	}

	function formatTime(minutes: number | null): string {
		if (!minutes) return '';
		if (minutes < 60) return minutes + ' min';
		var hours = Math.floor(minutes / 60);
		var mins = minutes % 60;
		if (mins === 0) return hours + ' hr';
		return hours + ' hr ' + mins + ' min';
	}

	async function handleFindIngredients() {
		if (!recipe) return;
		finding = true;
		showFinderModal = true;
		try {
			finderResult = await zonesApi.findIngredients(recipe.id, true);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to find ingredients';
		} finally {
			finding = false;
		}
	}

	async function handleTurnOffLights() {
		try {
			await zonesApi.allLedsOff();
		} catch (e) {
			console.error('Failed to turn off lights:', e);
		}
		showFinderModal = false;
		finderResult = null;
	}

	onDestroy(function() {
		if (finderResult) {
			zonesApi.allLedsOff();
		}
	});
</script>

{#if cookingMode && recipe}
	<!-- COOKING MODE - Full screen cooking view -->
	<header class="bg-gradient-to-r from-green-500 to-emerald-600 text-white p-4 shrink-0">
		<div class="flex items-center justify-between">
			<button
				type="button"
				class="p-2 -ml-2 rounded-xl hover:bg-white/20 active:bg-white/30"
				on:click={exitCooking}
			>
				<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				</svg>
			</button>
			<div class="text-center">
				<h1 class="text-2xl font-bold">&#127859; Cooking Mode</h1>
				<p class="text-green-100">{recipe.name}</p>
			</div>
			<div class="w-12"></div>
		</div>
	</header>

	<main class="flex-1 flex flex-col overflow-hidden bg-gray-50">
		{#if cookingComplete}
			<!-- Cooking Complete Screen -->
			<div class="flex-1 flex flex-col items-center justify-center p-8">
				<span class="text-8xl mb-6">&#127881;</span>
				<h2 class="text-3xl font-bold text-gray-800 mb-4">Done Cooking!</h2>
				<p class="text-xl text-gray-600 mb-8">Inventory has been updated</p>

				{#if makeResult && makeResult.decremented.length > 0}
					<div class="w-full max-w-md p-4 bg-green-50 rounded-2xl border-2 border-green-200 mb-6">
						<p class="font-bold text-green-800 mb-2">Used from inventory:</p>
						{#each makeResult.decremented as item}
							<p class="text-green-700">{item.ingredient}: -{item.amount_used}</p>
						{/each}
					</div>
				{/if}

				<button
					type="button"
					class="w-full max-w-md py-5 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-600 text-white text-xl font-bold shadow-lg active:scale-95 transition-transform"
					on:click={exitCooking}
				>
					&#9989; Done
				</button>
			</div>
		{:else}
			<!-- Active Cooking Screen -->
			<div class="flex-1 overflow-y-auto p-4">
				<!-- Servings Adjuster -->
				<div class="flex items-center justify-center gap-4 mb-6 p-4 bg-white rounded-2xl shadow-sm">
					<span class="text-lg font-semibold text-gray-700">Servings:</span>
					<button
						type="button"
						class="w-12 h-12 rounded-xl bg-gray-200 text-2xl font-bold active:scale-95"
						on:click={() => servingsToMake = Math.max(1, servingsToMake - 1)}
					>-</button>
					<span class="text-3xl font-bold text-gray-800 w-12 text-center">{servingsToMake}</span>
					<button
						type="button"
						class="w-12 h-12 rounded-xl bg-green-500 text-white text-2xl font-bold active:scale-95"
						on:click={() => servingsToMake = Math.min(20, servingsToMake + 1)}
					>+</button>
				</div>

				<!-- Ingredients Checklist -->
				<section class="mb-6">
					<h2 class="text-xl font-bold text-gray-700 mb-3">&#127822; Gather Ingredients</h2>
					<div class="bg-white rounded-2xl overflow-hidden shadow-sm">
						{#each recipe.ingredients as ing, i}
							{@const entries = getInventoryEntriesForProduct(ing.product_id)}
							<button
								type="button"
								class="w-full flex items-center gap-4 p-4 text-left active:bg-gray-50 {i > 0 ? 'border-t border-gray-100' : ''}"
								on:click={() => toggleIngredient(i)}
							>
								<span class="w-10 h-10 rounded-full border-3 flex items-center justify-center text-xl shrink-0
									{checkedIngredients.has(i) ? 'bg-green-500 border-green-500 text-white' : 'border-gray-300'}">
									{#if checkedIngredients.has(i)}&#10003;{/if}
								</span>
								<div class="flex-1 min-w-0">
									<span class="text-lg {checkedIngredients.has(i) ? 'line-through text-gray-400' : 'text-gray-800'}">
										{ing.ingredient_text}
									</span>
									{#if entries.length > 0 && !checkedIngredients.has(i)}
										<div class="mt-1 space-y-0.5">
											{#each entries as entry}
												<p class="text-sm text-gray-500">
													<span class="font-medium text-gray-600">{entry.product.name}</span>
													<span class="mx-1">-</span>
													<span>{entry.quantity} {ing.unit || entry.product.default_unit}</span>
													{#if entry.location}
														<span class="mx-1">in</span>
														<span class="text-blue-600">{entry.location}{entry.freezer ? ' (' + entry.freezer.name + ')' : ''}</span>
													{/if}
													{#if entry.container_description}
														<span class="text-gray-400"> - {entry.container_description}</span>
													{/if}
												</p>
											{/each}
										</div>
									{/if}
								</div>
							</button>
						{/each}
					</div>
				</section>

				<!-- Instructions -->
				{#if instructionSteps.length > 0}
					<section class="mb-6">
						<h2 class="text-xl font-bold text-gray-700 mb-3">&#128203; Instructions</h2>
						<div class="space-y-3">
							{#each instructionSteps as step, i}
								<div class="p-4 bg-white rounded-2xl shadow-sm">
									<div class="flex gap-4">
										<span class="w-10 h-10 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center text-xl font-bold shrink-0">
											{i + 1}
										</span>
										<p class="text-lg text-gray-700 leading-relaxed">{step}</p>
									</div>
								</div>
							{/each}
						</div>
					</section>
				{/if}
			</div>

			<!-- Finish Cooking Button -->
			<div class="shrink-0 p-4 bg-white border-t border-gray-100">
				<button
					type="button"
					class="w-full py-6 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-600 text-white text-2xl font-bold shadow-lg active:scale-95 transition-transform disabled:opacity-50"
					disabled={making}
					on:click={handleFinishCooking}
				>
					{#if making}
						Updating Inventory...
					{:else}
						&#9989; Done Cooking
					{/if}
				</button>
			</div>
		{/if}
	</main>

{:else}
	<!-- NORMAL VIEW - Recipe details -->
	<Header title={recipe ? recipe.name : 'Recipe'} showBack backHref="/recipes" />

	<main class="flex-1 flex flex-col overflow-hidden">
		{#if loading}
			<div class="flex justify-center py-12">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
			</div>
		{:else if error}
			<div class="m-4 bg-red-100 border-2 border-red-400 text-red-700 p-4 rounded-xl text-lg">
				{error}
			</div>
		{:else if recipe}
			<div class="flex-1 overflow-y-auto p-4">
				<!-- Recipe Header -->
				<div class="p-5 rounded-2xl bg-gradient-to-br from-purple-50 to-purple-100 border-2 border-purple-200 mb-4">
					<h1 class="text-2xl font-bold text-gray-800 mb-2">{recipe.name}</h1>

					{#if recipe.description}
						<p class="text-lg text-gray-600 mb-3">{recipe.description}</p>
					{/if}

					<div class="flex flex-wrap gap-3 text-lg">
						{#if recipe.prep_time_minutes}
							<span class="px-3 py-1 bg-white rounded-lg">&#9201; {formatTime(recipe.prep_time_minutes)}</span>
						{/if}
						{#if recipe.cook_time_minutes}
							<span class="px-3 py-1 bg-white rounded-lg">&#127859; {formatTime(recipe.cook_time_minutes)}</span>
						{/if}
						{#if recipe.servings}
							<span class="px-3 py-1 bg-white rounded-lg">&#127869; Serves {recipe.servings}</span>
						{/if}
					</div>
				</div>

				<!-- Ingredients Preview -->
				<section class="mb-4">
					<h2 class="text-xl font-bold text-gray-700 mb-3">Ingredients ({recipe.ingredients.length})</h2>
					<div class="bg-white rounded-2xl border-2 border-gray-100 overflow-hidden">
						{#each recipe.ingredients.slice(0, 5) as ing, i}
							{@const status = getIngredientStatus(ing.product_id, ing.quantity)}
							{@const entries = getInventoryEntriesForProduct(ing.product_id)}
							<div class="flex items-center gap-4 p-4 {i > 0 ? 'border-t border-gray-100' : ''}">
								<span class="w-10 h-10 flex items-center justify-center rounded-full text-lg font-bold shrink-0 {
									status === 'have' ? 'bg-green-100 text-green-600' :
									status === 'partial' ? 'bg-amber-100 text-amber-600' :
									status === 'missing' ? 'bg-red-100 text-red-600' :
									'bg-gray-100 text-gray-400'
								}">
									{getIngredientStatusIcon(status)}
								</span>
								<div class="flex-1 min-w-0">
									<span class="text-lg text-gray-800">{ing.ingredient_text}</span>
									{#if ing.product && (status === 'have' || status === 'partial')}
										<div class="mt-1 space-y-0.5">
											{#each entries as entry}
												<p class="text-sm text-gray-500">
													<span class="font-medium text-gray-600">{entry.product.name}</span>
													<span class="mx-1">-</span>
													<span>{entry.quantity} {ing.unit || entry.product.default_unit}</span>
													{#if entry.location}
														<span class="mx-1">in</span>
														<span class="text-blue-600">{entry.location}{entry.freezer ? ' (' + entry.freezer.name + ')' : ''}</span>
													{/if}
													{#if entry.container_description}
														<span class="text-gray-400"> - {entry.container_description}</span>
													{/if}
												</p>
											{/each}
										</div>
									{:else if ing.product && status === 'missing'}
										<p class="text-sm text-red-400">Matched to: {ing.product.name} (out of stock)</p>
									{/if}
								</div>
							</div>
						{/each}
						{#if recipe.ingredients.length > 5}
							<div class="p-4 text-center text-gray-500 border-t border-gray-100">
								+{recipe.ingredients.length - 5} more ingredients
							</div>
						{/if}
					</div>
				</section>

				<!-- Instructions Preview -->
				{#if recipe.instructions}
					<section class="mb-4">
						<h2 class="text-xl font-bold text-gray-700 mb-3">Instructions</h2>
						<div class="bg-white rounded-2xl border-2 border-gray-100 p-5">
							<p class="text-lg text-gray-600 line-clamp-4">
								{recipe.instructions.slice(0, 200)}{recipe.instructions.length > 200 ? '...' : ''}
							</p>
							<p class="text-purple-600 font-semibold mt-2">Tap "Cook This!" to see full instructions</p>
						</div>
					</section>
				{/if}
			</div>

			<!-- Action Buttons -->
			<div class="shrink-0 p-4 border-t border-gray-100 bg-white">
				<button
					type="button"
					class="w-full py-6 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-600 text-white text-2xl font-bold shadow-lg active:scale-95 transition-transform mb-3"
					on:click={startCooking}
				>
					&#127859; Cook This!
				</button>
				<div class="flex gap-3">
					<button
						type="button"
						class="flex-1 py-4 rounded-2xl bg-blue-500 text-white text-lg font-bold shadow-md active:scale-95 transition-transform"
						on:click={handleFindIngredients}
					>
						&#128161; Find Ingredients
					</button>
					<button
						type="button"
						class="py-4 px-6 rounded-2xl bg-gray-200 text-gray-600 text-lg font-bold active:scale-95 transition-transform"
						on:click={function() { showDeleteModal = true; }}
					>
						&#128465;
					</button>
				</div>
			</div>
		{/if}
	</main>
{/if}

<!-- Delete Confirmation Modal -->
{#if showDeleteModal && recipe}
	<Modal title="Delete Recipe" open={showDeleteModal} on:close={function() { showDeleteModal = false; }}>
		<div class="text-center py-4">
			<span class="text-5xl block mb-4">&#128465;</span>
			<p class="text-lg text-gray-600 mb-6">
				Delete "{recipe.name}"? This cannot be undone.
			</p>
		</div>
		<div class="flex gap-3">
			<button
				type="button"
				class="flex-1 py-5 rounded-2xl bg-gray-200 text-gray-700 text-xl font-bold active:scale-95 transition-transform"
				on:click={function() { showDeleteModal = false; }}
			>
				Cancel
			</button>
			<button
				type="button"
				class="flex-1 py-5 rounded-2xl bg-red-500 text-white text-xl font-bold shadow-lg active:scale-95 transition-transform disabled:opacity-50"
				disabled={deleting}
				on:click={handleDelete}
			>
				{deleting ? 'Deleting...' : 'Delete'}
			</button>
		</div>
	</Modal>
{/if}

<!-- Ingredient Finder Modal -->
{#if showFinderModal}
	<Modal title="Find Ingredients" open={showFinderModal} on:close={handleTurnOffLights}>
		{#if finding}
			<div class="flex flex-col items-center justify-center py-12">
				<div class="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-500 mb-4"></div>
				<p class="text-xl text-gray-500">Lighting up zones...</p>
			</div>
		{:else if finderResult}
			<div class="mb-4 p-4 bg-blue-50 rounded-xl">
				<p class="text-lg text-blue-800 font-semibold">{finderResult.message}</p>
				{#if finderResult.zones_to_light.length > 0}
					<p class="text-blue-600 mt-1">
						&#128161; {finderResult.zones_to_light.length} zone{finderResult.zones_to_light.length !== 1 ? 's' : ''} lit up
					</p>
				{/if}
			</div>

			<div class="space-y-2 max-h-80 overflow-y-auto mb-4">
				{#each finderResult.ingredients as ing}
					<div class="flex items-center gap-3 p-3 rounded-xl {ing.zone_id ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'}">
						<span class="text-2xl">
							{#if ing.zone_id}
								&#128161;
							{:else if ing.in_stock}
								&#9989;
							{:else}
								&#10060;
							{/if}
						</span>
						<div class="flex-1 min-w-0">
							<p class="font-semibold text-gray-800">{ing.ingredient_text}</p>
							{#if ing.product_name}
								<p class="text-sm text-gray-600">Matched: <span class="font-medium">{ing.product_name}</span></p>
							{/if}
							{#if ing.inventory_entries && ing.inventory_entries.length > 0}
								{#each ing.inventory_entries as entry}
									<p class="text-sm text-gray-500">
										{entry.quantity}
										{#if entry.location}
											<span class="mx-1">in</span>
											<span class="text-blue-600">{entry.location}{entry.freezer_name ? ' (' + entry.freezer_name + ')' : ''}</span>
										{/if}
										{#if entry.container_description}
											<span class="text-gray-400"> - {entry.container_description}</span>
										{/if}
									</p>
								{/each}
							{:else if ing.zone_name}
								<p class="text-sm text-green-600 font-medium">
									{ing.zone_name}
									{#if ing.zone_location} - {ing.zone_location}{/if}
								</p>
							{:else if ing.product_name}
								<p class="text-sm text-gray-400">No zone assigned</p>
							{/if}
						</div>
						{#if ing.in_stock}
							<span class="px-3 py-1 bg-green-100 text-green-600 rounded-lg font-semibold">
								{ing.quantity_available}
							</span>
						{:else if ing.product_id}
							<span class="px-3 py-1 bg-red-100 text-red-500 rounded-lg font-semibold">Out</span>
						{/if}
					</div>
				{/each}
			</div>

			<button
				type="button"
				class="w-full py-5 rounded-2xl bg-blue-500 text-white text-xl font-bold shadow-lg active:scale-95 transition-transform"
				on:click={handleTurnOffLights}
			>
				&#128161; Turn Off Lights
			</button>
		{/if}
	</Modal>
{/if}
