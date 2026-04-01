<script lang="ts">
	import { goto } from '$app/navigation';
	import Header from '$lib/components/Header.svelte';
	import { recipesApi } from '$lib/api';
	import type { RecipeIngredientCreate } from '$lib/types';

	let name = '';
	let description = '';
	let instructions = '';
	let prepTime: number | null = null;
	let cookTime: number | null = null;
	let servings: number | null = null;
	let tagsInput = '';
	let ingredients: RecipeIngredientCreate[] = [];
	let newIngredient = '';

	let saving = false;
	let error = '';

	function addIngredient() {
		if (!newIngredient.trim()) return;
		ingredients = [...ingredients, {
			ingredient_text: newIngredient.trim(),
			is_optional: false
		}];
		newIngredient = '';
	}

	function removeIngredient(index: number) {
		ingredients = ingredients.filter(function(_, i) { return i !== index; });
	}

	function toggleOptional(index: number) {
		ingredients = ingredients.map(function(ing, i) {
			if (i === index) {
				return { ...ing, is_optional: !ing.is_optional };
			}
			return ing;
		});
	}

	async function handleSubmit() {
		if (!name.trim()) {
			error = 'Recipe name is required';
			return;
		}

		saving = true;
		error = '';

		try {
			var tags = tagsInput
				.split(',')
				.map(function(t) { return t.trim(); })
				.filter(function(t) { return t; });

			var recipe = await recipesApi.create({
				name: name.trim(),
				description: description.trim() || null,
				instructions: instructions.trim() || null,
				prep_time_minutes: prepTime,
				cook_time_minutes: cookTime,
				servings: servings,
				tags: tags.length > 0 ? JSON.stringify(tags) : null,
				ingredients: ingredients
			});

			goto('/recipes/' + recipe.id);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to create recipe';
			saving = false;
		}
	}
</script>

<Header title="Add Recipe" backLink="/recipes" />

<main class="p-4 pb-24">
	{#if error}
		<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
			{error}
		</div>
	{/if}

	<form on:submit|preventDefault={handleSubmit}>
		<!-- Basic Info -->
		<section class="card p-4 mb-4">
			<h2 class="font-semibold mb-3">Basic Info</h2>

			<div class="mb-4">
				<label class="block text-sm font-medium mb-1" for="name">
					Recipe Name *
				</label>
				<input
					type="text"
					id="name"
					class="input w-full"
					bind:value={name}
					placeholder="e.g., Chicken Alfredo"
				/>
			</div>

			<div class="mb-4">
				<label class="block text-sm font-medium mb-1" for="description">
					Description
				</label>
				<textarea
					id="description"
					class="input w-full"
					rows="2"
					bind:value={description}
					placeholder="Brief description of the dish"
				></textarea>
			</div>

			<div class="flex gap-4 mb-4">
				<div class="flex-1">
					<label class="block text-sm font-medium mb-1" for="prep">
						Prep Time (min)
					</label>
					<input
						type="number"
						id="prep"
						class="input w-full"
						bind:value={prepTime}
						min="0"
					/>
				</div>
				<div class="flex-1">
					<label class="block text-sm font-medium mb-1" for="cook">
						Cook Time (min)
					</label>
					<input
						type="number"
						id="cook"
						class="input w-full"
						bind:value={cookTime}
						min="0"
					/>
				</div>
				<div class="flex-1">
					<label class="block text-sm font-medium mb-1" for="servings">
						Servings
					</label>
					<input
						type="number"
						id="servings"
						class="input w-full"
						bind:value={servings}
						min="1"
					/>
				</div>
			</div>

			<div>
				<label class="block text-sm font-medium mb-1" for="tags">
					Tags
				</label>
				<input
					type="text"
					id="tags"
					class="input w-full"
					bind:value={tagsInput}
					placeholder="quick, mexican, kid-friendly (comma separated)"
				/>
			</div>
		</section>

		<!-- Ingredients -->
		<section class="card p-4 mb-4">
			<h2 class="font-semibold mb-3">Ingredients</h2>

			<div class="flex gap-2 mb-4">
				<input
					type="text"
					class="input flex-1"
					bind:value={newIngredient}
					placeholder="e.g., 1 lb ground beef"
					on:keypress={function(e) { if (e.key === 'Enter') { e.preventDefault(); addIngredient(); } }}
				/>
				<button
					type="button"
					class="btn btn-secondary"
					on:click={addIngredient}
				>
					Add
				</button>
			</div>

			{#if ingredients.length === 0}
				<p class="text-gray-500 text-sm text-center py-4">
					No ingredients added yet
				</p>
			{:else}
				<ul class="space-y-2">
					{#each ingredients as ing, i}
						<li class="flex items-center gap-2 p-2 bg-gray-50 rounded">
							<button
								type="button"
								class="text-xs px-2 py-1 rounded {ing.is_optional ? 'bg-gray-200' : 'bg-primary/10 text-primary'}"
								on:click={function() { toggleOptional(i); }}
							>
								{ing.is_optional ? 'Optional' : 'Required'}
							</button>
							<span class="flex-1 {ing.is_optional ? 'text-gray-500' : ''}">
								{ing.ingredient_text}
							</span>
							<button
								type="button"
								class="text-red-500 px-2"
								on:click={function() { removeIngredient(i); }}
							>
								&times;
							</button>
						</li>
					{/each}
				</ul>
			{/if}
		</section>

		<!-- Instructions -->
		<section class="card p-4 mb-4">
			<h2 class="font-semibold mb-3">Instructions</h2>
			<textarea
				class="input w-full"
				rows="8"
				bind:value={instructions}
				placeholder="Step by step cooking instructions..."
			></textarea>
		</section>

		<!-- Submit -->
		<button
			type="submit"
			class="btn btn-primary w-full"
			disabled={saving || !name.trim()}
		>
			{saving ? 'Saving...' : 'Save Recipe'}
		</button>
	</form>
</main>
