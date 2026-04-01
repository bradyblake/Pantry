import { c as create_ssr_component, f as createEventDispatcher, d as add_attribute } from "./ssr.js";
const SearchBar = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { value = "" } = $$props;
  let { placeholder = "Search..." } = $$props;
  let { autofocus = false } = $$props;
  createEventDispatcher();
  if ($$props.value === void 0 && $$bindings.value && value !== void 0) $$bindings.value(value);
  if ($$props.placeholder === void 0 && $$bindings.placeholder && placeholder !== void 0) $$bindings.placeholder(placeholder);
  if ($$props.autofocus === void 0 && $$bindings.autofocus && autofocus !== void 0) $$bindings.autofocus(autofocus);
  return `<div class="relative group"><div class="${[
    "absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none transition-colors duration-200",
    " text-gray-400"
  ].join(" ").trim()}" data-svelte-h="svelte-1747e0h"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg></div> <input type="text"${add_attribute("value", value, 0)}${add_attribute("placeholder", placeholder, 0)} ${autofocus ? "autofocus" : ""} class="input pl-12 pr-12 bg-white/80 backdrop-blur-sm shadow-sm hover:shadow transition-shadow duration-200"> ${value ? `<button type="button" class="absolute inset-y-0 right-0 pr-4 flex items-center group/clear" data-svelte-h="svelte-1ocdgh0"><div class="p-1 rounded-full bg-gray-100 group-hover/clear:bg-gray-200 transition-colors"><svg class="w-3.5 h-3.5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"></path></svg></div></button>` : ``}</div>`;
});
export {
  SearchBar as S
};
