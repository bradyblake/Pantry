import { c as create_ssr_component, a as subscribe, v as validate_component, b as each, e as escape } from "../../../../chunks/ssr.js";
import "@sveltejs/kit/internal";
import "../../../../chunks/exports.js";
import "../../../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../../../chunks/state.svelte.js";
import { H as Header } from "../../../../chunks/Header.js";
import { S as SearchBar } from "../../../../chunks/SearchBar.js";
import { p as products, f as freezers } from "../../../../chunks/shopping.js";
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let filteredProducts;
  let $products, $$unsubscribe_products;
  let $$unsubscribe_freezers;
  $$unsubscribe_products = subscribe(products, (value) => $products = value);
  $$unsubscribe_freezers = subscribe(freezers, (value) => value);
  let searchQuery = "";
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
        title: "Add to Freezer",
        showBack: true,
        backHref: "/freezer"
      },
      {},
      {}
    )} <main class="flex-1 p-4">${` <div class="space-y-4">${validate_component(SearchBar, "SearchBar").$$render(
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
    )} <div class="grid grid-cols-2 gap-3">${filteredProducts.length ? each(filteredProducts, (product) => {
      return `<button type="button" class="card text-left hover:shadow-md active:shadow-sm transition-shadow"><p class="font-semibold text-gray-900 truncate">${escape(product.name)}</p> ${product.category ? `<p class="text-xs text-gray-500">${escape(product.category)}</p>` : ``} </button>`;
    }) : `<p class="col-span-full text-center py-8 text-gray-500">${escape(searchQuery ? `No products match "${searchQuery}"` : "No products yet")} </p>`}</div> ${searchQuery && filteredProducts.length === 0 ? `<a href="/add" class="btn btn-outline w-full text-center" data-svelte-h="svelte-1h88hb8">Create New Product</a>` : ``}</div>`}</main>`;
  } while (!$$settled);
  $$unsubscribe_products();
  $$unsubscribe_freezers();
  return $$rendered;
});
export {
  Page as default
};
