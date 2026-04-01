<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let value: number = 1;
	export let min: number = 0;
	export let max: number = 999;
	export let step: number = 1;
	export let unit: string = '';

	const dispatch = createEventDispatcher<{ change: number }>();

	function decrease() {
		if (value > min) {
			value = Math.max(min, value - step);
			dispatch('change', value);
		}
	}

	function increase() {
		if (value < max) {
			value = Math.min(max, value + step);
			dispatch('change', value);
		}
	}

	function handleInput(e: Event) {
		const target = e.target as HTMLInputElement;
		const newValue = parseFloat(target.value);
		if (!isNaN(newValue)) {
			value = Math.max(min, Math.min(max, newValue));
			dispatch('change', value);
		}
	}
</script>

<div class="flex items-center justify-center gap-3">
	<button
		type="button"
		on:click={decrease}
		disabled={value <= min}
		class="w-14 h-14 rounded-2xl bg-gradient-to-br from-gray-100 to-gray-200 hover:from-gray-200 hover:to-gray-300 active:from-gray-300 active:to-gray-400 disabled:opacity-40 disabled:hover:from-gray-100 disabled:hover:to-gray-200 flex items-center justify-center shadow-sm hover:shadow transition-all duration-200 active:scale-95"
	>
		<svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M20 12H4" />
		</svg>
	</button>

	<div class="flex items-center gap-2 bg-white rounded-2xl border border-gray-200 px-4 py-2 shadow-sm min-w-[120px] justify-center">
		<input
			type="number"
			{value}
			{min}
			{max}
			{step}
			on:input={handleInput}
			class="w-14 text-center text-2xl font-bold text-gray-800 bg-transparent focus:outline-none"
		/>
		{#if unit}
			<span class="text-gray-400 text-sm font-medium">{unit}</span>
		{/if}
	</div>

	<button
		type="button"
		on:click={increase}
		disabled={value >= max}
		class="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-400 to-primary-600 hover:from-primary-500 hover:to-primary-700 active:from-primary-600 active:to-primary-800 disabled:opacity-40 disabled:hover:from-primary-400 disabled:hover:to-primary-600 flex items-center justify-center shadow-md hover:shadow-lg shadow-primary-500/25 transition-all duration-200 active:scale-95"
	>
		<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
		</svg>
	</button>
</div>
