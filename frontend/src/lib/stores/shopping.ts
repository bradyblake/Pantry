import { writable, derived } from 'svelte/store';
import type { ShoppingItem } from '../types';
import { shoppingApi } from '../api';

function createShoppingStore() {
	const { subscribe, set, update } = writable<ShoppingItem[]>([]);

	return {
		subscribe,
		load: async () => {
			const items = await shoppingApi.list();
			set(items);
		},
		add: async (data: Parameters<typeof shoppingApi.create>[0]) => {
			const item = await shoppingApi.create(data);
			update(items => [item, ...items]);
			return item;
		},
		update: async (id: number, data: Parameters<typeof shoppingApi.update>[1]) => {
			const updated = await shoppingApi.update(id, data);
			update(items => items.map(i => i.id === id ? updated : i));
			return updated;
		},
		toggle: async (id: number) => {
			const items = await shoppingApi.list();
			const item = items.find(i => i.id === id);
			if (item) {
				const updated = await shoppingApi.update(id, { checked: !item.checked });
				update(items => items.map(i => i.id === id ? updated : i));
				return updated;
			}
		},
		remove: async (id: number) => {
			await shoppingApi.delete(id);
			update(items => items.filter(i => i.id !== id));
		},
		clearChecked: async () => {
			await shoppingApi.clearChecked();
			update(items => items.filter(i => !i.checked));
		},
		generateFromLowStock: async () => {
			const newItems = await shoppingApi.generateFromLowStock();
			if (newItems.length > 0) {
				// Reload to get complete list
				const items = await shoppingApi.list();
				set(items);
			}
			return newItems;
		}
	};
}

export const shopping = createShoppingStore();

// Derived: unchecked items
export const uncheckedItems = derived(shopping, $shopping =>
	$shopping.filter(item => !item.checked)
);

// Derived: checked items
export const checkedItems = derived(shopping, $shopping =>
	$shopping.filter(item => item.checked)
);

// Derived: count of unchecked items
export const uncheckedCount = derived(uncheckedItems, $items => $items.length);
