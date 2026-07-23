<script lang="ts">
	import { safeTranslate } from '$lib/utils/i18n';
	import { invalidateAll } from '$app/navigation';
	import BurndownChart from '$lib/components/Chart/BurndownChart.svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	let brandingMsg = $state('');
	async function uploadLogo(url: string, file: File | undefined, okMsg: string) {
		if (!file) return;
		const fd = new FormData();
		fd.append('logo', file);
		brandingMsg = 'Enviando…';
		const r = await fetch(url, { method: 'POST', body: fd });
		brandingMsg = r.ok ? okMsg : 'Falha no envio.';
		if (r.ok) await invalidateAll();
	}
	async function removeClientLogo(engId: string) {
		const r = await fetch(`/engagements/${engId}/logo`, { method: 'DELETE' });
		if (r.ok) {
			brandingMsg = 'Logo do cliente removido.';
			await invalidateAll();
		}
	}
	let domainInput = $state(data.engagement?.website ?? '');
	async function fetchLogoByDomain(engId: string) {
		if (!domainInput.trim()) return;
		brandingMsg = safeTranslate('fetchingLogo');
		const r = await fetch(`/engagements/${engId}/fetch-logo`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ domain: domainInput.trim() })
		});
		if (r.ok) {
			const d = await r.json();
			if (d.found) {
				brandingMsg =
					safeTranslate('logoFound') + (d.low_res ? ` — ${safeTranslate('lowRes')}` : '');
				await invalidateAll();
			} else {
				brandingMsg = safeTranslate('logoNotFound');
			}
		} else {
			brandingMsg = safeTranslate('logoNotFound');
		}
	}

	const eng = $derived(data.engagement);
	const cap = $derived(data.capacity);
	const dash = $derived(data.dashboard);
	const folderId = $derived(eng?.folder?.id ?? '');
	const tr = $derived(data.teamResources);
	const bd = $derived(data.burnDown);
	const catSummary = $derived(data.catalogsSummary);

	const PLAN_MODULES = [
		{ key: 'anbima', label: 'ANBIMA — Gestora / Asset' },
		{ key: 'cvm', label: 'CVM — Corretora / DTVM / Adm. de carteiras' },
		{ key: 'bacen', label: 'BACEN — Banco / Instituição financeira' },
		{ key: 'lgpd', label: 'LGPD — Privacidade' }
	];
	let selectedModules = $state<string[]>([]);
	let seeding = $state(false);
	let seedMsg = $state('');
	async function applyModules(engId: string) {
		seeding = true;
		seedMsg = safeTranslate('seeding');
		const r = await fetch(`/engagements/${engId}/seed-plan`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ modules: selectedModules })
		});
		if (r.ok) {
			const d = await r.json();
			const n = (d?.plan_tasks ?? 0) as number;
			seedMsg = n ? safeTranslate('modulesAdded') + ` (+${n})` : safeTranslate('planUpToDate');
			selectedModules = [];
			await invalidateAll();
		} else {
			seedMsg = safeTranslate('seedFailed');
		}
		seeding = false;
	}

	const utilization = $derived(Math.round(cap?.utilization_pct ?? 0));
	const barWidth = $derived(Math.min(utilization, 100));
	const overBudget = $derived(cap?.over_budget ?? false);

	const kanbanHref = $derived(
		`/applied-controls/kanban-mode/?folder=${folderId}&backUrl=/engagements/${eng?.id}&backLabel=${encodeURIComponent(eng?.name ?? 'Engagement')}`
	);

	const quadrants = [
		{ key: 'do', label: 'quadrantDo', color: 'text-red-600 dark:text-red-400' },
		{ key: 'schedule', label: 'quadrantSchedule', color: 'text-blue-600 dark:text-blue-400' },
		{ key: 'delegate', label: 'quadrantDelegate', color: 'text-amber-600 dark:text-amber-400' },
		{ key: 'eliminate', label: 'quadrantEliminate', color: 'text-surface-600-400' }
	];
</script>

