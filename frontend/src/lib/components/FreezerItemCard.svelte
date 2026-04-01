<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import type { InventoryItem } from '../types';
	import { getDaysFrozen } from '../types';

	export let item: InventoryItem;

	const dispatch = createEventDispatcher<{ click: InventoryItem }>();

	$: daysFrozen = getDaysFrozen(item.frozen_date);
	$: isOld = daysFrozen !== null && daysFrozen > 90;
	$: isVeryOld = daysFrozen !== null && daysFrozen > 180;
</script>

<button
	type="button"
	on:click={() => dispatch('click', item)}
	class="w-full card-interactive text-left group {isOld ? 'border-amber-200 bg-gradient-to-br from-white to-amber-50/50' : ''}"
>
	<div class="flex items-start gap-3">
		<!-- Ice crystal icon -->
		<div class="icon-box-sm shrink-0 {isOld ? 'bg-gradient-to-br from-amber-400 to-amber-500' : 'bg-gradient-to-br from-cyan-400 to-cyan-600'} shadow-sm">
			<span class="text-white text-lg">&#10052;</span>
		</div>

		<div class="flex-1 min-w-0">
			<div class="flex items-start justify-between gap-2">
				<div class="min-w-0">
					<p class="font-semibold text-gray-800 truncate group-hover:text-gray-900">{item.product.name}</p>
					<p class="text-sm text-gray-500">
						{item.quantity} {item.product.default_unit}{item.quantity !== 1 ? 's' : ''}
					</p>
				</div>

				{#if daysFrozen !== null}
					<div class="text-right shrink-0">
						{#if isVeryOld}
							<span class="badge badge-danger">
								{daysFrozen}d
							</span>
						{:else if isOld}
							<span class="badge badge-warning">
								{daysFrozen}d
							</span>
						{:else}
							<span class="text-sm text-gray-400 font-medium">
								{daysFrozen}d
							</span>
						{/if}
					</div>
				{/if}
			</div>

			{#if item.container_description}
				<p class="text-xs text-gray-400 mt-1.5 flex items-center gap-1">
					<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
					</svg>
					{item.container_description}
				</p>
			{/if}

			<div class="flex items-center gap-2 mt-2">
				{#if item.freezer}
					<span class="text-[10px] uppercase tracking-wide text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
						{item.freezer.name}
					</span>
				{/if}
				{#if item.frozen_date}
					<span class="text-[10px] text-gray-400">
						Frozen {new Date(item.frozen_date).toLocaleDateString()}
					</span>
				{/if}
			</div>
		</div>

		<svg class="w-4 h-4 text-gray-300 group-hover:text-gray-400 transition-colors shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
		</svg>
	</div>
</button>
