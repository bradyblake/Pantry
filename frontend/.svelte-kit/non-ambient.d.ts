
// this file is generated — do not edit it


declare module "svelte/elements" {
	export interface HTMLAttributes<T> {
		'data-sveltekit-keepfocus'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-noscroll'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-preload-code'?:
			| true
			| ''
			| 'eager'
			| 'viewport'
			| 'hover'
			| 'tap'
			| 'off'
			| undefined
			| null;
		'data-sveltekit-preload-data'?: true | '' | 'hover' | 'tap' | 'off' | undefined | null;
		'data-sveltekit-reload'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-replacestate'?: true | '' | 'off' | undefined | null;
	}
}

export {};


declare module "$app/types" {
	export interface AppTypes {
		RouteId(): "/" | "/add" | "/freezer" | "/freezer/add" | "/inventory" | "/recipes" | "/recipes/add" | "/recipes/upload" | "/recipes/[id]" | "/settings" | "/shopping" | "/use";
		RouteParams(): {
			"/recipes/[id]": { id: string }
		};
		LayoutParams(): {
			"/": { id?: string };
			"/add": Record<string, never>;
			"/freezer": Record<string, never>;
			"/freezer/add": Record<string, never>;
			"/inventory": Record<string, never>;
			"/recipes": { id?: string };
			"/recipes/add": Record<string, never>;
			"/recipes/upload": Record<string, never>;
			"/recipes/[id]": { id: string };
			"/settings": Record<string, never>;
			"/shopping": Record<string, never>;
			"/use": Record<string, never>
		};
		Pathname(): "/" | "/add" | "/add/" | "/freezer" | "/freezer/" | "/freezer/add" | "/freezer/add/" | "/inventory" | "/inventory/" | "/recipes" | "/recipes/" | "/recipes/add" | "/recipes/add/" | "/recipes/upload" | "/recipes/upload/" | `/recipes/${string}` & {} | `/recipes/${string}/` & {} | "/settings" | "/settings/" | "/shopping" | "/shopping/" | "/use" | "/use/";
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): "/favicon.png" | string & {};
	}
}