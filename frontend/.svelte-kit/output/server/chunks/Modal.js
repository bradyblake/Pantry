import { c as create_ssr_component, f as createEventDispatcher, e as escape } from "./ssr.js";
const Modal = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { open = false } = $$props;
  let { title = "" } = $$props;
  createEventDispatcher();
  if ($$props.open === void 0 && $$bindings.open && open !== void 0) $$bindings.open(open);
  if ($$props.title === void 0 && $$bindings.title && title !== void 0) $$bindings.title(title);
  return ` ${open ? `<div class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 sm:p-6"> <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" role="button" tabindex="-1"></div>  <div class="relative bg-white w-full max-w-lg max-h-[85vh] overflow-auto rounded-2xl shadow-2xl border border-gray-100"> <div class="sm:hidden flex justify-center pt-3 pb-1" data-svelte-h="svelte-axcmvm"><div class="w-10 h-1 bg-gray-300 rounded-full"></div></div> ${title ? `<div class="flex items-center justify-between px-5 py-4 border-b border-gray-100"><h2 class="text-lg font-bold text-gray-800">${escape(title)}</h2> <button type="button" class="p-2 -mr-2 rounded-xl hover:bg-gray-100 active:bg-gray-200 transition-colors" data-svelte-h="svelte-1pnvf1n"><svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg></button></div>` : ``} <div class="p-5">${slots.default ? slots.default({}) : ``}</div></div></div>` : ``}`;
});
export {
  Modal as M
};
