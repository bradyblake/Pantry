<script lang="ts">
	import { goto } from '$app/navigation';
	import Header from '$lib/components/Header.svelte';
	import { recipesApi } from '$lib/api';
	import type { RecipeDocument, Recipe } from '$lib/types';

	type UploadState = 'idle' | 'uploading' | 'uploaded' | 'parsing' | 'done' | 'error';

	let state: UploadState = 'idle';
	let error = '';
	let document: RecipeDocument | null = null;
	let parsedRecipes: Recipe[] = [];
	let useVision = true;

	let fileInput: HTMLInputElement;

	async function handleFileSelect(event: Event) {
		var input = event.target as HTMLInputElement;
		if (!input.files || input.files.length === 0) return;

		var file = input.files[0];

		// Validate file type
		var validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/webp'];
		if (validTypes.indexOf(file.type) === -1) {
			error = 'Please select a PDF or image file';
			return;
		}

		// Validate size (max 10MB)
		if (file.size > 10 * 1024 * 1024) {
			error = 'File too large. Maximum size is 10MB';
			return;
		}

		state = 'uploading';
		error = '';

		try {
			document = await recipesApi.uploadDocument(file);
			state = 'uploaded';
		} catch (e) {
			error = e instanceof Error ? e.message : 'Upload failed';
			state = 'error';
		}
	}

	async function handleParse() {
		if (!document) return;

		state = 'parsing';
		error = '';

		try {
			parsedRecipes = await recipesApi.parseDocument(document.id, useVision);
			state = 'done';
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to parse document';
			state = 'error';
		}
	}

	function reset() {
		state = 'idle';
		error = '';
		document = null;
		parsedRecipes = [];
		if (fileInput) fileInput.value = '';
	}

	function formatBytes(bytes: number | null): string {
		if (!bytes) return '';
		if (bytes < 1024) return bytes + ' B';
		if (bytes < 1024 * 1024) return Math.round(bytes / 1024) + ' KB';
		return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
	}
</script>

<Header title="Upload Recipe" backLink="/recipes" />

<main class="p-4 pb-24">
	{#if error}
		<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
			{error}
			<button type="button" class="float-right font-bold" on:click={function() { error = ''; }}>
				&times;
			</button>
		</div>
	{/if}

	<!-- Idle State - File Selection -->
	{#if state === 'idle' || state === 'error'}
		<div class="card p-6 text-center">
			<div class="text-6xl mb-4">📄</div>
			<h2 class="text-xl font-semibold mb-2">Upload a Recipe</h2>
			<p class="text-gray-500 mb-6">
				Upload a PDF or photo of a recipe to automatically extract it
			</p>

			<input
				type="file"
				accept=".pdf,image/jpeg,image/png,image/webp"
				class="hidden"
				bind:this={fileInput}
				on:change={handleFileSelect}
			/>

			<button
				type="button"
				class="btn btn-primary w-full mb-3"
				on:click={function() { fileInput.click(); }}
			>
				Select PDF or Image
			</button>

			<p class="text-xs text-gray-400">
				Supports PDF, JPEG, PNG, WebP (max 10MB)
			</p>
		</div>

		<div class="mt-6">
			<h3 class="font-medium mb-3">How it works:</h3>
			<ol class="space-y-3 text-sm text-gray-600">
				<li class="flex gap-3">
					<span class="bg-primary text-white w-6 h-6 rounded-full flex items-center justify-center text-sm shrink-0">1</span>
					<span>Upload a PDF or photo of your recipe</span>
				</li>
				<li class="flex gap-3">
					<span class="bg-primary text-white w-6 h-6 rounded-full flex items-center justify-center text-sm shrink-0">2</span>
					<span>AI extracts the recipe name, ingredients, and instructions</span>
				</li>
				<li class="flex gap-3">
					<span class="bg-primary text-white w-6 h-6 rounded-full flex items-center justify-center text-sm shrink-0">3</span>
					<span>Review and save the recipe to your collection</span>
				</li>
			</ol>
		</div>
	{/if}

	<!-- Uploading State -->
	{#if state === 'uploading'}
		<div class="card p-6 text-center">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
			<p class="text-gray-600">Uploading file...</p>
		</div>
	{/if}

	<!-- Uploaded State - Ready to Parse -->
	{#if state === 'uploaded' && document}
		<div class="card p-4 mb-4">
			<div class="flex items-center gap-3">
				<div class="text-3xl">
					{document.file_type === 'pdf' ? '📄' : '🖼️'}
				</div>
				<div class="flex-1">
					<p class="font-medium">{document.original_filename}</p>
					<p class="text-sm text-gray-500">
						{formatBytes(document.file_size_bytes)}
						{#if document.page_count}
							&bull; {document.page_count} pages
						{/if}
					</p>
				</div>
				<button
					type="button"
					class="text-gray-400 hover:text-red-500"
					on:click={reset}
				>
					&times;
				</button>
			</div>
		</div>

		<div class="card p-4 mb-4">
			<label class="flex items-center gap-3 cursor-pointer">
				<input
					type="checkbox"
					bind:checked={useVision}
					class="w-5 h-5"
				/>
				<div>
					<p class="font-medium">Use Vision AI</p>
					<p class="text-sm text-gray-500">
						Better parsing for photos and complex PDFs (recommended)
					</p>
				</div>
			</label>
		</div>

		<button
			type="button"
			class="btn btn-primary w-full"
			on:click={handleParse}
		>
			Parse Recipe
		</button>
	{/if}

	<!-- Parsing State -->
	{#if state === 'parsing'}
		<div class="card p-6 text-center">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
			<p class="text-gray-600 mb-2">Analyzing document...</p>
			<p class="text-sm text-gray-400">This may take a moment</p>
		</div>
	{/if}

	<!-- Done State - Show Results -->
	{#if state === 'done'}
		<div class="mb-4">
			<div class="flex items-center gap-2 text-green-600 mb-2">
				<span class="text-2xl">✓</span>
				<span class="font-medium">
					{parsedRecipes.length} recipe{parsedRecipes.length !== 1 ? 's' : ''} extracted!
				</span>
			</div>
		</div>

		{#if parsedRecipes.length === 0}
			<div class="card p-4 text-center text-gray-500">
				<p>No recipes could be extracted from this document.</p>
				<button
					type="button"
					class="btn btn-secondary mt-3"
					on:click={reset}
				>
					Try Another File
				</button>
			</div>
		{:else}
			<div class="space-y-3 mb-6">
				{#each parsedRecipes as recipe}
					<a href="/recipes/{recipe.id}" class="card p-4 block">
						<div class="flex justify-between items-center">
							<div>
								<h3 class="font-medium">{recipe.name}</h3>
								<p class="text-sm text-gray-500">
									{recipe.ingredients.length} ingredients
									{#if recipe.servings}
										&bull; Serves {recipe.servings}
									{/if}
								</p>
							</div>
							<span class="text-gray-400">&rarr;</span>
						</div>
					</a>
				{/each}
			</div>

			<div class="flex gap-3">
				<button
					type="button"
					class="flex-1 btn btn-secondary"
					on:click={reset}
				>
					Upload Another
				</button>
				<a href="/recipes" class="flex-1 btn btn-primary text-center">
					View All Recipes
				</a>
			</div>
		{/if}
	{/if}
</main>
