import type {
	Product, ProductCreate, ProductUpdate,
	Freezer, FreezerCreate, FreezerUpdate,
	InventoryItem, InventoryAdd, InventoryUse, InventoryUpdate, InventoryLog,
	ShoppingItem, ShoppingItemCreate, ShoppingItemUpdate,
	Recipe, RecipeCreate, RecipeUpdate, RecipeSuggestion, RecipeDocument, RecipeIngredientCreate,
	Zone, ZoneCreate, LedCommand, RfidTag, RfidTagCreate, PutItBackAlert, FindIngredientsResponse
} from './types';

const API_BASE = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : '');

async function fetchApi<T>(
	endpoint: string,
	options: RequestInit = {}
): Promise<T> {
	const url = `${API_BASE}${endpoint}`;
	const response = await fetch(url, {
		...options,
		headers: {
			'Content-Type': 'application/json',
			...options.headers
		}
	});

	if (!response.ok) {
		const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
		throw new Error(error.detail || `HTTP ${response.status}`);
	}

	// Handle 204 No Content
	if (response.status === 204) {
		return undefined as T;
	}

	return response.json();
}

// Products API
export const productsApi = {
	list: (params?: { search?: string; category?: string }) => {
		const searchParams = new URLSearchParams();
		if (params?.search) searchParams.set('search', params.search);
		if (params?.category) searchParams.set('category', params.category);
		const query = searchParams.toString();
		return fetchApi<Product[]>(`/api/products${query ? `?${query}` : ''}`);
	},

	get: (id: number) => fetchApi<Product>(`/api/products/${id}`),

	getByBarcode: (barcode: string) => fetchApi<Product>(`/api/products/barcode/${barcode}`),

	create: (data: ProductCreate) =>
		fetchApi<Product>('/api/products', {
			method: 'POST',
			body: JSON.stringify(data)
		}),

	update: (id: number, data: ProductUpdate) =>
		fetchApi<Product>(`/api/products/${id}`, {
			method: 'PUT',
			body: JSON.stringify(data)
		}),

	delete: (id: number) =>
		fetchApi<void>(`/api/products/${id}`, { method: 'DELETE' }),

	getCategories: () => fetchApi<string[]>('/api/products/categories')
};

// Freezers API
export const freezersApi = {
	list: () => fetchApi<Freezer[]>('/api/freezers'),

	get: (id: number) => fetchApi<Freezer>(`/api/freezers/${id}`),

	getContents: (id: number, category?: string) => {
		const params = category ? `?category=${encodeURIComponent(category)}` : '';
		return fetchApi<InventoryItem[]>(`/api/freezers/${id}/contents${params}`);
	},

	getOldest: (params?: { freezer_id?: number; days?: number; limit?: number }) => {
		const searchParams = new URLSearchParams();
		if (params?.freezer_id) searchParams.set('freezer_id', params.freezer_id.toString());
		if (params?.days) searchParams.set('days', params.days.toString());
		if (params?.limit) searchParams.set('limit', params.limit.toString());
		const query = searchParams.toString();
		return fetchApi<InventoryItem[]>(`/api/freezers/oldest${query ? `?${query}` : ''}`);
	},

	create: (data: FreezerCreate) =>
		fetchApi<Freezer>('/api/freezers', {
			method: 'POST',
			body: JSON.stringify(data)
		}),

	update: (id: number, data: FreezerUpdate) =>
		fetchApi<Freezer>(`/api/freezers/${id}`, {
			method: 'PUT',
			body: JSON.stringify(data)
		}),

	delete: (id: number) =>
		fetchApi<void>(`/api/freezers/${id}`, { method: 'DELETE' })
};

// Inventory API
export const inventoryApi = {
	list: (params?: { location?: string; category?: string }) => {
		const searchParams = new URLSearchParams();
		if (params?.location) searchParams.set('location', params.location);
		if (params?.category) searchParams.set('category', params.category);
		const query = searchParams.toString();
		return fetchApi<InventoryItem[]>(`/api/inventory${query ? `?${query}` : ''}`);
	},

	getLowStock: (threshold?: number) => {
		const params = threshold ? `?threshold=${threshold}` : '';
		return fetchApi<InventoryItem[]>(`/api/inventory/low-stock${params}`);
	},

	getForProduct: (productId: number) =>
		fetchApi<InventoryItem[]>(`/api/inventory/product/${productId}`),

	getLog: (params?: { product_id?: number; source?: string; limit?: number; offset?: number }) => {
		const searchParams = new URLSearchParams();
		if (params?.product_id) searchParams.set('product_id', params.product_id.toString());
		if (params?.source) searchParams.set('source', params.source);
		if (params?.limit) searchParams.set('limit', params.limit.toString());
		if (params?.offset) searchParams.set('offset', params.offset.toString());
		const query = searchParams.toString();
		return fetchApi<InventoryLog[]>(`/api/inventory/log${query ? `?${query}` : ''}`);
	},

	add: (data: InventoryAdd) =>
		fetchApi<InventoryItem>('/api/inventory/add', {
			method: 'POST',
			body: JSON.stringify(data)
		}),

	use: (data: InventoryUse) =>
		fetchApi<InventoryItem>('/api/inventory/use', {
			method: 'POST',
			body: JSON.stringify(data)
		}),

	update: (id: number, data: InventoryUpdate) =>
		fetchApi<InventoryItem>(`/api/inventory/${id}`, {
			method: 'PUT',
			body: JSON.stringify(data)
		}),

	delete: (id: number) =>
		fetchApi<void>(`/api/inventory/${id}`, { method: 'DELETE' })
};

