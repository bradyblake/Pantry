import { c as create_ssr_component, a as subscribe, v as validate_component, e as escape, b as each } from "../../../chunks/ssr.js";
import { p as page } from "../../../chunks/stores.js";
import { H as Header } from "../../../chunks/Header.js";
import { S as SearchBar } from "../../../chunks/SearchBar.js";
import { M as Modal } from "../../../chunks/Modal.js";
import { i as inventoryByCategory, l as lowStockItems } from "../../../chunks/shopping.js";
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let filteredCategories;
  let $inventoryByCategory, $$unsubscribe_inventoryByCategory;
  let $$unsubscribe_lowStockItems;
  let $$unsubscribe_page;
  $$unsubscribe_inventoryByCategory = subscribe(inventoryByCategory, (value) => $inventoryByCategory = value);
  $$unsubscribe_lowStockItems = subscribe(lowStockItems, (value) => value);
  $$unsubscribe_page = subscribe(page, (value) => value);
  let searchQuery = "";
  let showModal = false;
  let $$settled;
  let $$rendered;
  let previous_head = $$result.head;
  do {
    $$settled = true;
    $$result.head = previous_head;
    filteredCategories = (() => {
      let items = Object.values($inventoryByCategory).flat();
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        items = items.filter((i) => i.product.name.toLowerCase().includes(query) || i.product.category?.toLowerCase().includes(query));
      }
      const grouped = {};
      for (const item of items) {
        const category = item.product.category || "Other";
        if (!grouped[category]) grouped[category] = [];
        grouped[category].push(item);
      }
      return grouped;
    })();
    $$rendered = `${validate_component(Header, "Header").$$render(
      $$result,
      {
        title: "Inventory",
        showBack: true,
        backHref: "/"
      },
      {},
      {}
    )} <main class="flex-1 flex flex-col overflow-hidden"> <div class="p-4 pb-3">${validate_component(SearchBar, "SearchBar").$$render(
      $$result,
      {
        placeholder: "Search inventory...",
        value: searchQuery
      },
      {
        value: ($$value) => {
          searchQuery = $$value;
          $$settled = false;
        }
      },
      {}
    )}</div>  <div class="px-4 pb-3 flex gap-2 overflow-x-auto"><button class="${"px-5 py-3 rounded-xl text-lg font-semibold whitespace-nowrap transition-all " + escape(
      "bg-blue-500 text-white shadow-lg",
      true
    )}">All</button> <button class="${"px-5 py-3 rounded-xl text-lg font-semibold whitespace-nowrap transition-all " + escape(
      "bg-white text-gray-600 border border-gray-200",
      true
    )}">🏠 Pantry</button> <button class="${"px-5 py-3 rounded-xl text-lg font-semibold whitespace-nowrap transition-all " + escape(
      "bg-white text-gray-600 border border-gray-200",
      true
    )}">🧊 Fridge</button> <button class="${"px-5 py-3 rounded-xl text-lg font-semibold whitespace-nowrap transition-all " + escape(
      "bg-white text-gray-600 border border-gray-200",
      true
    )}">❄ Freezer</button> <button class="${"px-5 py-3 rounded-xl text-lg font-semibold whitespace-nowrap transition-all " + escape(
      "bg-white text-gray-600 border border-gray-200",
      true
    )}">⚠ Low</button></div>  <div class="flex-1 p-4 pt-2 overflow-y-auto">${Object.entries(filteredCategories).length ? each(Object.entries(filteredCategories), ([category, items], i) => {
      return `<div class="mb-5"><h3 class="text-lg font-bold text-gray-700 mb-3">${escape(category)}</h3> <div class="grid grid-cols-2 gap-3">${each(items, (item) => {
        let stockLevel = item.quantity <= 0 ? "out" : item.quantity <= 1 ? "low" : "high";
        return ` <button class="${"p-4 rounded-2xl text-left transition-all active:scale-95 " + escape(
          stockLevel === "out" ? "bg-red-50 border-2 border-red-200" : stockLevel === "low" ? "bg-amber-50 border-2 border-amber-200" : "bg-white border-2 border-gray-100 shadow-sm",
          true
        )}"><p class="text-xl font-bold text-gray-800 truncate">${escape(item.product.name)}</p> <div class="flex items-center justify-between mt-2"><span class="${"text-2xl font-bold " + escape(
          stockLevel === "out" ? "text-red-500" : stockLevel === "low" ? "text-amber-500" : "text-green-600",
          true
        )}">${escape(item.quantity)}</span> <span class="text-gray-500">${escape(item.product.default_unit)}${escape(item.quantity !== 1 ? "s" : "")}</span></div> ${item.location ? `<p class="text-sm text-gray-400 mt-1 capitalize">${escape(item.location)}</p>` : ``} </button>`;
      })}</div> </div>`;
    }) : `<div class="text-center py-16"><div class="w-24 h-24 mx-auto mb-4 rounded-2xl bg-gray-100 flex items-center justify-center" data-svelte-h="svelte-1s50akt"><svg class="w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg></div> ${searchQuery ? `<p class="text-xl text-gray-500 font-medium">No items match &quot;${escape(searchQuery)}&quot;</p> <p class="text-gray-400 mt-1" data-svelte-h="svelte-1xoz1x1">Try a different search term</p>` : `<p class="text-xl text-gray-500 font-medium" data-svelte-h="svelte-2bkwl5">No items in inventory</p> <p class="text-gray-400 mt-1" data-svelte-h="svelte-1eugk6z">Add items to get started</p> <a href="/add" class="inline-flex mt-6 px-8 py-4 rounded-2xl bg-green-500 text-white text-xl font-bold shadow-lg" data-svelte-h="svelte-fidfd">Add Items</a>`} </div>`}</div></main>  ${validate_component(Modal, "Modal").$$render(
      $$result,
      {
        title: "",
        open: showModal
      },
      {
        open: ($$value) => {
          showModal = $$value;
          $$settled = false;
        }
      },
      {
        default: () => {
          return `${``}`;
        }
      }
    )}`;
  } while (!$$settled);
  $$unsubscribe_inventoryByCategory();
  $$unsubscribe_lowStockItems();
  $$unsubscribe_page();
  return $$rendered;
});
export {
  Page as default
};
