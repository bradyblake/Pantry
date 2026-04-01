import { writable, derived, get } from 'svelte/store';
import type { Freezer, InventoryItem } from '../types';
import { freezersApi } from '../api';

function createFreezersStore() {
	const { subscribe, set, update } = writable<Freezer[]>([]);

	return {
		subscribe,
		load: async () => {
			const freezers = await freezersApi.list();
			set(freezers);
			return freezers;
		},
		add: async (data: Parameters<typeof freezersApi.create>[0]) => {
			const freezer = await freezersApi.create(data);
			update(freezers => [...freezers, freezer]);
			return freezer;
		},
		update: async (id: number, data: Parameters<typeof freezersApi.update>[1]) => {
			const updated = await freezersApi.update(id, data);
			update(freezers => freezers.map(f => f.id === id ? updated : f));
			return updated;
		},
		remove: async (id: number) => {
			await freezersApi.delete(id);
			update(freezers => freezers.filter(f => f.id !== id));
		}
	};
}

export const freezers = createFreezersStore();

// Currently selected freezer
export const selectedFreezerId = writable<number | null>(null);

// Contents of the selected freezer
function createFreezerContentsStore() {
	const { subscribe, set } = writable<InventoryItem[]>([]);

	return {
		subscribe,
		load: async (freezerId: number, category?: string) => {
			const contents = await freezersApi.getContents(freezerId, category);
			set(contents);
			return contents;
		},
		clear: () => set([])
	};
}

export const freezerContents = createFreezerContentsStore();

// Oldest items across all freezers
function createOldestItemsStore() {
	const { subscribe, set } = writable<InventoryItem[]>([]);

	return {
		subscribe,
		load: async (freezerId?: number, days: number = 90, limit: number = 10) => {
			const items = await freezersApi.getOldest({ freezer_id: freezerId, days, limit });
			set(items);
			return items;
		}
	};
}

export const oldestFrozenItems = createOldestItemsStore();

// Derived: group freezer contents by category
export const freezerContentsByCategory = derived(freezerContents, $contents => {
	const grouped: Record<string, InventoryItem[]> = {};
	for (const item of $contents) {
		const category = item.product.category || 'Other';
		if (!grouped[category]) {
			grouped[category] = [];
		}
		grouped[category].push(item);
	}
	return grouped;
});
