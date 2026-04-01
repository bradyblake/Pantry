import { c as create_ssr_component, v as validate_component } from "../../../../chunks/ssr.js";
import "@sveltejs/kit/internal";
import "../../../../chunks/exports.js";
import "../../../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../../../chunks/state.svelte.js";
import { H as Header } from "../../../../chunks/Header.js";
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  return `${validate_component(Header, "Header").$$render(
    $$result,
    {
      title: "Upload Recipe",
      backLink: "/recipes"
    },
    {},
    {}
  )} <main class="p-4 pb-24">${``}  ${`<div class="card p-6 text-center"><div class="text-6xl mb-4" data-svelte-h="svelte-1ikejk4">📄</div> <h2 class="text-xl font-semibold mb-2" data-svelte-h="svelte-1mh8idy">Upload a Recipe</h2> <p class="text-gray-500 mb-6" data-svelte-h="svelte-wvca7e">Upload a PDF or photo of a recipe to automatically extract it</p> <input type="file" accept=".pdf,image/jpeg,image/png,image/webp" class="hidden"> <button type="button" class="btn btn-primary w-full mb-3" data-svelte-h="svelte-u44eeo">Select PDF or Image</button> <p class="text-xs text-gray-400" data-svelte-h="svelte-n9tj7h">Supports PDF, JPEG, PNG, WebP (max 10MB)</p></div> <div class="mt-6" data-svelte-h="svelte-n1k6op"><h3 class="font-medium mb-3">How it works:</h3> <ol class="space-y-3 text-sm text-gray-600"><li class="flex gap-3"><span class="bg-primary text-white w-6 h-6 rounded-full flex items-center justify-center text-sm shrink-0">1</span> <span>Upload a PDF or photo of your recipe</span></li> <li class="flex gap-3"><span class="bg-primary text-white w-6 h-6 rounded-full flex items-center justify-center text-sm shrink-0">2</span> <span>AI extracts the recipe name, ingredients, and instructions</span></li> <li class="flex gap-3"><span class="bg-primary text-white w-6 h-6 rounded-full flex items-center justify-center text-sm shrink-0">3</span> <span>Review and save the recipe to your collection</span></li></ol></div>`}  ${``}  ${``}  ${``}  ${``}</main>`;
});
export {
  Page as default
};