// Shopping API
export const shoppingApi = {
	list: (checked?: boolean) => {
		const params = checked !== undefined ? `?checked=${checked}` : '';
		return fetchApi<ShoppingItem[]>(`/api/shopping${params}`);
	},

	get: (id: number) => fetchApi<ShoppingItem>(`/api/shopping/${id}`),

	create: (data: ShoppingItemCreate) =>
		fetchApi<ShoppingItem>('/api/shopping', {
			method: 'POST',
			body: JSON.stringify(data)
		}),

	update: (id: number, data: ShoppingItemUpdate) =>
		fetchApi<ShoppingItem>(`/api/shopping/${id}`, {
			method: 'PUT',
			body: JSON.stringify(data)
		}),

	delete: (id: number) =>
		fetchApi<void>(`/api/shopping/${id}`, { method: 'DELETE' }),

	clearChecked: () =>
		fetchApi<void>('/api/shopping/clear-checked', { method: 'DELETE' }),

	generateFromLowStock: (threshold?: number) => {
		const params = threshold ? `?threshold=${threshold}` : '';
		return fetchApi<ShoppingItem[]>(`/api/shopping/generate-from-low-stock${params}`, {
			method: 'POST'
		});
	}
};

// System API
export const systemApi = {
	health: () => fetchApi<{ status: string; version: string }>('/api/health'),
	getDefaultCategories: () => fetchApi<string[]>('/api/categories')
};

// Recipes API
export const recipesApi = {
	list: (params?: { search?: string; tags?: string; limit?: number; offset?: number }) => {
		const searchParams = new URLSearchParams();
		if (params && params.search) searchParams.set('search', params.search);
		if (params && params.tags) searchParams.set('tags', params.tags);
		if (params && params.limit) searchParams.set('limit', params.limit.toString());
		if (params && params.offset) searchParams.set('offset', params.offset.toString());
		const query = searchParams.toString();
		return fetchApi<Recipe[]>('/api/recipes/' + (query ? '?' + query : ''));
	},

	get: (id: number) => fetchApi<Recipe>('/api/recipes/' + id),

	create: (data: RecipeCreate) =>
		fetchApi<Recipe>('/api/recipes/', {
			method: 'POST',
			body: JSON.stringify(data)
		}),

	update: (id: number, data: RecipeUpdate) =>
		fetchApi<Recipe>('/api/recipes/' + id, {
			method: 'PUT',
			body: JSON.stringify(data)
		}),

	delete: (id: number) =>
		fetchApi<void>('/api/recipes/' + id, { method: 'DELETE' }),

	getSuggestions: (limit?: number) => {
		const params = limit ? '?limit=' + limit : '';
		return fetchApi<RecipeSuggestion[]>('/api/recipes/suggestions' + params);
	},

	addIngredient: (recipeId: number, ingredient: RecipeIngredientCreate) =>
		fetchApi<Recipe>('/api/recipes/' + recipeId + '/ingredients', {
			method: 'POST',
			body: JSON.stringify(ingredient)
		}),

	removeIngredient: (recipeId: number, ingredientId: number) =>
		fetchApi<void>('/api/recipes/' + recipeId + '/ingredients/' + ingredientId, {
			method: 'DELETE'
		}),

	make: (recipeId: number, servings?: number) => {
		const params = servings ? '?servings=' + servings : '';
		return fetchApi<{ status: string; recipe: string; decremented: object[]; skipped: string[] }>(
			'/api/recipes/' + recipeId + '/make' + params,
			{ method: 'POST' }
		);
	},

	importFromUrl: (url: string) =>
		fetchApi<Recipe[]>('/api/recipes/import-url', {
			method: 'POST',
			body: JSON.stringify({ url })
		}),

	// Document/PDF operations
	uploadDocument: async (file: File) => {
		const formData = new FormData();
		formData.append('file', file);

		const url = (import.meta.env.DEV ? 'http://localhost:8000' : '') + '/api/recipes/upload-pdf';
		const response = await fetch(url, {
			method: 'POST',
			body: formData
		});

		if (!response.ok) {
			const error = await response.json().catch(function() { return { detail: 'Upload failed' }; });
			throw new Error(error.detail || 'HTTP ' + response.status);
		}

		return response.json() as Promise<RecipeDocument>;
	},

	parseDocument: (documentId: number, useVision?: boolean) => {
		const params = useVision !== undefined ? '?use_vision=' + useVision : '';
		return fetchApi<Recipe[]>('/api/recipes/documents/' + documentId + '/parse' + params, {
			method: 'POST'
		});
	},

	listDocuments: (parsed?: boolean) => {
		const params = parsed !== undefined ? '?parsed=' + parsed : '';
		return fetchApi<RecipeDocument[]>('/api/recipes/documents' + params);
	},

	deleteDocument: (documentId: number) =>
		fetchApi<void>('/api/recipes/documents/' + documentId, { method: 'DELETE' })
};

