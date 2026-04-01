import { writable, derived } from 'svelte/store';
import type { Product } from '../types';
import { productsApi } from '../api';

function createProductsStore() {
	const { subscribe, set, update } = writable<Product[]>([]);

	return {
		subscribe,
		load: async () => {
			const products = await productsApi.list();
			set(products);
		},
		search: async (query: string, category?: string) => {
			const products = await productsApi.list({ search: query, category });
			set(products);
		},
		add: async (product: Parameters<typeof productsApi.create>[0]) => {
			const newProduct = await productsApi.create(product);
			update(products => [...products, newProduct]);
			return newProduct;
		},
		update: async (id: number, data: Parameters<typeof productsApi.update>[1]) => {
			const updated = await productsApi.update(id, data);
			update(products => products.map(p => p.id === id ? updated : p));
			return updated;
		},
		remove: async (id: number) => {
			await productsApi.delete(id);
			update(products => products.filter(p => p.id !== id));
		}
	};
}

export const products = createProductsStore();

// Categories store
function createCategoriesStore() {
	const { subscribe, set } = writable<string[]>([]);

	return {
		subscribe,
		load: async () => {
			const categories = await productsApi.getCategories();
			set(categories);
		}
	};
}

export const categories = createCategoriesStore();
