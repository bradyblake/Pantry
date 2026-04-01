import { c as create_ssr_component, a as subscribe, v as validate_component } from "../../../chunks/ssr.js";
import "@sveltejs/kit/internal";
import "../../../chunks/exports.js";
import "../../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../../chunks/state.svelte.js";
import { H as Header } from "../../../chunks/Header.js";
import { M as Modal } from "../../../chunks/Modal.js";
import { c as categories, p as products } from "../../../chunks/shopping.js";
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let $categories, $$unsubscribe_categories;
  let $$unsubscribe_products;
  $$unsubscribe_categories = subscribe(categories, (value) => $categories = value);
  $$unsubscribe_products = subscribe(products, (value) => value);
  let showModal = false;
  let defaultCategories = [];
  let $$settled;
  let $$rendered;
  let previous_head = $$result.head;
  do {
    $$settled = true;
    $$result.head = previous_head;
    [.../* @__PURE__ */ new Set([...defaultCategories, ...$categories])];
    $$rendered = `${validate_component(Header, "Header").$$render(
      $$result,
      {
        title: "Add Stock",
        showBack: true,
        backHref: "/"
      },
      {},
      {}
    )} <main class="flex-1 p-4 flex flex-col overflow-hidden">${` <button class="flex-1 flex items-center justify-center gap-6 rounded-3xl bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-xl active:scale-[0.98] transition-transform" data-svelte-h="svelte-zfw3ev"><svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg> <div class="text-left"><span class="text-4xl font-bold block">Manual Entry</span> <span class="text-xl text-green-100">Search and add items</span></div></button>`}</main>  ${validate_component(Modal, "Modal").$$render(
      $$result,
      {
        title: `Add ${""}`,
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
  $$unsubscribe_categories();
  $$unsubscribe_products();
  return $$rendered;
});
export {
  Page as default
};
