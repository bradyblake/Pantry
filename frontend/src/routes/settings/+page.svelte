<script lang="ts">
	import { onMount } from 'svelte';
	import { Header, Modal } from '$lib/components';
	import { freezers } from '$lib/stores';
	import { zonesApi, rfidApi } from '$lib/api';
	import type { Freezer, Zone, RfidTag } from '$lib/types';

	// Tab state
	let activeTab: 'freezers' | 'zones' | 'rfid' = 'freezers';

	// Freezer state
	let showFreezerModal = false;
	let editingFreezer: Freezer | null = null;
	let freezerName = '';
	let freezerLocation = '';
	let freezerDescription = '';

	// Zone state
	let zones: Zone[] = [];
	let loadingZones = true;
	let showZoneModal = false;
	let editingZone: Zone | null = null;
	let zoneName = '';
	let zoneLocation = '';
	let zoneType = 'shelf';
	let zoneEsp32Id = '';
	let zoneRfidAntenna: number | null = null;

	// RFID state
	let rfidTags: RfidTag[] = [];
	let loadingTags = true;

	onMount(function() {
		freezers.load();
		loadZones();
		loadTags();
	});

	async function loadZones() {
		loadingZones = true;
		try {
			zones = await zonesApi.list();
		} catch (e) {
			console.error('Failed to load zones:', e);
		} finally {
			loadingZones = false;
		}
	}

	async function loadTags() {
		loadingTags = true;
		try {
			rfidTags = await rfidApi.listTags();
		} catch (e) {
			console.error('Failed to load RFID tags:', e);
		} finally {
			loadingTags = false;
		}
	}

	// Freezer functions
	function openAddFreezer() {
		editingFreezer = null;
		freezerName = '';
		freezerLocation = '';
		freezerDescription = '';
		showFreezerModal = true;
	}

	function openEditFreezer(freezer: Freezer) {
		editingFreezer = freezer;
		freezerName = freezer.name;
		freezerLocation = freezer.location || '';
		freezerDescription = freezer.description || '';
		showFreezerModal = true;
	}

	async function saveFreezer() {
		if (!freezerName.trim()) return;
		try {
			if (editingFreezer) {
				await freezers.update(editingFreezer.id, {
					name: freezerName.trim(),
					location: freezerLocation.trim() || null,
					description: freezerDescription.trim() || null
				});
			} else {
				await freezers.add({
					name: freezerName.trim(),
					location: freezerLocation.trim() || null,
					description: freezerDescription.trim() || null
				});
			}
			showFreezerModal = false;
		} catch (e) {
			console.error('Failed to save freezer:', e);
		}
	}

	async function deleteFreezer() {
		if (editingFreezer && confirm('Delete "' + editingFreezer.name + '"? This cannot be undone.')) {
			try {
				await freezers.remove(editingFreezer.id);
				showFreezerModal = false;
			} catch (e: any) {
				alert(e.message || 'Failed to delete freezer');
			}
		}
	}

	// Zone functions
	function openAddZone() {
		editingZone = null;
		zoneName = '';
		zoneLocation = '';
		zoneType = 'shelf';
		zoneEsp32Id = '';
		zoneRfidAntenna = null;
		showZoneModal = true;
	}

	function openEditZone(zone: Zone) {
		editingZone = zone;
		zoneName = zone.name;
		zoneLocation = zone.location || '';
		zoneType = zone.zone_type;
		zoneEsp32Id = zone.esp32_id || '';
		zoneRfidAntenna = zone.rfid_antenna_id;
		showZoneModal = true;
	}

	async function saveZone() {
		if (!zoneName.trim()) return;
		try {
			if (editingZone) {
				await zonesApi.update(editingZone.id, {
					name: zoneName.trim(),
					location: zoneLocation.trim() || null,
					zone_type: zoneType,
					esp32_id: zoneEsp32Id.trim() || null,
					rfid_antenna_id: zoneRfidAntenna
				});
			} else {
				await zonesApi.create({
					name: zoneName.trim(),
					location: zoneLocation.trim() || null,
					zone_type: zoneType,
					esp32_id: zoneEsp32Id.trim() || null,
					rfid_antenna_id: zoneRfidAntenna
				});
			}
			showZoneModal = false;
			loadZones();
		} catch (e) {
			console.error('Failed to save zone:', e);
		}
	}

	async function deleteZone() {
		if (editingZone && confirm('Delete zone "' + editingZone.name + '"?')) {
			try {
				await zonesApi.delete(editingZone.id);
				showZoneModal = false;
				loadZones();
			} catch (e: any) {
				alert(e.message || 'Failed to delete zone');
			}
		}
	}

	async function testZoneLed(zone: Zone) {
		try {
			await zonesApi.setLed(zone.id, { state: 'highlight', duration_ms: 3000 });
			setTimeout(function() {
				zonesApi.setLed(zone.id, { state: 'idle' });
			}, 3000);
		} catch (e) {
			console.error('Failed to test LED:', e);
		}
	}

	function getZoneTypeLabel(type: string): string {
		var labels: { [key: string]: string } = {
			'shelf': 'Shelf',
			'bulk': 'Bulk Storage',
			'spice': 'Spice Tower',
			'pouch': 'Pouch Bin',
			'can_lane': 'Can Lane'
		};
		return labels[type] || type;
	}

	function getLedStateColor(state: string): string {
		var colors: { [key: string]: string } = {
			'off': 'bg-gray-200',
			'idle': 'bg-gray-300',
			'scanning': 'bg-red-500',
			'confirm': 'bg-yellow-500',
			'success': 'bg-green-500',
			'return': 'bg-blue-500',
			'highlight': 'bg-white border border-gray-300'
		};
		return colors[state] || 'bg-gray-200';
	}
