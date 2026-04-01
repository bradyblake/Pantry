import { c as create_ssr_component, a as subscribe, o as onDestroy, v as validate_component } from "../../../../chunks/ssr.js";
import { p as page } from "../../../../chunks/stores.js";
import "@sveltejs/kit/internal";
import "../../../../chunks/exports.js";
import "../../../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../../../chunks/state.svelte.js";
import { H as Header } from "../../../../chunks/Header.js";
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let $page, $$unsubscribe_page;
  $$unsubscribe_page = subscribe(page, (value) => $page = value);
  onDestroy(function() {
  });
  parseInt($page.params.id);
  $$unsubscribe_page();
  return `${` ${validate_component(Header, "Header").$$render(
    $$result,
    {
      title: "Recipe",
      showBack: true,
      backHref: "/recipes"
    },
    {},
    {}
  )} <main class="flex-1 flex flex-col overflow-hidden">${`<div class="flex justify-center py-12" data-svelte-h="svelte-amlxx1"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div></div>`}</main>`}  ${``}  ${``}`;
});
export {
  Page as default
};
