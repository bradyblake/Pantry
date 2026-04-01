import { w as writable, d as derived } from "./index.js";
const API_BASE = "";
async function fetchApi(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers
    }
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  if (response.status === 204) {
    return void 0;
  }
  return response.json();
}
const productsApi = {
  list: (params) => {
    const searchParams = new URLSearchParams();
    if (params?.search) searchParams.set("search", params.search);
    if (params?.category) searchParams.set("category", params.category);
    const query = searchParams.toString();
    return fetchApi(`/api/products${query ? `?${query}` : ""}`);
  },
  get: (id) => fetchApi(`/api/products/${id}`),
  getByBarcode: (barcode) => fetchApi(`/api/products/barcode/${barcode}`),
  create: (data) => fetchApi("/api/products", {
    method: "POST",
    body: JSON.stringify(data)
  }),
  update: (id, data) => fetchApi(`/api/products/${id}`, {
    method: "PUT",
    body: JSON.stringify(data)
  }),
  delete: (id) => fetchApi(`/api/products/${id}`, { method: "DELETE" }),
  getCategories: () => fetchApi("/api/products/categories")
};
const freezersApi = {
  list: () => fetchApi("/api/freezers"),
  get: (id) => fetchApi(`/api/freezers/${id}`),
  getContents: (id, category) => {
    const params = category ? `?category=${encodeURIComponent(category)}` : "";
    return fetchApi(`/api/freezers/${id}/contents${params}`);
  },
  getOldest: (params) => {
    const searchParams = new URLSearchParams();
    if (params?.freezer_id) searchParams.set("freezer_id", params.freezer_id.toString());
    if (params?.days) searchParams.set("days", params.days.toString());
    if (params?.limit) searchParams.set("limit", params.limit.toString());
    const query = searchParams.toString();
    return fetchApi(`/api/freezers/oldest${query ? `?${query}` : ""}`);
  },
  create: (data) => fetchApi("/api/freezers", {
    method: "POST",
    body: JSON.stringify(data)
  }),
  update: (id, data) => fetchApi(`/api/freezers/${id}`, {
    method: "PUT",
    body: JSON.stringify(data)
  }),
  delete: (id) => fetchApi(`/api/freezers/${id}`, { method: "DELETE" })
};
const inventoryApi = {
  list: (params) => {
    const searchParams = new URLSearchParams();
    if (params?.location) searchParams.set("location", params.location);
    if (params?.category) searchParams.set("category", params.category);
    const query = searchParams.toString();
    return fetchApi(`/api/inventory${query ? `?${query}` : ""}`);
  },
  getLowStock: (threshold) => {
    const params = threshold ? `?threshold=${threshold}` : "";
    return fetchApi(`/api/inventory/low-stock${params}`);
  },
  getForProduct: (productId) => fetchApi(`/api/inventory/product/${productId}`),
  getLog: (params) => {
    const searchParams = new URLSearchParams();
    if (params?.product_id) searchParams.set("product_id", params.product_id.toString());
    if (params?.source) searchParams.set("source", params.source);
    if (params?.limit) searchParams.set("limit", params.limit.toString());
    if (params?.offset) searchParams.set("offset", params.offset.toString());
    const query = searchParams.toString();
    return fetchApi(`/api/inventory/log${query ? `?${query}` : ""}`);
  },
  add: (data) => fetchApi("/api/inventory/add", {
    method: "POST",
    body: JSON.stringify(data)
  }),
  use: (data) => fetchApi("/api/inventory/use", {
    method: "POST",
    body: JSON.stringify(data)
  }),
  update: (id, data) => fetchApi(`/api/inventory/${id}`, {
    method: "PUT",
    body: JSON.stringify(data)
  }),
  delete: (id) => fetchApi(`/api/inventory/${id}`, { method: "DELETE" })
};
const shoppingApi = {
  list: (checked) => {
    const params = checked !== void 0 ? `?checked=${checked}` : "";
    return fetchApi(`/api/shopping${params}`);
  },
  get: (id) => fetchApi(`/api/shopping/${id}`),
  create: (data) => fetchApi("/api/shopping", {
    method: "POST",
    body: JSON.stringify(data)
  }),
  update: (id, data) => fetchApi(`/api/shopping/${id}`, {
    method: "PUT",
    body: JSON.stringify(data)
  }),
  delete: (id) => fetchApi(`/api/shopping/${id}`, { method: "DELETE" }),
  clearChecked: () => fetchApi("/api/shopping/clear-checked", { method: "DELETE" }),
  generateFromLowStock: (threshold) => {
    const params = threshold ? `?threshold=${threshold}` : "";
    return fetchApi(`/api/shopping/generate-from-low-stock${params}`, {
      method: "POST"
    });
  }
};
function createProductsStore() {
  const { subscribe, set, update } = writable([]);
  return {
    subscribe,
    load: async () => {
      const products2 = await productsApi.list();
      set(products2);
    },
    search: async (query, category) => {
      const products2 = await productsApi.list({ search: query, category });
      set(products2);
    },
    add: async (product) => {
      const newProduct = await productsApi.create(product);
      update((products2) => [...products2, newProduct]);
      return newProduct;
    },
    update: async (id, data) => {
      const updated = await productsApi.update(id, data);
      update((products2) => products2.map((p) => p.id === id ? updated : p));
      return updated;
    },
    remove: async (id) => {
      await productsApi.delete(id);
      update((products2) => products2.filter((p) => p.id !== id));
    }
  };
}
const products = createProductsStore();
function createCategoriesStore() {
  const { subscribe, set } = writable([]);
  return {
    subscribe,
    load: async () => {
      const categories2 = await productsApi.getCategories();
      set(categories2);
    }
  };
}
const categories = createCategoriesStore();
function getStockLevel(quantity, threshold = 1) {
  if (quantity <= 0) return "out";
  if (quantity <= threshold) return "low";
  return "high";
}
function getDaysFrozen(frozenDate) {
  if (!frozenDate) return null;
  const frozen = new Date(frozenDate);
  const today = /* @__PURE__ */ new Date();
  const diffTime = Math.abs(today.getTime() - frozen.getTime());
  return Math.ceil(diffTime / (1e3 * 60 * 60 * 24));
}
function createInventoryStore() {
  const { subscribe, set, update } = writable([]);
  return {
    subscribe,
    load: async (location, category) => {
      const items = await inventoryApi.list({ location, category });
      set(items);
    },
    add: async (data) => {
      const item = await inventoryApi.add(data);
      const items = await inventoryApi.list();
      set(items);
      return item;
    },
    use: async (data) => {
      const item = await inventoryApi.use(data);
      update((items) => items.map((i) => i.id === item.id ? item : i));
      return item;
    },
    updateItem: async (id, data) => {
      const item = await inventoryApi.update(id, data);
      update((items) => items.map((i) => i.id === id ? item : i));
      return item;
    },
    remove: async (id) => {
      await inventoryApi.delete(id);
      update((items) => items.filter((i) => i.id !== id));
    },
    refresh: async () => {
      const items = await inventoryApi.list();
      set(items);
    }
  };
}
const inventory = createInventoryStore();
const lowStockItems = derived(
  inventory,
  ($inventory) => $inventory.filter((item) => getStockLevel(item.quantity) !== "high")
);
const inventoryByCategory = derived(inventory, ($inventory) => {
  const grouped = {};
  for (const item of $inventory) {
    const category = item.product.category || "Other";
    if (!grouped[category]) {
      grouped[category] = [];
    }
    grouped[category].push(item);
  }
  const sorted = {};
  for (const key of Object.keys(grouped).sort()) {
    sorted[key] = grouped[key];
  }
  return sorted;
});
function createLogStore() {
  const { subscribe, set } = writable([]);
  return {
    subscribe,
    load: async (productId, limit = 50) => {
      const log = await inventoryApi.getLog({ product_id: productId, limit });
      set(log);
    }
  };
}
createLogStore();
function createFreezersStore() {
  const { subscribe, set, update } = writable([]);
  return {
    subscribe,
    load: async () => {
      const freezers2 = await freezersApi.list();
      set(freezers2);
      return freezers2;
    },
    add: async (data) => {
      const freezer = await freezersApi.create(data);
      update((freezers2) => [...freezers2, freezer]);
      return freezer;
    },
    update: async (id, data) => {
      const updated = await freezersApi.update(id, data);
      update((freezers2) => freezers2.map((f) => f.id === id ? updated : f));
      return updated;
    },
    remove: async (id) => {
      await freezersApi.delete(id);
      update((freezers2) => freezers2.filter((f) => f.id !== id));
    }
  };
}
const freezers = createFreezersStore();
const selectedFreezerId = writable(null);
function createFreezerContentsStore() {
  const { subscribe, set } = writable([]);
  return {
    subscribe,
    load: async (freezerId, category) => {
      const contents = await freezersApi.getContents(freezerId, category);
      set(contents);
      return contents;
    },
    clear: () => set([])
  };
}
const freezerContents = createFreezerContentsStore();
function createOldestItemsStore() {
  const { subscribe, set } = writable([]);
  return {
    subscribe,
    load: async (freezerId, days = 90, limit = 10) => {
      const items = await freezersApi.getOldest({ freezer_id: freezerId, days, limit });
      set(items);
      return items;
    }
  };
}
const oldestFrozenItems = createOldestItemsStore();
const freezerContentsByCategory = derived(freezerContents, ($contents) => {
  const grouped = {};
  for (const item of $contents) {
    const category = item.product.category || "Other";
    if (!grouped[category]) {
      grouped[category] = [];
    }
    grouped[category].push(item);
  }
  return grouped;
});
function createShoppingStore() {
  const { subscribe, set, update } = writable([]);
  return {
    subscribe,
    load: async () => {
      const items = await shoppingApi.list();
      set(items);
    },
    add: async (data) => {
      const item = await shoppingApi.create(data);
      update((items) => [item, ...items]);
      return item;
    },
    update: async (id, data) => {
      const updated = await shoppingApi.update(id, data);
      update((items) => items.map((i) => i.id === id ? updated : i));
      return updated;
    },
    toggle: async (id) => {
      const items = await shoppingApi.list();
      const item = items.find((i) => i.id === id);
      if (item) {
        const updated = await shoppingApi.update(id, { checked: !item.checked });
        update((items2) => items2.map((i) => i.id === id ? updated : i));
        return updated;
      }
    },
    remove: async (id) => {
      await shoppingApi.delete(id);
      update((items) => items.filter((i) => i.id !== id));
    },
    clearChecked: async () => {
      await shoppingApi.clearChecked();
      update((items) => items.filter((i) => !i.checked));
    },
    generateFromLowStock: async () => {
      const newItems = await shoppingApi.generateFromLowStock();
      if (newItems.length > 0) {
        const items = await shoppingApi.list();
        set(items);
      }
      return newItems;
    }
  };
}
const shopping = createShoppingStore();
const uncheckedItems = derived(
  shopping,
  ($shopping) => $shopping.filter((item) => !item.checked)
);
const checkedItems = derived(
  shopping,
  ($shopping) => $shopping.filter((item) => item.checked)
);
const uncheckedCount = derived(uncheckedItems, ($items) => $items.length);
export {
  freezerContentsByCategory as a,
  freezerContents as b,
  categories as c,
  uncheckedItems as d,
  checkedItems as e,
  freezers as f,
  getDaysFrozen as g,
  inventory as h,
  inventoryByCategory as i,
  lowStockItems as l,
  oldestFrozenItems as o,
  products as p,
  selectedFreezerId as s,
  uncheckedCount as u
};