<div class="p-4 space-y-6">
	<!-- HERO redesenhado -->
	<section class="st-hero">
		<div class="st-hero-glow" aria-hidden="true"></div>
		<div class="st-hero-top">
			<div class="st-hero-id">
				<div class="st-eyebrow"><i class="fa-solid fa-shield-halved"></i> Engajamento vCISO</div>
				<h1 class="st-hero-title">{eng?.name}</h1>
				<div class="st-hero-sub">
					<span class="st-pill">{safeTranslate(eng?.status)}</span>
					{#if eng?.folder?.str}<span class="st-dot">·</span><span>{eng.folder.str}</span>{/if}
					{#if eng?.day_zero}<span class="st-dot">·</span><span>{safeTranslate('dayZero')} {eng.day_zero}</span>{/if}
				</div>
				<div class="st-hero-actions">
					<a class="st-btn st-btn-primary" href="/engagements/{eng?.id}/plan"><i class="fa-solid fa-diagram-project"></i>{safeTranslate('viewPlan')}</a>
					<a class="st-btn" href="/engagements/{eng?.id}/eisenhower"><i class="fa-solid fa-table-cells-large"></i>{safeTranslate('eisenhowerMatrix')}</a>
					{#if folderId}<a class="st-btn" href={kanbanHref}><i class="fa-solid fa-columns"></i>{safeTranslate('openClientKanban')}</a>{/if}
					<a class="st-btn" href="/my-assignments"><i class="fa-solid fa-list-check"></i>{safeTranslate('myAssignments')}</a>
					<a class="st-btn" href="/engagements/{eng?.id}/export/pptx"><i class="fa-solid fa-file-powerpoint"></i>{safeTranslate('exportPptx')}</a>
				</div>
			</div>
			<div class="st-gauge" class:over={overBudget}>
				<svg viewBox="0 0 120 120">
					<circle class="st-gauge-track" cx="60" cy="60" r="52" />
					<circle class="st-gauge-arc" cx="60" cy="60" r="52" style="stroke-dasharray: {2 * Math.PI * 52}; stroke-dashoffset: {2 * Math.PI * 52 * (1 - barWidth / 100)};" />
				</svg>
				<div class="st-gauge-center">
					<div class="st-gauge-num">{utilization}%</div>
					<div class="st-gauge-cap">{overBudget ? safeTranslate('overBudget') : safeTranslate('capacity')}</div>
				</div>
			</div>
		</div>
		<div class="st-kpis">
			<div class="st-kpi"><div class="st-kpi-num">{cap?.contracted_hours ?? '—'}</div><div class="st-kpi-lbl">{safeTranslate('contractedHours')}</div></div>
			<div class="st-kpi"><div class="st-kpi-num">{cap?.estimated_hours ?? 0}</div><div class="st-kpi-lbl">{safeTranslate('estimatedHours')}</div></div>
			<div class="st-kpi"><div class="st-kpi-num">{cap?.logged_hours ?? 0}</div><div class="st-kpi-lbl">{safeTranslate('loggedHours')}</div></div>
			<div class="st-kpi"><div class="st-kpi-num">{(dash?.phases ?? []).reduce((sum, ph) => sum + (ph.task_count || 0), 0)}</div><div class="st-kpi-lbl">{safeTranslate('tasks')}</div></div>
		</div>
	</section>

	<!-- burn-down de horas -->
	<section class="rounded-lg border border-surface-200-800 p-4 space-y-3">
		<div class="flex items-center justify-between">
			<h2 class="text-lg font-semibold">{safeTranslate('burnDown')}</h2>
			<a class="text-sm text-primary-500 hover:underline" href="/time-entries">{safeTranslate('logHours')} →</a>
		</div>
		{#if bd && bd.logged_total > 0}
			<BurndownChart
				name={eng?.id}
				actual={bd.actual}
				ideal={bd.ideal}
				labelActual={safeTranslate('actualBurn')}
				labelIdeal={safeTranslate('idealBurn')}
			/>
			<div class="grid grid-cols-3 gap-3 text-sm">
				<div><div class="text-surface-600-400">{safeTranslate('budgetHours')}</div><div class="text-lg font-semibold">{bd.budget ?? '—'}</div></div>
				<div><div class="text-surface-600-400">{safeTranslate('hoursLogged')}</div><div class="text-lg font-semibold">{bd.logged_total}</div></div>
				<div><div class="text-surface-600-400">{safeTranslate('remainingHours')}</div><div class="text-lg font-semibold">{bd.budget != null ? Math.max(bd.budget - bd.logged_total, 0) : '—'}</div></div>
			</div>
		{:else}
			<div class="rounded-lg border border-dashed border-surface-300-700 p-4 text-sm text-surface-600-400">
				{safeTranslate('noTimeLogged')} · <a class="text-primary-500 hover:underline" href="/time-entries">{safeTranslate('logHours')}</a>
			</div>
		{/if}
	</section>

	<!-- fases -->
	<section class="space-y-3">
		<h2 class="text-lg font-semibold">{safeTranslate('byPhase')}</h2>
		<div class="grid grid-cols-1 gap-3 md:grid-cols-3">
			{#each dash?.phases ?? [] as ph (ph.phase)}
				<div class="rounded-lg border border-surface-200-800 p-4 space-y-2">
					<div class="text-sm font-semibold">{ph.name}</div>
					<div class="text-xs text-surface-600-400">{ph.date_start ?? ''} → {ph.date_end ?? ''}</div>
					<div class="flex items-center justify-between text-sm">
						<span>{ph.task_count} {safeTranslate('tasks')}</span>
						<span class="font-medium">{ph.estimated_hours}h</span>
					</div>
					<div class="h-2 w-full overflow-hidden rounded-full bg-surface-200-800">
						<div class="h-full rounded-full bg-primary-500" style="width: {ph.task_count ? Math.round((ph.done_count / ph.task_count) * 100) : 0}%"></div>
					</div>
					<div class="text-xs text-surface-600-400">{ph.done_count}/{ph.task_count} {safeTranslate('done')}</div>
				</div>
			{/each}
		</div>
	</section>

	<!-- módulos regulatórios / plano -->
	<section class="rounded-lg border border-surface-200-800 p-4 space-y-3">
		<div class="flex items-center justify-between">
			<h2 class="text-lg font-semibold">{safeTranslate('regulatoryModules')}</h2>
			{#if seedMsg}<span class="text-xs text-primary-500">{seedMsg}</span>{/if}
		</div>
		<p class="text-sm text-surface-600-400">{safeTranslate('regulatoryModulesHint')}</p>
		<div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
			{#each PLAN_MODULES as mod}
				<label class="flex items-center gap-2 rounded-md border border-surface-200-800 p-2 text-sm">
					<input type="checkbox" bind:group={selectedModules} value={mod.key} />
					{mod.label}
				</label>
			{/each}
		</div>
		<button
			type="button"
			disabled={seeding}
			class="rounded-md bg-primary-500 px-3 py-2 text-sm font-medium text-white hover:bg-primary-600 disabled:opacity-50"
			onclick={() => applyModules(eng?.id)}
		>
			<i class="fa-solid fa-layer-group mr-1"></i>{safeTranslate('addToPlan')}
		</button>
	</section>

	<!-- eisenhower resumo -->
	<section class="space-y-3">
		<div class="flex items-center justify-between">
			<h2 class="text-lg font-semibold">{safeTranslate('eisenhowerMatrix')}</h2>
			<a class="text-sm text-primary-500 hover:underline" href="/engagements/{eng?.id}/eisenhower">{safeTranslate('viewEisenhower')} →</a>
		</div>
		<div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
			{#each quadrants as qd}
				<div class="rounded-lg border border-surface-200-800 p-4 text-center">
					<div class="text-3xl font-bold {qd.color}">{dash?.eisenhower?.[qd.key] ?? 0}</div>
					<div class="mt-1 text-xs text-surface-600-400">{safeTranslate(qd.label)}</div>
				</div>
			{/each}
		</div>
	</section>

	<!-- time de entrega -->
	<section class="space-y-3">
		<div class="flex items-center justify-between">
			<h2 class="text-lg font-semibold">{safeTranslate('deliveryTeam')}</h2>
			<a class="text-sm text-primary-500 hover:underline" href="/role-assignments">{safeTranslate('manageAccess')} →</a>
		</div>
		{#if tr?.team?.length}
			<div class="overflow-x-auto rounded-lg border border-surface-200-800">
				<table class="w-full text-sm">
					<tbody>
						{#each tr.team as m}
							<tr class="border-t border-surface-200-800 first:border-t-0">
								<td class="p-3">
									<i class="fa-solid {m.kind === 'group' ? 'fa-users' : 'fa-user'} mr-2 text-surface-500"></i>{m.name}
								</td>
								<td class="p-3 text-right text-surface-600-400">{m.role}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{:else}
			<div class="rounded-lg border border-dashed border-surface-300-700 p-4 text-sm text-surface-600-400">
				{safeTranslate('noTeamYet')} · <a class="text-primary-500 hover:underline" href="/role-assignments">{safeTranslate('addTeamMember')}</a>
			</div>
		{/if}
	</section>

	<!-- recursos do cliente -->
	<section class="space-y-3">
		<div class="flex items-center justify-between">
			<h2 class="text-lg font-semibold">{safeTranslate('clientResources')}</h2>
			<a class="text-sm text-primary-500 hover:underline" href="/assets">{safeTranslate('manageAssets')} →</a>
		</div>
		{#if tr?.resources?.length}
			<div class="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
				{#each tr.resources as r (r.id)}
					<div class="rounded-lg border border-surface-200-800 p-4">
						<div class="flex items-center justify-between gap-2">
							<span class="font-medium">{r.name}</span>
							<span class="whitespace-nowrap rounded-full bg-surface-200-800 px-2 py-0.5 text-xs">{r.type}</span>
						</div>
						{#if r.description}<p class="mt-1 text-xs text-surface-600-400">{r.description}</p>{/if}
					</div>
				{/each}
			</div>
		{:else}
			<div class="rounded-lg border border-dashed border-surface-300-700 p-4 text-sm text-surface-600-400">
				{safeTranslate('noResourcesYet')} · <a class="text-primary-500 hover:underline" href="/assets">{safeTranslate('addResource')}</a>
			</div>
		{/if}
	</section>

	<!-- catálogos de negócio -->
	<section class="space-y-3">
		<div class="flex items-center justify-between">
			<h2 class="text-lg font-semibold">{safeTranslate('businessCatalogs')}</h2>
			<a class="text-sm text-primary-500 hover:underline" href="/business-catalogs">{safeTranslate('manageCatalogs')} →</a>
		</div>
		{#if catSummary?.count}
			<div class="grid grid-cols-1 gap-3 text-sm sm:grid-cols-3">
				<div class="rounded-lg border border-surface-200-800 p-4">
					<div class="text-surface-600-400">{safeTranslate('catalogsCount')}</div>
					<div class="text-2xl font-bold">{catSummary.count}</div>
				</div>
				<div class="rounded-lg border border-surface-200-800 p-4">
					<div class="text-surface-600-400">{safeTranslate('totalMaintenanceAnnual')}</div>
					<div class="text-2xl font-bold">{catSummary.total_maintenance_annual_fmt}</div>
				</div>
				<div class="rounded-lg border border-surface-200-800 p-4">
					<div class="text-surface-600-400">{safeTranslate('totalLossPerHour')}</div>
					<div class="text-2xl font-bold text-red-600 dark:text-red-400">{catSummary.total_loss_hourly_fmt}</div>
				</div>
			</div>
			<div class="overflow-x-auto rounded-lg border border-surface-200-800">
				<table class="w-full text-sm">
					<thead>
						<tr class="border-b border-surface-200-800 text-left text-surface-600-400">
							<th class="p-3 font-medium">{safeTranslate('name')}</th>
							<th class="p-3 font-medium">{safeTranslate('criticality')}</th>
							<th class="p-3 text-right font-medium">{safeTranslate('maintenanceCost')}</th>
							<th class="p-3 text-right font-medium">{safeTranslate('totalLossPerHour')}</th>
							<th class="p-3"></th>
						</tr>
					</thead>
					<tbody>
						{#each catSummary.catalogs as c (c.id)}
							<tr class="border-t border-surface-200-800 first:border-t-0">
								<td class="p-3 font-medium">{c.name}</td>
								<td class="p-3">{safeTranslate(c.criticality)}</td>
								<td class="p-3 text-right">{c.maintenance_annual_fmt}</td>
								<td class="p-3 text-right font-semibold text-red-600 dark:text-red-400">{c.total_hourly_fmt}</td>
								<td class="p-3 text-right">
									<a class="text-primary-500 hover:underline" href="/catalog-impact/{c.id}">{safeTranslate('viewImpact')} →</a>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{:else}
			<div class="rounded-lg border border-dashed border-surface-300-700 p-4 text-sm text-surface-600-400">
				{safeTranslate('noCatalogsYet')} · <a class="text-primary-500 hover:underline" href="/business-catalogs">{safeTranslate('addCatalog')}</a>
			</div>
		{/if}
	</section>

	<!-- branding / identidade visual -->
	<section class="rounded-lg border border-surface-200-800 p-4 space-y-3">
		<div class="flex items-center justify-between">
			<h2 class="text-lg font-semibold">{safeTranslate('branding')}</h2>
			{#if brandingMsg}<span class="text-xs text-primary-500">{brandingMsg}</span>{/if}
		</div>
		<p class="text-sm text-surface-600-400">{safeTranslate('brandingHint')}</p>
		<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
			<div class="space-y-1">
				<div class="text-sm font-medium">{safeTranslate('clientLogo')}</div>
				<div class="text-xs text-surface-600-400">
					{eng?.logo ? safeTranslate('logoSet') : safeTranslate('logoNone')}
				</div>
				<div class="flex gap-2 pt-1">
					<input
						type="url"
						bind:value={domainInput}
						placeholder="ex.: galapagoscapital.com"
						class="min-w-0 flex-1 rounded-md border border-surface-300-700 bg-transparent p-1.5 text-sm"
					/>
					<button
						type="button"
						class="whitespace-nowrap rounded-md bg-primary-500 px-3 py-1.5 text-sm font-medium text-white hover:bg-primary-600"
						onclick={() => fetchLogoByDomain(eng?.id)}
					>
						{safeTranslate('searchByDomain')}
					</button>
				</div>
				<div class="pt-1 text-xs text-surface-600-400">{safeTranslate('orUploadManually')}</div>
				<input
					type="file"
					accept="image/png,image/jpeg"
					class="block text-sm"
					onchange={(e) =>
						uploadLogo(`/engagements/${eng?.id}/logo`, e.currentTarget.files?.[0], safeTranslate('clientLogoUpdated'))}
				/>
				{#if eng?.logo}
					<button type="button" class="text-xs text-red-500 hover:underline" onclick={() => removeClientLogo(eng?.id)}>
						{safeTranslate('remove')}
					</button>
				{/if}
			</div>
			<div class="space-y-1">
				<div class="text-sm font-medium">{safeTranslate('providerLogo')}</div>
				<div class="text-xs text-surface-600-400">{safeTranslate('providerLogoHint')}</div>
				<input
					type="file"
					accept="image/png,image/jpeg"
					class="block text-sm"
					onchange={(e) =>
						uploadLogo(`/engagements/provider-logo`, e.currentTarget.files?.[0], safeTranslate('providerLogoUpdated'))}
				/>
			</div>
		</div>
	</section>
</div>


<style>
	.st-hero {
		position: relative;
		overflow: hidden;
		border-radius: 1.1rem;
		color: #fff;
		background: linear-gradient(135deg, oklch(49% 0.20 283deg), oklch(43% 0.19 302deg) 58%, oklch(47% 0.17 328deg));
		box-shadow: 0 24px 52px -26px oklch(45% 0.2 285deg / 0.75);
	}
	.st-hero-glow {
		position: absolute;
		inset: 0;
		background:
			radial-gradient(520px 260px at 88% -10%, rgba(255, 255, 255, 0.22), transparent 60%),
			radial-gradient(420px 240px at -5% 115%, rgba(236, 132, 205, 0.28), transparent 55%);
		pointer-events: none;
	}
	.st-hero-top {
		position: relative;
		z-index: 1;
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		justify-content: space-between;
		gap: 1.75rem;
		padding: 1.9rem 2rem;
	}
	.st-eyebrow {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.72rem;
		font-weight: 600;
		letter-spacing: 0.14em;
		text-transform: uppercase;
		color: rgba(255, 255, 255, 0.72);
	}
	.st-hero-title {
		font-family: 'Geist', ui-sans-serif, sans-serif;
		font-size: clamp(1.9rem, 4vw, 2.7rem);
		font-weight: 700;
		letter-spacing: -0.02em;
		line-height: 1.05;
		margin: 0.55rem 0 0;
	}
	.st-hero-sub {
		margin-top: 0.6rem;
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.9rem;
		color: rgba(255, 255, 255, 0.82);
	}
	.st-dot { color: rgba(255, 255, 255, 0.4); }
	.st-pill {
		background: rgba(255, 255, 255, 0.16);
		border: 1px solid rgba(255, 255, 255, 0.28);
		padding: 0.15rem 0.7rem;
		border-radius: 999px;
		font-size: 0.76rem;
		font-weight: 600;
	}
	.st-hero-actions {
		margin-top: 1.3rem;
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}
	.st-btn {
		display: inline-flex;
		align-items: center;
		gap: 0.45rem;
		padding: 0.5rem 0.9rem;
		border-radius: 0.65rem;
		font-size: 0.82rem;
		font-weight: 600;
		color: #fff;
		background: rgba(255, 255, 255, 0.12);
		border: 1px solid rgba(255, 255, 255, 0.22);
		transition: background 0.15s ease, transform 0.15s ease;
	}
	.st-btn:hover {
		background: rgba(255, 255, 255, 0.24);
		transform: translateY(-1px);
	}
	.st-btn-primary {
		background: #fff;
		color: oklch(46% 0.2 285deg);
		border-color: #fff;
	}
	.st-btn-primary:hover { background: rgba(255, 255, 255, 0.9); }
	.st-gauge {
		position: relative;
		width: 132px;
		height: 132px;
		flex-shrink: 0;
	}
	.st-gauge svg {
		width: 100%;
		height: 100%;
		transform: rotate(-90deg);
	}
	.st-gauge-track { fill: none; stroke: rgba(255, 255, 255, 0.16); stroke-width: 10; }
	.st-gauge-arc {
		fill: none;
		stroke: #fff;
		stroke-width: 10;
		stroke-linecap: round;
		transition: stroke-dashoffset 0.9s cubic-bezier(0.22, 1, 0.36, 1);
	}
	.st-gauge.over .st-gauge-arc { stroke: oklch(74% 0.17 22deg); }
	.st-gauge-center {
		position: absolute;
		inset: 0;
		display: grid;
		place-content: center;
		text-align: center;
	}
	.st-gauge-num {
		font-family: 'Geist', ui-sans-serif, sans-serif;
		font-size: 1.7rem;
		font-weight: 700;
		line-height: 1;
	}
	.st-gauge-cap {
		margin-top: 0.2rem;
		font-size: 0.64rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: rgba(255, 255, 255, 0.72);
	}
	.st-kpis {
		position: relative;
		z-index: 1;
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 1px;
		background: rgba(255, 255, 255, 0.14);
		border-top: 1px solid rgba(255, 255, 255, 0.14);
	}
	.st-kpi {
		background: linear-gradient(180deg, rgba(255, 255, 255, 0.04), transparent);
		padding: 1.05rem 1.3rem;
	}
	.st-kpi-num {
		font-family: 'Geist', ui-sans-serif, sans-serif;
		font-size: 1.65rem;
		font-weight: 700;
		line-height: 1;
	}
	.st-kpi-lbl {
		margin-top: 0.35rem;
		font-size: 0.72rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: rgba(255, 255, 255, 0.72);
	}
	@media (max-width: 640px) {
		.st-kpis { grid-template-columns: repeat(2, 1fr); }
	}
	@media (prefers-reduced-motion: reduce) {
		.st-gauge-arc, .st-btn { transition: none; }
	}
</style>
