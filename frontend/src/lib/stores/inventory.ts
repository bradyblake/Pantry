import { writable, derived } from 'svelte/store';
import type { InventoryItem, InventoryLog } from '../types';
import { inventoryApi } from '../api';
import { getStockLevel } from '../types';

function createInventoryStore() {
	const { subscribe, set, update } = writable<InventoryItem[]>([]);

	return {
		subscribe,
		load: async (location?: string, category?: string) => {
			const items = await inventoryApi.list({ location, category });
			set(items);
		},
		add: async (data: Parameters<typeof inventoryApi.add>[0]) => {
			const item = await inventoryApi.add(data);
			// Reload to get updated quantities
			const items = await inventoryApi.list();
			set(items);
			return item;
		},
		use: async (data: Parameters<typeof inventoryApi.use>[0]) => {
			const item = await inventoryApi.use(data);
			update(items => items.map(i => i.id === item.id ? item : i));
			return item;
		},
		updateItem: async (id: number, data: Parameters<typeof inventoryApi.update>[1]) => {
			const item = await inventoryApi.update(id, data);
			update(items => items.map(i => i.id === id ? item : i));
			return item;
		},
		remove: async (id: number) => {
			await inventoryApi.delete(id);
			update(items => items.filter(i => i.id !== id));
		},
		refresh: async () => {
			const items = await inventoryApi.list();
			set(items);
		}
	};
}

export const inventory = createInventoryStore();

// Derived store for low stock items
export const lowStockItems = derived(inventory, $inventory =>
	$inventory.filter(item => getStockLevel(item.quantity) !== 'high')
);

// Derived store for grouping by category
export const inventoryByCategory = derived(inventory, $inventory => {
	const grouped: Record<string, InventoryItem[]> = {};
	for (const item of $inventory) {
		const category = item.product.category || 'Other';
		if (!grouped[category]) {
			grouped[category] = [];
		}
		grouped[category].push(item);
	}
	// Sort categories
	const sorted: Record<string, InventoryItem[]> = {};
	for (const key of Object.keys(grouped).sort()) {
		sorted[key] = grouped[key];
	}
	return sorted;
});

// Recent activity log
function createLogStore() {
	const { subscribe, set } = writable<InventoryLog[]>([]);

	return {
		subscribe,
		load: async (productId?: number, limit: number = 50) => {
			const log = await inventoryApi.getLog({ product_id: productId, limit });
			set(log);
		}
	};
}

export const inventoryLog = createLogStore();
