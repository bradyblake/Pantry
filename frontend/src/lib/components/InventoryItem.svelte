<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import type { InventoryItem } from '../types';
	import { getStockLevel } from '../types';

	export let item: InventoryItem;

	const dispatch = createEventDispatcher<{ click: InventoryItem }>();

	$: stockLevel = getStockLevel(item.quantity);
	$: stockClass = {
		'high': 'text-green-600',
		'low': 'text-amber-500',
		'out': 'text-red-500'
	}[stockLevel];
	$: stockDotClass = {
		'high': 'stock-dot-high',
		'low': 'stock-dot-low',
		'out': 'stock-dot-out'
	}[stockLevel];
	$: badgeClass = {
		'high': '',
		'low': 'badge-warning',
		'out': 'badge-danger'
	}[stockLevel];
</script>

<button
	type="button"
	on:click={() => dispatch('click', item)}
	class="w-full flex items-center gap-3 p-3.5 rounded-xl hover:bg-gray-50/80 active:bg-gray-100 transition-all duration-200 text-left group"
>
	<span class="stock-dot {stockDotClass}"></span>

	<div class="flex-1 min-w-0">
		<p class="font-medium text-gray-800 truncate group-hover:text-gray-900">{item.product.name}</p>
		{#if item.location}
			<p class="text-xs text-gray-400 capitalize mt-0.5">{item.location}</p>
		{/if}
	</div>

	<div class="text-right flex items-center gap-2">
		<div>
			<span class="font-semibold {stockClass}">
				{item.quantity}
			</span>
			<span class="text-gray-400 text-sm ml-0.5">
				{item.product.default_unit}{item.quantity !== 1 ? 's' : ''}
			</span>
		</div>
		{#if stockLevel === 'low'}
			<span class="badge {badgeClass} text-[10px]">Low</span>
		{:else if stockLevel === 'out'}
			<span class="badge {badgeClass} text-[10px]">Out</span>
		{/if}
	</div>

	<svg class="w-4 h-4 text-gray-300 group-hover:text-gray-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
		<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
	</svg>
</button>
