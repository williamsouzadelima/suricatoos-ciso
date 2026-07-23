<script lang="ts">
	import { handlers } from 'svelte/legacy';
	import { page } from '$app/state';

	import CreateModal from '$lib/components/Modals/CreateModal.svelte';
	import ExportModal, {
		type ExportGroup,
		type ExportOption
	} from '$lib/components/Modals/ExportModal.svelte';
	import ModelTable from '$lib/components/ModelTable/ModelTable.svelte';
	import { buildCustomFieldFilters, listViewFields } from '$lib/utils/table';
	import { safeTranslate } from '$lib/utils/i18n';
	import { driverInstance } from '$lib/utils/stores';
	import { m } from '$paraglide/messages';
	import type { ActionData, PageData } from './$types';
	import Anchor from '$lib/components/Anchor/Anchor.svelte';
	import { onMount } from 'svelte';
	import {
		getModalStore,
		type ModalComponent,
		type ModalSettings,
		type ModalStore
	} from '$lib/components/Modals/stores';
	import { getToastStore } from '$lib/components/Toast/stores';
	import { invalidateAll } from '$app/navigation';

	interface Props {
		data: PageData;
		form: ActionData;
	}

	let { data, form }: Props = $props();

	let catHero = $state<{ count: number; byCrit: Record<string, number>; maintenance: number } | null>(null);
	onMount(async () => {
		if (data.URLModel === 'business-catalogs') {
			try {
				const r = await fetch('/business-catalogs/summary');
				if (r.ok) catHero = await r.json();
			} catch (e) {
				/* hero é decorativo — ignora falha */
			}
		}
	});

	let depHero = $state<{ count: number; catalogs: number; withAsset: number } | null>(null);
	onMount(async () => {
		if (data.URLModel === 'catalog-dependencies') {
			try {
				const r = await fetch('/catalog-dependencies/summary');
				if (r.ok) depHero = await r.json();
			} catch (e) {
				/* hero é decorativo — ignora falha */
			}
		}
	});
	const toastStore = getToastStore();
	let URLModel = $derived(data.URLModel);
	// Static (per-model) filters merged with dynamic custom-field filters.
	const tableFilters = $derived({
		...listViewFields[URLModel]?.filters,
		...buildCustomFieldFilters(data.customFields ?? [])
	});
	let pullCatalogOpen = $state(false);
	let currentFilterSearch = $state(page.url.search);

	function handleFilterChange(filters: Record<string, any>) {
		const params = new URLSearchParams();
		for (const [field, values] of Object.entries(filters)) {
			if (Array.isArray(values)) {
				for (const v of values) {
					if (v?.value) params.append(field, v.value);
				}
			}
		}
		const search = params.toString();
		currentFilterSearch = search ? `?${search}` : '';
	}

	const modalStore: ModalStore = getModalStore();

	function buildTableExportOptions(filterSearch: string): ExportOption[] {
		const opts: ExportOption[] = [
			{
				titleKey: 'exportTableCsv',
				descriptionKey: 'exportTableCsvDesc',
				format: 'CSV',
				href: `${URLModel}/export/${filterSearch}`,
				testId: filterSearch ? 'export-option-csv-filtered' : 'export-option-csv-all'
			},
			{
				titleKey: 'exportTableXlsx',
				descriptionKey: 'exportTableXlsxDesc',
				format: 'XLSX',
				href: `${URLModel}/export/xlsx/${filterSearch}`,
				testId: filterSearch ? 'export-option-xlsx-filtered' : 'export-option-xlsx-all'
			}
		];
		if (URLModel === 'entities') {
			opts.push({
				titleKey: 'exportTableEcosystem',
				descriptionKey: 'exportTableEcosystemDesc',
				format: 'XLSX',
				href: `/entities/export/ecosystem/${filterSearch}`,
				testId: filterSearch ? 'export-option-ecosystem-filtered' : 'export-option-ecosystem-all'
			});
		}
		if (URLModel === 'applied-controls') {
			opts.push({
				titleKey: 'exportTableMss',
				descriptionKey: 'exportTableMssDesc',
				format: 'XLSX',
				href: `/applied-controls/export/mss-xlsx/${filterSearch}`,
				testId: filterSearch ? 'export-option-mss-filtered' : 'export-option-mss-all'
			});
		}
		return opts;
	}

	function modalExport(): void {
		const hasFilters = currentFilterSearch.length > 0;
		const groups: ExportGroup[] = hasFilters
			? [
					{
						titleKey: 'exportGroupCurrentView',
						options: buildTableExportOptions(currentFilterSearch)
					},
					{ titleKey: 'exportGroupEntireTable', options: buildTableExportOptions('') }
				]
			: [{ titleKey: '', options: buildTableExportOptions('') }];

		const modalComponent: ModalComponent = {
			ref: ExportModal,
			props: {
				title: m.exportOptionsTitle(),
				groups
			}
		};
		const modal: ModalSettings = {
			type: 'component',
			component: modalComponent
		};
		modalStore.trigger(modal);
	}

	function modalCreateForm(): void {
		let modalComponent: ModalComponent = {
			ref: CreateModal,
			props: {
				form: data.createForm,
				model: data.model
			}
		};
		let modal: ModalSettings = {
			type: 'component',
			component: modalComponent,
			// Data
			title: safeTranslate('add-' + data.model.localName)
		};
		modalStore.trigger(modal);
	}

	function modalFolderImportForm(): void {
		let modalComponent: ModalComponent = {
			ref: CreateModal,
			props: {
				form: data.model['folderImportForm'],
				model: data.model['folderImportModel'],
				importFolder: true,
				formAction: '?/importFolder',
				enctype: 'multipart/form-data',
				dataType: 'form'
			}
		};
		let modal: ModalSettings = {
			type: 'component',
			component: modalComponent,
			// Data
			title: safeTranslate('importFolder')
		};
		modalStore.trigger(modal);
	}

	function handleKeyDown(event: KeyboardEvent) {
		if (event.metaKey || event.ctrlKey) return;
		if (document.activeElement?.tagName !== 'BODY') return;

		// Check if 'c' is pressed and no input fields are currently focused
		if (
			event.key.toLowerCase() === 'c' &&
			document.activeElement?.tagName !== 'INPUT' &&
			document.activeElement?.tagName !== 'TEXTAREA'
		) {
			// Prevent default 'c' key behavior
			event.preventDefault();

			// Check if the add button exists and is not in a disabled list
			if (
				![
					'risk-matrices',
					'frameworks',
					'requirement-mapping-sets',
					'user-groups',
					'role-assignments'
				].includes(URLModel)
			) {
				modalCreateForm();
			}
		}
	}

	function handleClickForGT() {
		setTimeout(() => {
			$driverInstance?.moveNext();
		}, 300);
	}
	onMount(() => {
		// Add event listener when component mounts
		window.addEventListener('keydown', handleKeyDown);

		// Cleanup event listener when component is destroyed
		return () => {
			window.removeEventListener('keydown', handleKeyDown);
		};
	});