</script>

<Header title="Settings" showBack backHref="/" />

<main class="flex-1 p-4 space-y-4">
	<!-- Tabs -->
	<div class="flex gap-2 border-b border-gray-200 pb-2">
		<button
			type="button"
			class="px-4 py-2 text-sm font-medium rounded-t {activeTab === 'freezers' ? 'bg-primary text-white' : 'text-gray-600'}"
			on:click={function() { activeTab = 'freezers'; }}
		>
			Freezers
		</button>
		<button
			type="button"
			class="px-4 py-2 text-sm font-medium rounded-t {activeTab === 'zones' ? 'bg-primary text-white' : 'text-gray-600'}"
			on:click={function() { activeTab = 'zones'; }}
		>
			Zones
		</button>
		<button
			type="button"
			class="px-4 py-2 text-sm font-medium rounded-t {activeTab === 'rfid' ? 'bg-primary text-white' : 'text-gray-600'}"
			on:click={function() { activeTab = 'rfid'; }}
		>
			RFID Tags
		</button>
	</div>

	<!-- Freezers Tab -->
	{#if activeTab === 'freezers'}
		<section>
			<div class="flex items-center justify-between mb-3">
				<h2 class="text-lg font-semibold">Freezers</h2>
				<button class="btn btn-secondary text-sm" on:click={openAddFreezer}>
					+ Add
				</button>
			</div>

			{#if $freezers.length > 0}
				<div class="card p-0 divide-y divide-gray-100">
					{#each $freezers as freezer}
						<button
							type="button"
							class="w-full p-4 text-left hover:bg-gray-50 flex items-center justify-between"
							on:click={function() { openEditFreezer(freezer); }}
						>
							<div>
								<p class="font-medium text-gray-900">{freezer.name}</p>
								{#if freezer.location}
									<p class="text-sm text-gray-500">{freezer.location}</p>
								{/if}
							</div>
							<span class="text-gray-400">&rarr;</span>
						</button>
					{/each}
				</div>
			{:else}
				<p class="text-gray-500 text-center py-4">No freezers configured</p>
			{/if}
		</section>
	{/if}

	<!-- Zones Tab -->
	{#if activeTab === 'zones'}
		<section>
			<div class="flex items-center justify-between mb-3">
				<h2 class="text-lg font-semibold">Pantry Zones</h2>
				<button class="btn btn-secondary text-sm" on:click={openAddZone}>
					+ Add
				</button>
			</div>

			{#if loadingZones}
				<p class="text-gray-500 text-center py-4">Loading...</p>
			{:else if zones.length > 0}
				<div class="space-y-2">
					{#each zones as zone}
						<div class="card p-3 flex items-center gap-3">
							<div class="w-3 h-3 rounded-full {getLedStateColor(zone.current_led_state)}"></div>
							<div class="flex-1 min-w-0">
								<p class="font-medium text-sm truncate">{zone.name}</p>
								<p class="text-xs text-gray-500">
									{getZoneTypeLabel(zone.zone_type)}
									{#if zone.rfid_antenna_id}
										&bull; RFID
									{/if}
								</p>
							</div>
							<button
								type="button"
								class="text-xs px-2 py-1 bg-gray-100 rounded"
								on:click={function() { testZoneLed(zone); }}
							>
								Test
							</button>
							<button
								type="button"
								class="text-gray-400"
								on:click={function() { openEditZone(zone); }}
							>
								Edit
							</button>
						</div>
					{/each}
				</div>
			{:else}
				<p class="text-gray-500 text-center py-4">No zones configured</p>
			{/if}
		</section>
	{/if}

	<!-- RFID Tags Tab -->
	{#if activeTab === 'rfid'}
		<section>
			<div class="flex items-center justify-between mb-3">
				<h2 class="text-lg font-semibold">RFID Tags</h2>
				<span class="text-sm text-gray-500">{rfidTags.length} tags</span>
			</div>

			{#if loadingTags}
				<p class="text-gray-500 text-center py-4">Loading...</p>
			{:else if rfidTags.length > 0}
				<div class="space-y-2">
					{#each rfidTags as tag}
						<div class="card p-3 flex items-center gap-3">
							<div class="w-8 h-8 rounded-full flex items-center justify-center {tag.is_out ? 'bg-red-100 text-red-600' : 'bg-green-100 text-green-600'}">
								{tag.is_out ? '!' : '✓'}
							</div>
							<div class="flex-1 min-w-0">
								<p class="font-medium text-sm truncate">
									{tag.product ? tag.product.name : tag.container_name || 'Unknown'}
								</p>
								<p class="text-xs text-gray-500 truncate">
									{tag.tag_id}
								</p>
							</div>
							{#if tag.home_zone}
								<span class="text-xs text-gray-400">{tag.home_zone.name}</span>
							{/if}
						</div>
					{/each}
				</div>
			{:else}
				<p class="text-gray-500 text-center py-4">No RFID tags registered</p>
			{/if}
		</section>
	{/if}

	<!-- App Info -->
	<section class="pt-4 border-t border-gray-200">
		<h2 class="text-lg font-semibold mb-3">About</h2>
		<div class="card">
			<p class="font-medium">PantryPal</p>
			<p class="text-sm text-gray-500">Smart Pantry Inventory System</p>
			<p class="text-sm text-gray-500 mt-2">Version 1.0 - Phase 1</p>
		</div>
	</section>
</main>

<!-- Freezer Modal -->
{#if showFreezerModal}
	<Modal title={editingFreezer ? 'Edit Freezer' : 'Add Freezer'} onClose={function() { showFreezerModal = false; }}>
		<div class="p-4 space-y-4">
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1">Name *</label>
				<input type="text" bind:value={freezerName} class="input w-full" placeholder="e.g., Main Freezer" />
			</div>
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1">Location</label>
				<input type="text" bind:value={freezerLocation} class="input w-full" placeholder="e.g., Kitchen" />
			</div>
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
				<input type="text" bind:value={freezerDescription} class="input w-full" placeholder="Optional notes" />
			</div>
			<div class="flex gap-3 pt-2">
				{#if editingFreezer}
					<button class="btn bg-red-100 text-red-700" on:click={deleteFreezer}>Delete</button>
				{/if}
				<button class="btn btn-primary flex-1" on:click={saveFreezer} disabled={!freezerName.trim()}>
					{editingFreezer ? 'Save' : 'Add'}
				</button>
			</div>
		</div>
	</Modal>
{/if}

<!-- Zone Modal -->
{#if showZoneModal}
	<Modal title={editingZone ? 'Edit Zone' : 'Add Zone'} onClose={function() { showZoneModal = false; }}>
		<div class="p-4 space-y-4">
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1">Name *</label>
				<input type="text" bind:value={zoneName} class="input w-full" placeholder="e.g., V1 Shelf 1" />
			</div>
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1">Location</label>
				<input type="text" bind:value={zoneLocation} class="input w-full" placeholder="e.g., V1 Shelf 1" />
			</div>
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1">Type</label>
				<select bind:value={zoneType} class="input w-full">
					<option value="shelf">Shelf</option>
					<option value="bulk">Bulk Storage</option>
					<option value="spice">Spice Tower</option>
					<option value="pouch">Pouch Bin</option>
					<option value="can_lane">Can Lane</option>
				</select>
			</div>
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1">ESP32 ID</label>
				<input type="text" bind:value={zoneEsp32Id} class="input w-full" placeholder="e.g., esp32_v1_1" />
			</div>
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1">RFID Antenna #</label>
				<input type="number" bind:value={zoneRfidAntenna} class="input w-full" placeholder="Leave empty if none" />
			</div>
			<div class="flex gap-3 pt-2">
				{#if editingZone}
					<button class="btn bg-red-100 text-red-700" on:click={deleteZone}>Delete</button>
				{/if}
				<button class="btn btn-primary flex-1" on:click={saveZone} disabled={!zoneName.trim()}>
					{editingZone ? 'Save' : 'Add'}
				</button>
			</div>
		</div>
	</Modal>
{/if}
