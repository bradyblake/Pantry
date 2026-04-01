<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let value: string = '';
	export let placeholder: string = 'Search...';
	export let autofocus: boolean = false;

	const dispatch = createEventDispatcher<{ search: string; clear: void }>();

	let focused = false;

	function handleInput(e: Event) {
		const target = e.target as HTMLInputElement;
		value = target.value;
		dispatch('search', value);
	}

	function handleClear() {
		value = '';
		dispatch('clear');
		dispatch('search', '');
	}
</script>

<div class="relative group">
	<div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none transition-colors duration-200"
		class:text-primary-500={focused}
		class:text-gray-400={!focused}>
		<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
		</svg>
	</div>
	<input
		type="text"
		{value}
		{placeholder}
		autofocus={autofocus}
		on:input={handleInput}
		on:focus={() => focused = true}
		on:blur={() => focused = false}
		class="input pl-12 pr-12 bg-white/80 backdrop-blur-sm shadow-sm hover:shadow transition-shadow duration-200"
	/>
	{#if value}
		<button
			type="button"
			on:click={handleClear}
			class="absolute inset-y-0 right-0 pr-4 flex items-center group/clear"
		>
			<div class="p-1 rounded-full bg-gray-100 group-hover/clear:bg-gray-200 transition-colors">
				<svg class="w-3.5 h-3.5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
				</svg>
			</div>
		</button>
	{/if}
</div>