// Zones API
export const zonesApi = {
	list: () => fetchApi<Zone[]>('/api/zones/'),

	get: (id: number) => fetchApi<Zone>('/api/zones/' + id),

	create: (data: ZoneCreate) =>
		fetchApi<Zone>('/api/zones/', {
			method: 'POST',
			body: JSON.stringify(data)
		}),

	update: (id: number, data: Partial<ZoneCreate>) =>
		fetchApi<Zone>('/api/zones/' + id, {
			method: 'PUT',
			body: JSON.stringify(data)
		}),

	delete: (id: number) =>
		fetchApi<void>('/api/zones/' + id, { method: 'DELETE' }),

	setLed: (id: number, command: LedCommand) =>
		fetchApi<{ zone_id: number; state: string; color: string }>('/api/zones/' + id + '/led', {
			method: 'POST',
			body: JSON.stringify(command)
		}),

	allLedsOff: () =>
		fetchApi<{ status: string; zones_updated: number }>('/api/zones/led/all-off', {
			method: 'POST'
		}),

	findIngredients: (recipeId: number, lightZones?: boolean) => {
		var params = lightZones !== undefined ? '?light_zones=' + lightZones : '';
		return fetchApi<FindIngredientsResponse>('/api/zones/find-ingredients/' + recipeId + params, {
			method: 'POST'
		});
	},

	findProducts: (productIds: number[], lightZones?: boolean) =>
		fetchApi<{ products: Array<{ product_id: number; product_name: string; zone_id: number; zone_name: string }>; zones_lit: number[] }>(
			'/api/zones/find-products' + (lightZones !== undefined ? '?light_zones=' + lightZones : ''),
			{
				method: 'POST',
				body: JSON.stringify(productIds)
			}
		)
};

// RFID API
export const rfidApi = {
	listTags: (params?: { is_out?: boolean; zone_id?: number }) => {
		var searchParams = new URLSearchParams();
		if (params && params.is_out !== undefined) searchParams.set('is_out', String(params.is_out));
		if (params && params.zone_id !== undefined) searchParams.set('zone_id', String(params.zone_id));
		var query = searchParams.toString();
		return fetchApi<RfidTag[]>('/api/rfid/tags' + (query ? '?' + query : ''));
	},

	getTag: (id: number) => fetchApi<RfidTag>('/api/rfid/tags/' + id),

	createTag: (data: RfidTagCreate) =>
		fetchApi<RfidTag>('/api/rfid/tags', {
			method: 'POST',
			body: JSON.stringify(data)
		}),

	updateTag: (id: number, data: Partial<RfidTagCreate>) =>
		fetchApi<RfidTag>('/api/rfid/tags/' + id, {
			method: 'PUT',
			body: JSON.stringify(data)
		}),

	deleteTag: (id: number) =>
		fetchApi<void>('/api/rfid/tags/' + id, { method: 'DELETE' }),

	getItemsOut: (minutesThreshold?: number) => {
		var params = minutesThreshold ? '?minutes_threshold=' + minutesThreshold : '';
		return fetchApi<PutItBackAlert[]>('/api/rfid/out' + params);
	},

	guideReturn: (tagId: number) =>
		fetchApi<{ status: string; tag_id: number; home_zone_id: number }>('/api/rfid/guide-return/' + tagId, {
			method: 'POST'
		}),

	acknowledgeReturn: (tagId: number) =>
		fetchApi<{ status: string; tag_id: number }>('/api/rfid/acknowledge-return/' + tagId, {
			method: 'POST'
		})
};
