<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import type { Product } from '../types';

	export let product: Product;
	export let selected: boolean = false;

	const dispatch = createEventDispatcher<{ click: Product }>();
</script>

<button
	type="button"
	on:click={() => dispatch('click', product)}
	class="w-full p-4 rounded-xl border-2 transition-all text-left
		{selected
			? 'border-primary-500 bg-primary-50'
			: 'border-gray-200 hover:border-gray-300 active:bg-gray-50'}"
>
	<p class="font-semibold text-gray-900">{product.name}</p>
	{#if product.category}
		<p class="text-sm text-gray-500">{product.category}</p>
	{/if}
	<p class="text-sm text-gray-400 mt-1">
		{product.default_quantity} {product.default_unit}
	</p>
</button>
