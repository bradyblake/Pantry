<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { fade, fly } from 'svelte/transition';
	import { cubicOut } from 'svelte/easing';

	export let open: boolean = false;
	export let title: string = '';

	const dispatch = createEventDispatcher<{ close: void }>();

	function handleBackdropClick() {
		dispatch('close');
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			dispatch('close');
		}
	}
</script>

<svelte:window on:keydown={handleKeydown} />

{#if open}
	<div class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 sm:p-6">
		<!-- Backdrop -->
		<div
			class="absolute inset-0 bg-black/40 backdrop-blur-sm"
			on:click={handleBackdropClick}
			on:keypress={handleBackdropClick}
			role="button"
			tabindex="-1"
			transition:fade={{ duration: 200 }}
		></div>

		<!-- Modal content -->
		<div
			class="relative bg-white w-full max-w-lg max-h-[85vh] overflow-auto rounded-2xl shadow-2xl border border-gray-100"
			transition:fly={{ y: 50, duration: 300, easing: cubicOut }}
		>
			<!-- Handle bar for mobile -->
			<div class="sm:hidden flex justify-center pt-3 pb-1">
				<div class="w-10 h-1 bg-gray-300 rounded-full"></div>
			</div>

			{#if title}
				<div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
					<h2 class="text-lg font-bold text-gray-800">{title}</h2>
					<button
						type="button"
						on:click={() => dispatch('close')}
						class="p-2 -mr-2 rounded-xl hover:bg-gray-100 active:bg-gray-200 transition-colors"
					>
						<svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
						</svg>
					</button>
				</div>
			{/if}

			<div class="p-5">
				<slot />
			</div>
		</div>
	</div>
{/if}
