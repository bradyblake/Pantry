<script lang="ts">
	import type { PutItBackAlert } from '$lib/types';
	import { rfidApi, zonesApi } from '$lib/api';

	export let alert: PutItBackAlert;
	export let onAcknowledge: () => void = function() {};

	let guiding = false;
	let acknowledging = false;

	async function handleGuide() {
		guiding = true;
		try {
			await rfidApi.guideReturn(alert.tag_id);
		} catch (e) {
			console.error('Failed to guide return:', e);
		} finally {
			guiding = false;
		}
	}

	async function handleAcknowledge() {
		acknowledging = true;
		try {
			await rfidApi.acknowledgeReturn(alert.tag_id);
			await zonesApi.allLedsOff();
			onAcknowledge();
		} catch (e) {
			console.error('Failed to acknowledge:', e);
		} finally {
			acknowledging = false;
		}
	}

	function formatTime(minutes: number): string {
		if (minutes < 1) return 'just now';
		if (minutes < 60) return minutes + ' min ago';
		var hours = Math.floor(minutes / 60);
		return hours + ' hr ago';
	}
</script>

<div class="card border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50 animate-fade-in">
	<div class="flex items-start gap-3">
		<div class="icon-box-sm bg-gradient-to-br from-blue-400 to-blue-600 shadow-sm shrink-0">
			<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
			</svg>
		</div>
		<div class="flex-1 min-w-0">
			<p class="font-semibold text-blue-900 truncate">
				{alert.product_name || alert.container_name || 'Unknown item'}
			</p>
			<p class="text-sm text-blue-700 mt-0.5">
				Return to <span class="font-medium">{alert.home_zone_name}</span>
				{#if alert.home_zone_location}
					<span class="text-blue-500">&#8226; {alert.home_zone_location}</span>
				{/if}
			</p>
			<p class="text-xs text-blue-400 mt-1 flex items-center gap-1">
				<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>
				{formatTime(alert.minutes_out)}
			</p>
		</div>
		<div class="flex gap-2 shrink-0">
			<button
				type="button"
				class="p-2.5 bg-white border border-blue-200 rounded-xl hover:bg-blue-50 hover:border-blue-300 disabled:opacity-50 transition-colors shadow-sm"
				disabled={guiding}
				on:click={handleGuide}
				title="Light up zone"
			>
				{#if guiding}
					<svg class="w-5 h-5 text-blue-500 animate-spin" fill="none" viewBox="0 0 24 24">
						<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
						<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
					</svg>
				{:else}
					<svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
					</svg>
				{/if}
			</button>
			<button
				type="button"
				class="p-2.5 bg-gradient-to-br from-green-400 to-green-600 rounded-xl hover:from-green-500 hover:to-green-700 disabled:opacity-50 transition-all shadow-md shadow-green-500/25"
				disabled={acknowledging}
				on:click={handleAcknowledge}
				title="Mark as returned"
			>
				{#if acknowledging}
					<svg class="w-5 h-5 text-white animate-spin" fill="none" viewBox="0 0 24 24">
						<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
						<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
					</svg>
				{:else}
					<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
					</svg>
				{/if}
			</button>
		</div>
	</div>
</div>
