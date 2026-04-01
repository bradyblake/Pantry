import { c as create_ssr_component } from "../../chunks/ssr.js";
import "../../chunks/shopping.js";
const Layout = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  return `<div class="min-h-screen flex flex-col">${slots.default ? slots.default({}) : ``}</div>`;
});
export {
  Layout as default
};
