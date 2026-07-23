<script lang="ts">
	import { run } from 'svelte/legacy';

	// Most of your app wide CSS should be put in this file
	import '../../app.css';

	import { AppBar } from '@skeletonlabs/skeleton-svelte';
	import { safeTranslate } from '$lib/utils/i18n';

	import SideBar from '$lib/components/SideBar/SideBar.svelte';
	import Breadcrumbs from '$lib/components/Breadcrumbs/Breadcrumbs.svelte';
	import {
		pageTitle,
		modelName,
		modelDescription,
		clientSideToast,
		getStartedTrigger
	} from '$lib/utils/stores';
	import { getCookie, deleteCookie } from '$lib/utils/cookies';
	import { browser } from '$app/environment';
	import { page } from '$app/stores';
	import { m } from '$paraglide/messages';

	import type { PageData, ActionData } from './$types';
	import { getSidebarVisibleItems } from '$lib/utils/sidebar-config';
	import { getModalStore, type ModalStore } from '$lib/components/Modals/stores';

	import CommandPalette from '$lib/components/CommandPalette/CommandPalette.svelte';
	import ThemeToggle from '$lib/components/ThemeToggle/ThemeToggle.svelte';
	import ChatWidget from '$lib/components/ChatWidget/ChatWidget.svelte';
	import {
		interceptExternalLinks,
		setGlobalModalStore,
		setShowWarningExternalLinks
	} from '$lib/utils/external-links';
	import { onMount } from 'svelte';
	import { initThemeFromUser } from '$lib/utils/theme';

	const isMac = browser && navigator.platform.toUpperCase().indexOf('MAC') >= 0;
	const modifierKey = isMac ? '⌘' : 'Ctrl';

	let commandPalette: ReturnType<typeof CommandPalette> | undefined = $state();

	let sidebarOpen = $state(true);

	let classesSidebarOpen = $derived((open: boolean) => (open ? 'ml-64' : 'ml-[4.5rem]'));

	interface Props {
		data: PageData;
		form: ActionData;
		sideBarVisibleItems?: any;
		children?: import('svelte').Snippet;
	}

	let {
		data,
		form,
		sideBarVisibleItems = getSidebarVisibleItems(data?.featureflags),
		children
	}: Props = $props();

	const modalStore: ModalStore = getModalStore();

	// Display title, model name, and description from either page data or manual store setting
	const displayTitle = $derived($page.data?.title || $pageTitle);

	// Auto-detect model from URL for list pages
	// Match pattern: /model-name or /model-name/ (but not /model-name/uuid or /model-name/something)
	const urlModel = $derived(() => {
		const path = $page.url.pathname;
		const match = path.match(/^\/([a-z-]+)\/?$/);
		return match ? match[1] : null;
	});

	// Generate description key from URL model: "risk-matrices" → "riskMatricesDescription"
	const urlDescriptionKey = $derived(() => {
		const model = urlModel();
		if (!model) return null;

		const camelCase = model
			.split('-')
			.map((word, index) => (index === 0 ? word : word.charAt(0).toUpperCase() + word.slice(1)))
			.join('');
		return `${camelCase}Description`;
	});

	// Determine if we're on a list page vs detail page
	// List page: URL matches /model-name pattern (e.g., /risk-assessments)
	// Detail page: has an object title from loadDetail (e.g., /risk-assessments/uuid)
	const matchesListUrl = $derived(!!urlModel());
	const hasObjectTitle = $derived(!!$page.data?.title);

	// For list pages: show description subtitle
	// For detail pages: show model name subtitle
	const displayModelName = $derived(
		hasObjectTitle ? $page.data?.modelVerboseName || $modelName : ''
	);

	const displayModelDescription = $derived(
		(() => {
			// Only show description on list pages (not on detail pages with object titles)
			// Exception: pages that explicitly provide a modelDescriptionKey
			if (hasObjectTitle && !$page.data?.modelDescriptionKey) return '';
			if (!matchesListUrl && !$page.data?.modelDescriptionKey) return '';

			// List pages: get description from i18n
			const descKey = $page.data?.modelDescriptionKey || urlDescriptionKey();
			if (descKey && m[descKey]) {
				return m[descKey]();
			}

			// Fallback to manual store
			return $modelDescription;
		})()
	);

	// Initialize external link interceptor
	$effect(() => {
		if (browser) {
			setGlobalModalStore(modalStore);
			// Set the warning preference from settings (default to true if not set)
			const showWarning = data?.settings?.show_warning_external_links ?? true;
			setShowWarningExternalLinks(showWarning);
			interceptExternalLinks();
		}
	});

	// Apply the theme persisted in the user's server-side preferences (ui.theme).
	// Falls back to localStorage / system preference when no server value is set.
	onMount(() => {
		initThemeFromUser(data.user?.preferences);
	});

	// Handle login-specific logic
	run(() => {
		if (browser) {
			const fromLogin = getCookie('from_login');
			if (fromLogin === 'true') {
				deleteCookie('from_login');
				fetch('/fe-api/waiting-risk-acceptances').then(async (res) => {
					const data = await res.json();
					const number = data.count ?? 0;
					if (number <= 0) return;
				});
			}
		}
	});

	// $inspect(data);
