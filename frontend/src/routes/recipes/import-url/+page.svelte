<script lang="ts">
	import Header from '$lib/components/Header.svelte';
	import { recipesApi } from '$lib/api';
	import type { Recipe } from '$lib/types';
	import { goto } from '$app/navigation';

	let url = '';
	let loading = false;
	let error = '';
	let importedRecipes: Recipe[] = [];

	async function handleImport() {
		if (!url.trim()) {
			error = 'Please enter a URL';
			return;
		}

		loading = true;
		error = '';
		importedRecipes = [];

		try {
			const recipes = await recipesApi.importFromUrl(url.trim());
			importedRecipes = Array.isArray(recipes) ? recipes : [recipes];
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to import recipe from URL';
		} finally {
			loading = false;
		}
	}

	function detectPlatform(inputUrl: string): string {
		if (inputUrl.includes('tiktok.com')) return 'TikTok';
		if (inputUrl.includes('instagram.com')) return 'Instagram';
		if (inputUrl.includes('youtube.com') || inputUrl.includes('youtu.be')) return 'YouTube';
		if (inputUrl.includes('pinterest.com')) return 'Pinterest';
		return 'website';
	}
</script>

<Header title="Import from URL" showBack backHref="/recipes" />

<main class="flex-1 flex flex-col overflow-hidden p-4">
	<div class="mb-6">
		<p class="text-gray-500 text-lg mb-4">
			Paste a link from TikTok, Instagram, YouTube, a recipe blog, or any website with a recipe. AI will extract the recipe details automatically.
		</p>

		<div class="flex flex-col gap-3">
			<input
				type="url"
				bind:value={url}
				placeholder="https://www.tiktok.com/@user/video/..."
				class="w-full px-4 py-4 rounded-xl border-2 border-gray-200 text-lg focus:border-blue-500 focus:outline-none"
				on:keydown={(e) => { if (e.key === 'Enter') handleImport(); }}
				disabled={loading}
			/>

			<button
				on:click={handleImport}
				disabled={loading || !url.trim()}
				class="w-full px-6 py-4 rounded-xl bg-blue-500 text-white font-bold text-xl active:scale-95 transition-transform disabled:opacity-50 disabled:active:scale-100"
			>
				{#if loading}
					<span class="flex items-center justify-center gap-3">
						<span class="animate-spin inline-block w-6 h-6 border-3 border-white border-t-transparent rounded-full"></span>
						Extracting recipe from {detectPlatform(url)}...
					</span>
				{:else}
					Import Recipe
				{/if}
			</button>
		</div>
	</div>

	{#if error}
		<div class="bg-red-100 border-2 border-red-400 text-red-700 p-4 rounded-xl mb-4 text-lg">
			{error}
		</div>
	{/if}

	{#if importedRecipes.length > 0}
		<div class="flex-1 overflow-y-auto">
			<h2 class="text-xl font-bold text-gray-700 mb-3">
				{importedRecipes.length === 1 ? 'Recipe Imported!' : importedRecipes.length + ' Recipes Imported!'}
			</h2>
			<div class="flex flex-col gap-3">
				{#each importedRecipes as recipe}
					<a
						href="/recipes/{recipe.id}"
						class="p-5 rounded-2xl bg-green-50 border-2 border-green-300 active:scale-[0.98] transition-transform"
					>
						<h3 class="text-xl font-bold text-gray-800 mb-1">{recipe.name}</h3>
						{#if recipe.description}
							<p class="text-gray-500 mb-2 line-clamp-2">{recipe.description}</p>
						{/if}
						<div class="flex gap-3 text-sm text-gray-400">
							{#if recipe.servings}
								<span>Serves {recipe.servings}</span>
							{/if}
							{#if recipe.ingredients.length > 0}
								<span>{recipe.ingredients.length} ingredients</span>
							{/if}
							{#if recipe.prep_time_minutes || recipe.cook_time_minutes}
								<span>
									{recipe.prep_time_minutes ? recipe.prep_time_minutes + 'm prep' : ''}
									{recipe.prep_time_minutes && recipe.cook_time_minutes ? ' + ' : ''}
									{recipe.cook_time_minutes ? recipe.cook_time_minutes + 'm cook' : ''}
								</span>
							{/if}
						</div>
						<span class="inline-block mt-2 text-green-600 font-semibold text-sm">View recipe &rarr;</span>
					</a>
				{/each}
			</div>
		</div>
	{/if}

	{#if !loading && importedRecipes.length === 0 && !error}
		<div class="flex-1 flex flex-col items-center justify-center text-center py-8">
			<span class="text-6xl mb-4">&#127760;</span>
			<p class="text-lg text-gray-400">Supports TikTok, Instagram, YouTube, Pinterest, and recipe blogs</p>
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
	.border-3 {
		border-width: 3px;
	}
</style>
