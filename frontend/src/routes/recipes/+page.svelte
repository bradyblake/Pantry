<script lang="ts">
	import { onMount } from 'svelte';
	import Header from '$lib/components/Header.svelte';
	import SearchBar from '$lib/components/SearchBar.svelte';
	import { recipesApi } from '$lib/api';
	import type { Recipe, RecipeSuggestion } from '$lib/types';
	import { parseTags } from '$lib/types';

	let recipes: Recipe[] = [];
	let suggestions: RecipeSuggestion[] = [];
	let loading = true;
	let error = '';
	let searchQuery = '';
	let showSuggestions = true;

	onMount(function() {
		loadData();
	});

	async function loadData() {
		loading = true;
		error = '';
		try {
			const results = await Promise.all([
				recipesApi.list(),
				recipesApi.getSuggestions(6)
			]);
			recipes = results[0];
			suggestions = results[1];
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load recipes';
		} finally {
			loading = false;
		}
	}

	async function handleSearch(query: string) {
		searchQuery = query;
		if (!query) {
			loadData();
			return;
		}
		loading = true;
		try {
			recipes = await recipesApi.list({ search: query });
			showSuggestions = false;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Search failed';
		} finally {
			loading = false;
		}
	}

	function getSuggestionColor(status: string): string {
		if (status === 'ready') return 'bg-green-100 border-green-500';
		if (status === 'almost_ready') return 'bg-yellow-100 border-yellow-500';
		if (status === 'need_items') return 'bg-orange-100 border-orange-500';
		return 'bg-gray-100 border-gray-300';
	}

	function getSuggestionLabel(status: string): string {
		if (status === 'ready') return 'Ready!';
		if (status === 'almost_ready') return 'Almost ready';
		if (status === 'need_items') return 'Need items';
		return 'Need shopping';
	}

	function formatTime(prep: number | null, cook: number | null): string {
		var parts: string[] = [];
		if (prep) parts.push('Prep: ' + prep + 'm');
		if (cook) parts.push('Cook: ' + cook + 'm');
		return parts.join(' | ') || '';
	}
</script>

<Header title="Recipes" showBack backHref="/" />

<main class="flex-1 flex flex-col overflow-hidden p-4">
	<div class="flex flex-col gap-3 mb-4 shrink-0">
		<SearchBar placeholder="Search recipes..." on:search={(e) => handleSearch(e.detail)} />
		<div class="flex gap-3">
			<a href="/recipes/add" class="flex-1 px-6 py-3 rounded-xl bg-green-500 text-white font-bold text-lg text-center whitespace-nowrap active:scale-95 transition-transform">
				+ Add Recipe
			</a>
			<a href="/recipes/import-url" class="flex-1 px-6 py-3 rounded-xl bg-blue-500 text-white font-bold text-lg text-center whitespace-nowrap active:scale-95 transition-transform">
				Import URL
			</a>
			<a href="/recipes/upload" class="flex-1 px-6 py-3 rounded-xl bg-purple-500 text-white font-bold text-lg text-center whitespace-nowrap active:scale-95 transition-transform">
				Upload PDF
			</a>
		</div>
	</div>

	{#if loading}
		<div class="flex justify-center py-12">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
		</div>
	{:else if error}
		<div class="bg-red-100 border-2 border-red-400 text-red-700 p-4 rounded-xl mb-4 text-lg">
			{error}
		</div>
	{:else}
		<div class="flex-1 overflow-y-auto">
			<!-- Tonight's Suggestions -->
			{#if showSuggestions && suggestions.length > 0}
				<section class="mb-6">
					<h2 class="text-xl font-bold text-gray-700 mb-3">Tonight's Suggestions</h2>
					<div class="grid grid-cols-2 gap-3">
						{#each suggestions as suggestion}
							{@const isReady = suggestion.status === 'ready'}
							<a
								href="/recipes/{suggestion.recipe.id}"
								class="p-4 rounded-2xl border-2 active:scale-95 transition-transform
									{isReady ? 'bg-green-50 border-green-300' :
									 suggestion.status === 'almost_ready' ? 'bg-amber-50 border-amber-300' :
									 'bg-gray-50 border-gray-200'}"
							>
								<h3 class="text-lg font-bold text-gray-800 line-clamp-2 mb-2">
									{suggestion.recipe.name}
								</h3>
								<span class="text-sm font-semibold {
									isReady ? 'text-green-600' :
									suggestion.status === 'almost_ready' ? 'text-amber-600' :
									'text-gray-500'
								}">
									{getSuggestionLabel(suggestion.status)}
								</span>
							</a>
						{/each}
					</div>
				</section>
			{/if}

			<!-- All Recipes -->
			<section>
				<h2 class="text-xl font-bold text-gray-700 mb-3">
					{searchQuery ? 'Search Results' : 'All Recipes'}
				</h2>

				{#if recipes.length === 0}
					<div class="text-center py-16">
						<span class="text-6xl block mb-4">&#128214;</span>
						{#if searchQuery}
							<p class="text-xl text-gray-500">No recipes found for "{searchQuery}"</p>
						{:else}
							<p class="text-xl text-gray-500">No recipes yet</p>
							<p class="text-gray-400 mt-2">Upload a PDF or add recipes manually</p>
						{/if}
					</div>
				{:else}
					<div class="grid grid-cols-2 gap-3">
						{#each recipes as recipe}
							<a href="/recipes/{recipe.id}" class="p-4 rounded-2xl bg-white border-2 border-gray-100 shadow-sm active:scale-95 transition-transform">
								<h3 class="text-lg font-bold text-gray-800 line-clamp-2">{recipe.name}</h3>
								<div class="flex gap-2 mt-2 text-sm text-gray-400">
									{#if recipe.servings}
										<span>Serves {recipe.servings}</span>
									{/if}
									{#if recipe.ingredients.length > 0}
										<span>{recipe.ingredients.length} items</span>
									{/if}
								</div>
							</a>
						{/each}
					</div>
				{/if}
			</section>
		</div>
	{/if}
</main>

<style>
	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
</style>