</script>

<svelte:head>
	<title>Suricatoos CISO | {safeTranslate(displayTitle)}</title>
</svelte:head>

<!-- App Shell -->
<div class="overflow-x-clip">
	<div class="st-ribbon" aria-hidden="true"></div>
	<SideBar bind:open={sidebarOpen} {sideBarVisibleItems} />
	<AppBar
		class="ds-masthead sticky top-0 z-50 transition-all duration-300 w-auto pb-2 px-4 {classesSidebarOpen(
			sidebarOpen
		)}"
	>
		<div class="flex items-start justify-between px-4 pt-2">
			<div class="min-w-0">
				<div class="ds-eyebrow ds-kicker pb-1">
					SURICATOOS vCISO{#if displayModelName} · {safeTranslate(displayModelName)}{/if}
				</div>
				<div
					class="ds-title text-3xl font-semibold tracking-tight leading-tight"
					id="page-title"
				>
					{safeTranslate(displayTitle)}
				</div>
				{#if displayModelDescription}
					<div class="text-xs italic pt-0.5" style="color: var(--color-surface-500)">
						{safeTranslate(displayModelDescription)}
					</div>
				{/if}
			</div>
			<div class="flex items-center gap-2 shrink-0">
				<ThemeToggle />
				{#if !data?.user?.is_third_party}
					<button
						onclick={() => commandPalette?.toggle()}
						aria-label={m.search()}
						class="ds-search flex items-center gap-2 shrink-0 rounded-md px-3 py-1.5 text-xs cursor-pointer"
					>
						<i class="fa-solid fa-magnifying-glass"></i>
						<span class="hidden sm:inline">{m.searchEllipsis()}</span>
						<kbd
							class="hidden sm:inline-flex items-center rounded border border-white/20 px-1.5 py-0.5 font-mono text-[10px]"
							>{modifierKey}K</kbd
						>
					</button>
				{/if}
			</div>
		</div>
		<div class="px-4 pt-1">
			<div class="ds-crumb"><Breadcrumbs /></div>
		</div>
	</AppBar>
	<!-- Router Slot -->
	{#if !data?.user?.is_third_party}
		<CommandPalette bind:this={commandPalette} />
	{/if}
	{#if $page.data.featureflags?.chat_mode}
		<ChatWidget />
	{/if}
	<main
		class="min-h-screen p-8 bg-linear-to-br from-surface-200-800 to-surface-150-850 transition-all duration-300 {classesSidebarOpen(
			sidebarOpen
		)}"
		style="view-transition-name: page-content"
	>
		{@render children?.()}
	</main>
	<!-- ---- / ---- -->
</div>
