import { c as create_ssr_component, a as subscribe, v as validate_component, e as escape, b as each, d as add_attribute } from "../../../chunks/ssr.js";
import { H as Header } from "../../../chunks/Header.js";
import { S as SearchBar } from "../../../chunks/SearchBar.js";
import { M as Modal } from "../../../chunks/Modal.js";
import { p as products, d as uncheckedItems, e as checkedItems } from "../../../chunks/shopping.js";
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let filteredProducts;
  let $products, $$unsubscribe_products;
  let $uncheckedItems, $$unsubscribe_uncheckedItems;
  let $checkedItems, $$unsubscribe_checkedItems;
  $$unsubscribe_products = subscribe(products, (value) => $products = value);
  $$unsubscribe_uncheckedItems = subscribe(uncheckedItems, (value) => $uncheckedItems = value);
  $$unsubscribe_checkedItems = subscribe(checkedItems, (value) => $checkedItems = value);
  let showAddModal = false;
  let searchQuery = "";
  let customItemName = "";
  let $$settled;
  let $$rendered;
  let previous_head = $$result.head;
  do {
    $$settled = true;
    $$result.head = previous_head;
    filteredProducts = searchQuery ? $products.filter((p) => p.name.toLowerCase().includes(searchQuery.toLowerCase())) : [];
    $$rendered = `${validate_component(Header, "Header").$$render(
      $$result,
      {
        title: "Shopping List",
        showBack: true,
        backHref: "/"
      },
      {},
      {}
    )} <main class="flex-1 flex flex-col overflow-hidden"><div class="flex-1 p-4 overflow-y-auto space-y-4"> ${$uncheckedItems.length > 0 ? `<section><h3 class="text-lg font-bold text-gray-700 mb-3">🛒 To Buy (${escape($uncheckedItems.length)})</h3> <div class="space-y-2">${each($uncheckedItems, (item) => {
      return `<div class="flex items-center gap-4 p-4 bg-white rounded-2xl border-2 border-gray-100 shadow-sm"><button type="button" class="w-10 h-10 rounded-full border-3 border-gray-300 flex-shrink-0 active:scale-90 transition-transform"></button> <div class="flex-1 min-w-0"><p class="text-xl font-semibold text-gray-800">${escape(item.product?.name || item.custom_item_name)}</p> ${item.quantity ? `<p class="text-sm text-gray-400">${escape(item.quantity)} ${escape(item.unit || item.product?.default_unit || "")} </p>` : ``}</div> <button type="button" class="p-3 text-gray-300 hover:text-red-500 rounded-xl active:scale-90 transition-all" data-svelte-h="svelte-3bjjwz"><svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg></button> </div>`;
    })}</div></section>` : ``}  ${$checkedItems.length > 0 ? `<section><div class="flex items-center justify-between mb-3"><h3 class="text-lg font-bold text-gray-400">✅ Done (${escape($checkedItems.length)})</h3> <button type="button" class="px-4 py-2 text-sm font-semibold text-red-500 bg-red-50 rounded-lg" data-svelte-h="svelte-h7zf3n">Clear all</button></div> <div class="space-y-2 opacity-60">${each($checkedItems, (item) => {
      return `<div class="flex items-center gap-4 p-4 bg-gray-50 rounded-2xl"><button type="button" class="w-10 h-10 rounded-full bg-green-500 flex-shrink-0 flex items-center justify-center active:scale-90 transition-transform" data-svelte-h="svelte-1js6pjd"><svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path></svg></button> <p class="flex-1 text-xl line-through text-gray-400">${escape(item.product?.name || item.custom_item_name)}</p> </div>`;
    })}</div></section>` : ``} ${$uncheckedItems.length === 0 && $checkedItems.length === 0 ? `<div class="text-center py-16"><div class="w-24 h-24 mx-auto mb-4 rounded-2xl bg-rose-100 flex items-center justify-center" data-svelte-h="svelte-1q1pld1"><span class="text-5xl">📋</span></div> <p class="text-xl text-gray-600 font-semibold mb-2" data-svelte-h="svelte-z8mr7">Shopping list is empty</p> <p class="text-gray-400 mb-6" data-svelte-h="svelte-m65xvw">Add items or generate from low stock</p> <button class="px-8 py-4 rounded-2xl bg-amber-500 text-white text-xl font-bold shadow-lg" data-svelte-h="svelte-b6fu2w">+ Add Low-Stock Items</button></div>` : ``}</div>  <div class="p-4 border-t border-gray-100 flex gap-3 shrink-0"><button class="flex-1 py-5 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-600 text-white text-xl font-bold shadow-lg active:scale-95 transition-transform" data-svelte-h="svelte-1ghjeqe">+ Add Item</button> <button class="flex-1 py-5 rounded-2xl bg-amber-500 text-white text-xl font-bold shadow-lg active:scale-95 transition-transform" data-svelte-h="svelte-os29lk">⚠ Low Stock</button></div></main>  ${validate_component(Modal, "Modal").$$render(
      $$result,
      {
        title: "Add to Shopping List",
        open: showAddModal
      },
      {
        open: ($$value) => {
          showAddModal = $$value;
          $$settled = false;
        }
      },
      {
        default: () => {
          return `<div class="space-y-4">${validate_component(SearchBar, "SearchBar").$$render(
            $$result,
            {
              placeholder: "Search products...",
              autofocus: true,
              value: searchQuery
            },
            {
              value: ($$value) => {
                searchQuery = $$value;
                $$settled = false;
              }
            },
            {}
          )} ${filteredProducts.length > 0 ? `<div class="max-h-64 overflow-y-auto space-y-2">${each(filteredProducts, (product) => {
            return `<button type="button" class="w-full p-4 rounded-xl text-left bg-gray-50 active:bg-gray-100 transition-colors"><p class="text-lg font-semibold text-gray-800">${escape(product.name)}</p> ${product.category ? `<p class="text-sm text-gray-400">${escape(product.category)}</p>` : ``} </button>`;
          })}</div>` : ``} <div class="h-px bg-gray-200 my-4"></div> <div><label class="block text-lg font-semibold text-gray-700 mb-3" data-svelte-h="svelte-1ilnpqe">Or add custom item:</label> <div class="flex gap-3"><input type="text" class="flex-1 px-4 py-4 text-xl border-2 border-gray-200 rounded-xl focus:border-green-500 focus:outline-none" placeholder="Item name..."${add_attribute("value", customItemName, 0)}> <button class="px-6 py-4 rounded-xl bg-green-500 text-white text-xl font-bold disabled:opacity-50 active:scale-95 transition-transform" ${!customItemName.trim() ? "disabled" : ""}>Add</button></div></div></div>`;
        }
      }
    )}`;
  } while (!$$settled);
  $$unsubscribe_products();
  $$unsubscribe_uncheckedItems();
  $$unsubscribe_checkedItems();
  return $$rendered;
});
export {
  Page as default
};
