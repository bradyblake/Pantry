import { c as create_ssr_component, v as validate_component, d as add_attribute, e as escape, b as each } from "../../../../chunks/ssr.js";
import "@sveltejs/kit/internal";
import "../../../../chunks/exports.js";
import "../../../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../../../chunks/state.svelte.js";
import { H as Header } from "../../../../chunks/Header.js";
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let name = "";
  let prepTime = null;
  let cookTime = null;
  let servings = null;
  let tagsInput = "";
  let ingredients = [];
  let newIngredient = "";
  return `${validate_component(Header, "Header").$$render(
    $$result,
    {
      title: "Add Recipe",
      backLink: "/recipes"
    },
    {},
    {}
  )} <main class="p-4 pb-24">${``} <form> <section class="card p-4 mb-4"><h2 class="font-semibold mb-3" data-svelte-h="svelte-w2ebwr">Basic Info</h2> <div class="mb-4"><label class="block text-sm font-medium mb-1" for="name" data-svelte-h="svelte-x7vwt9">Recipe Name *</label> <input type="text" id="name" class="input w-full" placeholder="e.g., Chicken Alfredo"${add_attribute("value", name, 0)}></div> <div class="mb-4"><label class="block text-sm font-medium mb-1" for="description" data-svelte-h="svelte-1umdsnt">Description</label> <textarea id="description" class="input w-full" rows="2" placeholder="Brief description of the dish">${escape("")}</textarea></div> <div class="flex gap-4 mb-4"><div class="flex-1"><label class="block text-sm font-medium mb-1" for="prep" data-svelte-h="svelte-tbr9xd">Prep Time (min)</label> <input type="number" id="prep" class="input w-full" min="0"${add_attribute("value", prepTime, 0)}></div> <div class="flex-1"><label class="block text-sm font-medium mb-1" for="cook" data-svelte-h="svelte-1tweddr">Cook Time (min)</label> <input type="number" id="cook" class="input w-full" min="0"${add_attribute("value", cookTime, 0)}></div> <div class="flex-1"><label class="block text-sm font-medium mb-1" for="servings" data-svelte-h="svelte-f2u5ux">Servings</label> <input type="number" id="servings" class="input w-full" min="1"${add_attribute("value", servings, 0)}></div></div> <div><label class="block text-sm font-medium mb-1" for="tags" data-svelte-h="svelte-1swkj0f">Tags</label> <input type="text" id="tags" class="input w-full" placeholder="quick, mexican, kid-friendly (comma separated)"${add_attribute("value", tagsInput, 0)}></div></section>  <section class="card p-4 mb-4"><h2 class="font-semibold mb-3" data-svelte-h="svelte-xx4uix">Ingredients</h2> <div class="flex gap-2 mb-4"><input type="text" class="input flex-1" placeholder="e.g., 1 lb ground beef"${add_attribute("value", newIngredient, 0)}> <button type="button" class="btn btn-secondary" data-svelte-h="svelte-17w0c9g">Add</button></div> ${ingredients.length === 0 ? `<p class="text-gray-500 text-sm text-center py-4" data-svelte-h="svelte-us9ptt">No ingredients added yet</p>` : `<ul class="space-y-2">${each(ingredients, (ing, i) => {
    return `<li class="flex items-center gap-2 p-2 bg-gray-50 rounded"><button type="button" class="${"text-xs px-2 py-1 rounded " + escape(
      ing.is_optional ? "bg-gray-200" : "bg-primary/10 text-primary",
      true
    )}">${escape(ing.is_optional ? "Optional" : "Required")}</button> <span class="${"flex-1 " + escape(ing.is_optional ? "text-gray-500" : "", true)}">${escape(ing.ingredient_text)}</span> <button type="button" class="text-red-500 px-2" data-svelte-h="svelte-kd22bc">×</button> </li>`;
  })}</ul>`}</section>  <section class="card p-4 mb-4"><h2 class="font-semibold mb-3" data-svelte-h="svelte-10yxxny">Instructions</h2> <textarea class="input w-full" rows="8" placeholder="Step by step cooking instructions...">${escape("")}</textarea></section>  <button type="submit" class="btn btn-primary w-full" ${!name.trim() ? "disabled" : ""}>${escape("Save Recipe")}</button></form></main>`;
});
export {
  Page as default
};
