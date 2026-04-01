import { c as create_ssr_component, a as subscribe, v as validate_component, b as each, e as escape } from "../../../chunks/ssr.js";
import { H as Header } from "../../../chunks/Header.js";
import { s as selectedFreezerId, f as freezers, o as oldestFrozenItems, a as freezerContentsByCategory, b as freezerContents, g as getDaysFrozen } from "../../../chunks/shopping.js";
import { M as Modal } from "../../../chunks/Modal.js";
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let $selectedFreezerId, $$unsubscribe_selectedFreezerId;
  let $freezers, $$unsubscribe_freezers;
  let $oldestFrozenItems, $$unsubscribe_oldestFrozenItems;
  let $freezerContentsByCategory, $$unsubscribe_freezerContentsByCategory;
  $$unsubscribe_selectedFreezerId = subscribe(selectedFreezerId, (value) => $selectedFreezerId = value);
  $$unsubscribe_freezers = subscribe(freezers, (value) => $freezers = value);
  $$unsubscribe_oldestFrozenItems = subscribe(oldestFrozenItems, (value) => $oldestFrozenItems = value);
  $$unsubscribe_freezerContentsByCategory = subscribe(freezerContentsByCategory, (value) => $freezerContentsByCategory = value);
  let showModal = false;
  let $$settled;
  let $$rendered;
  let previous_head = $$result.head;
  do {
    $$settled = true;
    $$result.head = previous_head;
    {
      if ($selectedFreezerId) {
        freezerContents.load($selectedFreezerId);
      }
    }
    $$rendered = `${validate_component(Header, "Header").$$render(
      $$result,
      {
        title: "Freezer",
        showBack: true,
        backHref: "/"
      },
      {},
      {}
    )} <main class="flex-1 flex flex-col overflow-hidden"> <div class="p-4 pb-3 flex gap-2 overflow-x-auto shrink-0">${each($freezers, (freezer) => {
      return `<button class="${"px-5 py-3 rounded-xl text-lg font-semibold whitespace-nowrap transition-all " + escape(
        $selectedFreezerId === freezer.id ? "bg-cyan-500 text-white shadow-lg" : "bg-white text-gray-600 border border-gray-200",
        true
      )}">🧊 ${escape(freezer.name)} </button>`;
    })}</div> <div class="flex-1 p-4 pt-0 overflow-y-auto space-y-4"> ${$oldestFrozenItems.length > 0 ? `<section class="p-4 rounded-2xl border-2 border-amber-300 bg-amber-50"><h3 class="text-xl font-bold text-amber-800 mb-3" data-svelte-h="svelte-182jqum">⚠ Use Soon</h3> <div class="space-y-2">${each($oldestFrozenItems.slice(0, 3), (item) => {
      let days = getDaysFrozen(item.frozen_date);
      return ` <button type="button" class="w-full flex items-center justify-between p-3 rounded-xl bg-white border border-amber-200 text-left active:scale-95 transition-transform"><span class="text-lg font-semibold text-amber-900">${escape(item.product.name)}</span> <span class="text-lg font-bold text-amber-600">${escape(days)}d</span> </button>`;
    })}</div></section>` : ``}  ${Object.entries($freezerContentsByCategory).length ? each(Object.entries($freezerContentsByCategory), ([category, items]) => {
      return `<section><h3 class="text-lg font-bold text-gray-700 mb-3">${escape(category)}</h3> <div class="grid grid-cols-2 gap-3">${each(items, (item) => {
        let days = getDaysFrozen(item.frozen_date), isOld = days !== null && days > 90;
        return `  <button class="${"p-4 rounded-2xl text-left transition-all active:scale-95 " + escape(
          isOld ? "bg-amber-50 border-2 border-amber-200" : "bg-white border-2 border-gray-100 shadow-sm",
          true
        )}"><p class="text-xl font-bold text-gray-800 truncate">${escape(item.product.name)}</p> <div class="flex items-center justify-between mt-2"><span class="text-lg text-gray-600">${escape(item.quantity)} ${escape(item.product.default_unit)}</span> ${days !== null ? `<span class="${"text-lg font-bold " + escape(isOld ? "text-amber-600" : "text-cyan-600", true)}">${escape(days)}d</span>` : ``}</div> </button>`;
      })}</div> </section>`;
    }) : `<div class="text-center py-16">${$freezers.length === 0 ? `<p class="text-xl text-gray-500" data-svelte-h="svelte-vxhqtr">No freezers configured</p> <a href="/settings" class="inline-block mt-4 px-8 py-4 rounded-2xl bg-cyan-500 text-white text-xl font-bold" data-svelte-h="svelte-1yka2gk">Add Freezer</a>` : `<p class="text-xl text-gray-500" data-svelte-h="svelte-sfajpm">This freezer is empty</p>`} </div>`}</div>  <div class="p-4 border-t border-gray-100 shrink-0" data-svelte-h="svelte-rf9j9j"><a href="/freezer/add" class="block w-full py-5 rounded-2xl bg-gradient-to-r from-cyan-500 to-cyan-600 text-white text-xl font-bold shadow-lg text-center active:scale-95 transition-transform">+ Add to Freezer</a></div></main>  ${validate_component(Modal, "Modal").$$render(
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
  $$unsubscribe_selectedFreezerId();
  $$unsubscribe_freezers();
  $$unsubscribe_oldestFrozenItems();
  $$unsubscribe_freezerContentsByCategory();
  return $$rendered;
});
export {
  Page as default
};