</script>

{#if URLModel === 'business-catalogs'}
	<section
		class="mb-4 overflow-hidden rounded-2xl text-white shadow-xl"
		style="background: linear-gradient(135deg, oklch(49% 0.20 283deg), oklch(43% 0.19 302deg) 58%, oklch(47% 0.17 328deg));"
	>
		<div class="relative p-6 sm:p-8">
			<div
				class="pointer-events-none absolute inset-0"
				style="background: radial-gradient(520px 240px at 88% -10%, rgba(255,255,255,.18), transparent 60%), radial-gradient(420px 220px at -5% 115%, rgba(236,132,205,.26), transparent 55%);"
			></div>
			<div class="relative flex flex-wrap items-center justify-between gap-6">
				<div class="min-w-0">
					<div class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-white/70">
						<i class="fa-solid fa-boxes-stacked"></i> Módulo · Entrega vCISO
					</div>
					<h1
						class="mt-2 text-3xl font-bold leading-tight sm:text-4xl"
						style="font-family: 'Geist', ui-sans-serif, sans-serif; letter-spacing: -0.02em;"
					>
						Catálogos de negócio
					</h1>
					<p class="mt-2 max-w-2xl text-sm text-white/80">
						Mapeie as capacidades de negócio do cliente, suas dependências tecnológicas e o custo de
						mantê-las — e calcule o prejuízo de indisponibilidade por hora.
					</p>
					<div class="mt-4 flex flex-wrap gap-2">
						<a
							href="/catalog-dependencies"
							class="inline-flex items-center gap-2 rounded-lg border border-white/20 bg-white/[0.12] px-3.5 py-2 text-sm font-semibold transition-colors hover:bg-white/[0.24]"
						>
							<i class="fa-solid fa-diagram-project"></i>Dependências tecnológicas
						</a>
					</div>
				</div>
				<div class="text-center">
					<div class="text-5xl font-bold" style="font-family: 'Geist', sans-serif;">
						{catHero?.count ?? '—'}
					</div>
					<div class="text-xs uppercase tracking-wide text-white/70">Catálogos</div>
				</div>
			</div>
			<div class="relative mt-5 grid grid-cols-2 gap-px overflow-hidden rounded-xl bg-white/10 sm:grid-cols-4">
				{#each [['critical', 'Crítico'], ['high', 'Alto'], ['medium', 'Médio'], ['low', 'Baixo']] as [k, lbl]}
					<div class="bg-white/[0.04] px-4 py-3">
						<div class="text-2xl font-bold" style="font-family: 'Geist', sans-serif;">
							{catHero?.byCrit?.[k] ?? 0}
						</div>
						<div class="text-xs uppercase tracking-wide text-white/70">{lbl}</div>
					</div>
				{/each}
			</div>
		</div>
	</section>
{/if}

{#if URLModel === 'catalog-dependencies'}
	<section
		class="mb-4 overflow-hidden rounded-2xl text-white shadow-xl"
		style="background: linear-gradient(135deg, oklch(47% 0.19 268deg), oklch(44% 0.19 292deg) 55%, oklch(48% 0.18 315deg));"
	>
		<div class="relative p-6 sm:p-8">
			<div
				class="pointer-events-none absolute inset-0"
				style="background: radial-gradient(520px 240px at 88% -10%, rgba(255,255,255,.16), transparent 60%), radial-gradient(420px 220px at -5% 115%, rgba(129,127,245,.30), transparent 55%);"
			></div>
			<div class="relative flex flex-wrap items-center justify-between gap-6">
				<div class="min-w-0">
					<div class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-white/70">
						<i class="fa-solid fa-diagram-project"></i> Módulo · Entrega vCISO
					</div>
					<h1
						class="mt-2 text-3xl font-bold leading-tight sm:text-4xl"
						style="font-family: 'Geist', ui-sans-serif, sans-serif; letter-spacing: -0.02em;"
					>
						Dependências tecnológicas
					</h1>
					<p class="mt-2 max-w-2xl text-sm text-white/80">
						As tecnologias que sustentam cada catálogo de negócio e o custo anual de mantê-las.
					</p>
					<div class="mt-4 flex flex-wrap gap-2">
						<a
							href="/business-catalogs"
							class="inline-flex items-center gap-2 rounded-lg border border-white/20 bg-white/[0.12] px-3.5 py-2 text-sm font-semibold transition-colors hover:bg-white/[0.24]"
						>
							<i class="fa-solid fa-boxes-stacked"></i>Catálogos de negócio
						</a>
					</div>
				</div>
				<div class="text-center">
					<div class="text-5xl font-bold" style="font-family: 'Geist', sans-serif;">
						{depHero?.count ?? '—'}
					</div>
					<div class="text-xs uppercase tracking-wide text-white/70">Dependências</div>
				</div>
			</div>
			<div class="relative mt-5 grid grid-cols-1 gap-px overflow-hidden rounded-xl bg-white/10 sm:grid-cols-3">
				<div class="bg-white/[0.04] px-4 py-3">
					<div class="text-2xl font-bold" style="font-family: 'Geist', sans-serif;">{depHero?.catalogs ?? 0}</div>
					<div class="text-xs uppercase tracking-wide text-white/70">Catálogos cobertos</div>
				</div>
				<div class="bg-white/[0.04] px-4 py-3">
					<div class="text-2xl font-bold" style="font-family: 'Geist', sans-serif;">{depHero?.withAsset ?? 0}</div>
					<div class="text-xs uppercase tracking-wide text-white/70">Com ativo vinculado</div>
				</div>
				<div class="bg-white/[0.04] px-4 py-3">
					<div class="text-2xl font-bold" style="font-family: 'Geist', sans-serif;">{(depHero?.count ?? 0) - (depHero?.withAsset ?? 0)}</div>
					<div class="text-xs uppercase tracking-wide text-white/70">Sem ativo</div>
				</div>
			</div>
		</div>
	</section>
{/if}

{#if data?.table}
	<div class="shadow-lg">
		{#key URLModel}
			<ModelTable
				source={data.table}
				{tableFilters}
				deleteForm={data.deleteForm}
				{URLModel}
				disableEdit={['user-groups', 'validation-flows'].includes(URLModel)}
				disableDelete={['user-groups'].includes(URLModel)}
				onFilterChange={handleFilterChange}
			>
				{#snippet addButton()}
					<div class="relative">
						<div class="inline-flex overflow-hidden rounded-md border bg-surface-50-950 shadow-xs">
							{#if !['risk-matrices', 'frameworks', 'requirement-mapping-sets', 'user-groups', 'role-assignments', 'qualifications'].includes(URLModel)}
								<button
									class="inline-block p-3 btn-mini-primary w-12 focus:relative"
									data-testid="add-button"
									id="add-button"
									title={safeTranslate('add-' + data.model.localName)}
									aria-label={safeTranslate('add-' + data.model.localName)}
									onclick={handlers(modalCreateForm, handleClickForGT)}
									><i class="fa-solid fa-file-circle-plus"></i>
								</button>
								{#if ['applied-controls', 'assets', 'incidents', 'security-exceptions', 'risk-scenarios', 'processings', 'task-templates', 'entities', 'solutions', 'contracts'].includes(URLModel)}
									<button
										class="inline-block p-3 btn-mini-tertiary w-12 focus:relative"
										title={m.exportButton()}
										data-testid="export-button"
										onclick={modalExport}
									>
										<i class="fa-solid fa-download"></i>
									</button>
								{/if}
								{#if URLModel === 'vulnerabilities'}
									<button
										class="inline-block p-3 btn-mini-tertiary w-12 focus:relative"
										title={m.refreshDueDates()}
										aria-label={m.refreshDueDates()}
										data-testid="refresh-due-dates-button"
										onclick={() => {
											modalStore.trigger({
												type: 'confirm',
												title: m.refreshDueDates(),
												body: m.refreshDueDatesConfirm(),
												response: async (confirmed) => {
													if (!confirmed) return;
													try {
														const res = await fetch('/vulnerabilities/refresh-due-dates', {
															method: 'POST'
														});
														const result = await res.json();
														toastStore.trigger({
															message: result.detail || result.error,
															preset: res.ok ? 'success' : 'error'
														});
														if (res.ok) invalidateAll();
													} catch {
														toastStore.trigger({
															message: m.refreshDueDatesFailed(),
															preset: 'error'
														});
													}
												}
											});
										}}><i class="fa-solid fa-clock-rotate-left"></i></button
									>
								{/if}
								{#if URLModel === 'applied-controls'}
									<a
										href="{URLModel}/flash-mode/{currentFilterSearch}"
										class="inline-block p-3 btn-mini-secondary w-12 focus:relative"
										title={m.flashMode()}
										aria-label={m.flashMode()}
										data-testid="flash-mode-button"><i class="fa-solid fa-bolt mr-2"></i></a
									>
									<a
										href="{URLModel}/kanban-mode/{currentFilterSearch}"
										class="inline-block p-3 btn-mini-quaternary w-12 focus:relative"
										title={m.kanbanMode()}
										aria-label={m.kanbanMode()}
										data-testid="kanban-mode-button"><i class="fa-solid fa-table-columns"></i></a
									>
									<a
										href="{URLModel}/analytics/{currentFilterSearch}"
										class="inline-block p-3 btn-mini-secondary w-12 focus:relative"
										title={m.appliedControlsAnalytics()}
										aria-label={m.appliedControlsAnalytics()}
										data-testid="analytics-button"><i class="fa-solid fa-chart-pie"></i></a
									>
								{/if}
								{#if URLModel === 'security-advisories'}
									<button
										class="inline-block p-3 w-12 focus:relative bg-blue-100 hover:bg-blue-200 dark:bg-blue-500/20 dark:hover:bg-blue-500/30"
										title={m.syncKev()}
										aria-label={m.syncKev()}
										data-testid="sync-kev-button"
										onclick={() => {
											modalStore.trigger({
												type: 'confirm',
												title: m.pullCatalog(),
												body: m.syncKev(),
												response: async (confirmed) => {
													if (!confirmed) return;
													try {
														const res = await fetch('/security-advisories/sync-kev', {
															method: 'POST'
														});
														const result = await res.json();
														toastStore.trigger({
															message: result.detail || result.error,
															preset: res.ok ? 'success' : 'error'
														});
														if (res.ok) invalidateAll();
													} catch {
														toastStore.trigger({
															message: m.syncKevFailed(),
															preset: 'error'
														});
													}
												}
											});
										}}>🇺🇸</button
									>
									<button
										class="inline-block p-3 w-12 focus:relative bg-yellow-100 hover:bg-yellow-200 dark:bg-yellow-500/20 dark:hover:bg-yellow-500/30"
										title={m.syncEuvd()}
										aria-label={m.syncEuvd()}
										data-testid="sync-euvd-button"
										onclick={() => {
											modalStore.trigger({
												type: 'confirm',
												title: m.pullCatalog(),
												body: m.syncEuvd(),
												response: async (confirmed) => {
													if (!confirmed) return;
													try {
														const res = await fetch('/security-advisories/sync-euvd', {
															method: 'POST'
														});
														const result = await res.json();
														toastStore.trigger({
															message: result.detail || result.error,
															preset: res.ok ? 'success' : 'error'
														});
														if (res.ok) invalidateAll();
													} catch {
														toastStore.trigger({
															message: m.syncEuvdFailed(),
															preset: 'error'
														});
													}
												}
											});
										}}>🇪🇺</button
									>
								{/if}
								{#if URLModel === 'cwes'}
									<button
										class="inline-block p-3 btn-mini-tertiary w-12 focus:relative"
										title={m.syncCweCatalog()}
										aria-label={m.syncCweCatalog()}
										data-testid="sync-cwe-button"
										onclick={async () => {
											try {
												const res = await fetch('/cwes/sync-catalog', { method: 'POST' });
												const result = await res.json();
												toastStore.trigger({
													message: result.detail || result.error,
													preset: res.ok ? 'success' : 'error'
												});
												if (res.ok) invalidateAll();
											} catch {
												toastStore.trigger({
													message: m.syncCweCatalogFailed(),
													preset: 'error'
												});
											}
										}}><i class="fa-solid fa-satellite-dish"></i></button
									>
								{/if}
								{#if ['threats', 'reference-controls', 'metric-definitions'].includes(URLModel)}
									{@const title =
										URLModel === 'threats'
											? m.importThreats()
											: URLModel === 'reference-controls'
												? m.importReferenceControls()
												: m.importMetricDefinitions()}
									<Anchor
										href={`/libraries?object_type=${URLModel.replace(/-/g, '_')}`}
										label={m.libraries()}
										class="inline-block p-3 btn-mini-tertiary w-12 focus:relative"
										data-testid="import-button"
										id="import-button"
										{title}><i class="fa-solid fa-file-import mr-2"></i></Anchor
									>
								{/if}
								{#if URLModel === 'assets'}
									<Anchor
										href="assets/graph/"
										class="inline-block p-3 btn-mini-secondary w-12 focus:relative"
										title={m.exploreButton()}
										label={m.inspect()}
										data-testid="viz-button"><i class="fa-solid fa-diagram-project"></i></Anchor
									>
								{/if}
								{#if URLModel === 'entities'}
									<Anchor
										href="entities/graph/"
										class="inline-block p-3 btn-mini-secondary w-12 focus:relative"
										title={m.exploreButton()}
										label={m.inspect()}
										data-testid="viz-button"><i class="fa-solid fa-diagram-project"></i></Anchor
									>
								{/if}
								{#if URLModel === 'folders'}
									<button
										class="text-white inline-block border-e p-3 bg-sky-400 hover:bg-sky-300 w-12 focus:relative"
										data-testid="import-button"
										title={safeTranslate('importFolder')}
										aria-label={safeTranslate('importFolder')}
										onclick={modalFolderImportForm}
										><i class="fa-solid fa-file-import"></i>
									</button>
									<Anchor
										href="x-rays/inspect"
										class="inline-block p-3 btn-mini-secondary w-12 focus:relative"
										title={m.exploreButton()}
										label={m.inspect()}
										data-testid="viz-button"><i class="fa-solid fa-diagram-project"></i></Anchor
									>
								{/if}
								{#if URLModel === 'vulnerabilities'}
									<Anchor
										href="vulnerabilities/treemap/"
										class="inline-block p-3 btn-mini-secondary w-12 focus:relative"
										title={m.visualizeButton()}
										label={m.visualize()}
										data-testid="viz-button"><i class="fa-solid fa-chart-pie"></i></Anchor
									>
								{/if}
							{:else if ['risk-matrices', 'frameworks', 'requirement-mapping-sets'].includes(URLModel)}
								{@const href = `/libraries?object_type=${URLModel.replace(/-/g, '_')}`}
								{@const title =
									URLModel === 'risk-matrices'
										? m.importMatrices()
										: URLModel === 'frameworks'
											? m.importFrameworks()
											: m.importMappings()}
								<Anchor
									{href}
									onclick={handleClickForGT}
									label={m.libraries()}
									class="inline-block p-3 btn-mini-tertiary w-12 focus:relative"
									data-testid="import-button"
									id="add-button"
									{title}><i class="fa-solid fa-file-import mr-2"></i></Anchor
								>
								{#if URLModel === 'requirement-mapping-sets'}
									<Anchor
										href="requirement-mapping-sets/graph/"
										class="inline-block p-3 btn-mini-secondary w-12 focus:relative"
										title={m.exploreButton()}
										label={m.inspect()}
										data-testid="viz-button"><i class="fa-solid fa-diagram-project"></i></Anchor
									>
								{/if}
							{/if}
						</div>
					</div>
				{/snippet}
				{#snippet badge(key, row)}
					{#if URLModel === 'risk-assessments'}
						{#if key === 'perimeter' && row.meta.ebios_rm_study}
							<span
								class="badge inline-block bg-amber-100 text-amber-800 text-xs px-2 py-0.5 rounded-md border border-amber-200 rotate-[-6deg] font-semibold uppercase tracking-wide"
								>ebios-rm</span
							>
						{/if}
					{/if}
				{/snippet}
				{#if URLModel === 'risk-assessments'}{/if}
			</ModelTable>
		{/key}
	</div>
{/if}
