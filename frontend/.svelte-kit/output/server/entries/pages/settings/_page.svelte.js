import { c as create_ssr_component, a as subscribe, v as validate_component, e as escape, b as each } from "../../../chunks/ssr.js";
import { H as Header } from "../../../chunks/Header.js";
import { f as freezers } from "../../../chunks/shopping.js";
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let $freezers, $$unsubscribe_freezers;
  $$unsubscribe_freezers = subscribe(freezers, (value) => $freezers = value);
  $$unsubscribe_freezers();
  return `${validate_component(Header, "Header").$$render(
    $$result,
    {
      title: "Settings",
      showBack: true,
      backHref: "/"
    },
    {},
    {}
  )} <main class="flex-1 p-4 space-y-4"> <div class="flex gap-2 border-b border-gray-200 pb-2"><button type="button" class="${"px-4 py-2 text-sm font-medium rounded-t " + escape(
    "bg-primary text-white",
    true
  )}">Freezers</button> <button type="button" class="${"px-4 py-2 text-sm font-medium rounded-t " + escape(
    "text-gray-600",
    true
  )}">Zones</button> <button type="button" class="${"px-4 py-2 text-sm font-medium rounded-t " + escape(
    "text-gray-600",
    true
  )}">RFID Tags</button></div>  ${`<section><div class="flex items-center justify-between mb-3"><h2 class="text-lg font-semibold" data-svelte-h="svelte-13b6kj3">Freezers</h2> <button class="btn btn-secondary text-sm" data-svelte-h="svelte-1htiksh">+ Add</button></div> ${$freezers.length > 0 ? `<div class="card p-0 divide-y divide-gray-100">${each($freezers, (freezer) => {
    return `<button type="button" class="w-full p-4 text-left hover:bg-gray-50 flex items-center justify-between"><div><p class="font-medium text-gray-900">${escape(freezer.name)}</p> ${freezer.location ? `<p class="text-sm text-gray-500">${escape(freezer.location)}</p>` : ``}</div> <span class="text-gray-400" data-svelte-h="svelte-qw6dhh">→</span> </button>`;
  })}</div>` : `<p class="text-gray-500 text-center py-4" data-svelte-h="svelte-1nlzjng">No freezers configured</p>`}</section>`}  ${``}  ${``}  <section class="pt-4 border-t border-gray-200" data-svelte-h="svelte-lqhogw"><h2 class="text-lg font-semibold mb-3">About</h2> <div class="card"><p class="font-medium">PantryPal</p> <p class="text-sm text-gray-500">Smart Pantry Inventory System</p> <p class="text-sm text-gray-500 mt-2">Version 1.0 - Phase 1</p></div></section></main>  ${``}  ${``}`;
});
export {
  Page as default
};
