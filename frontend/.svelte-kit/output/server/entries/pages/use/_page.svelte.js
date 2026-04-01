import { c as create_ssr_component, a as subscribe, v as validate_component, e as escape, b as each } from "../../../chunks/ssr.js";
import { H as Header } from "../../../chunks/Header.js";
import { S as SearchBar } from "../../../chunks/SearchBar.js";
import { M as Modal } from "../../../chunks/Modal.js";
import { h as inventory, p as products } from "../../../chunks/shopping.js";
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let filteredProducts;
  let $inventory, $$unsubscribe_inventory;
  let $products, $$unsubscribe_products;
  $$unsubscribe_inventory = subscribe(inventory, (value) => $inventory = value);
  $$unsubscribe_products = subscribe(products, (value) => $products = value);
  let searchQuery = "";
  let showModal = false;
  let $$settled;
  let $$rendered;
  let previous_head = $$result.head;
  do {
    $$settled = true;
    $$result.head = previous_head;
    filteredProducts = searchQuery ? $products.filter((p) => p.name.toLowerCase().includes(searchQuery.toLowerCase())) : $products.slice(0, 12);
    $$rendered = `${validate_component(Header, "Header").$$render(
      $$result,
      {
        title: "Use Item",
        showBack: true,
        backHref: "/"
      },
      {},
      {}
    )} <main class="flex-1 flex flex-col overflow-hidden p-4"> <div class="mb-4">${validate_component(SearchBar, "SearchBar").$$render(
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
    )}</div>  <h3 class="text-lg font-bold text-gray-700 mb-3">${escape(searchQuery ? "Search Results" : "Select item to use")}</h3>  <div class="flex-1 overflow-y-auto"><div class="grid grid-cols-2 gap-3">${filteredProducts.length ? each(filteredProducts, (product) => {
      let invItems = $inventory.filter((i) => i.product_id === product.id), totalQty = invItems.reduce((sum, i) => sum + i.quantity, 0);
      return `  <button type="button" class="${"p-4 rounded-2xl text-left transition-all active:scale-95 " + escape(
        totalQty <= 0 ? "bg-gray-100 border-2 border-gray-200 opacity-50" : "bg-white border-2 border-gray-100 shadow-sm",
        true
      )}" ${totalQty <= 0 ? "disabled" : ""}><p class="text-xl font-bold text-gray-800 truncate">${escape(product.name)}</p> <div class="flex items-center justify-between mt-2"><span class="${"text-2xl font-bold " + escape(totalQty > 0 ? "text-green-600" : "text-red-400", true)}">${escape(totalQty)}</span> <span class="text-gray-500" data-svelte-h="svelte-1kde1cz">in stock</span></div> </button>`;
    }) : `<div class="col-span-full text-center py-16"><p class="text-xl text-gray-500">${escape(searchQuery ? `No products match "${searchQuery}"` : "No products yet")}</p> </div>`}</div></div></main>  ${validate_component(Modal, "Modal").$$render(
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
  $$unsubscribe_inventory();
  $$unsubscribe_products();
  return $$rendered;
});
export {
  Page as default
};
