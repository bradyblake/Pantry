<script lang="ts">
	import { uncheckedCount } from '../stores';

	export let title: string = 'PantryPal';
	export let showBack: boolean = false;
	export let backHref: string = '/';

	$: isHome = title === 'PantryPal';
</script>

<header class="glass border-b border-gray-200/50 sticky top-0 z-50 shadow-sm">
	<div class="flex items-center justify-between px-4 py-3">
		<div class="flex items-center gap-3">
			{#if showBack}
				<a
					href={backHref}
					class="p-2 -ml-2 rounded-xl hover:bg-gray-100 active:bg-gray-200 transition-colors"
				>
					<svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
					</svg>
				</a>
			{:else if isHome}
				<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center shadow-md">
					<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
					</svg>
				</div>
			{/if}
			<div>
				{#if isHome}
					<h1 class="text-xl font-bold text-gradient">{title}</h1>
					<p class="text-xs text-gray-400">Smart Pantry Manager</p>
				{:else}
					<h1 class="text-xl font-bold text-gray-900">{title}</h1>
				{/if}
			</div>
		</div>

		<div class="flex items-center gap-1">
			<a
				href="/shopping"
				class="relative p-2.5 rounded-xl hover:bg-gray-100 active:bg-gray-200 transition-colors"
			>
				<svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
				</svg>
				{#if $uncheckedCount > 0}
					<span class="absolute -top-0.5 -right-0.5 bg-gradient-to-r from-primary-500 to-primary-600 text-white text-xs font-bold rounded-full min-w-[20px] h-5 px-1 flex items-center justify-center shadow-md animate-fade-in">
						{$uncheckedCount > 9 ? '9+' : $uncheckedCount}
					</span>
				{/if}
			</a>
			<a
				href="/settings"
				class="p-2.5 rounded-xl hover:bg-gray-100 active:bg-gray-200 transition-colors"
			>
				<svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
				</svg>
			</a>
		</div>
	</div>
</header>
