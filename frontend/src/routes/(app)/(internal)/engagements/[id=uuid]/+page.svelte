<script lang="ts">
	import { safeTranslate } from '$lib/utils/i18n';
	import BurndownChart from '$lib/components/Chart/BurndownChart.svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const eng = $derived(data.engagement);
	const cap = $derived(data.capacity);
	const dash = $derived(data.dashboard);
	const folderId = $derived(eng?.folder?.id ?? '');
	const tr = $derived(data.teamResources);
	const bd = $derived(data.burnDown);

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
	<!-- header -->
	<header class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex items-center gap-3">
			<i class="fa-solid fa-gauge-high text-2xl text-primary-500"></i>
			<div>
				<h1 class="text-2xl font-bold">{eng?.name}</h1>
				<p class="text-sm text-surface-600-400">
					{safeTranslate(eng?.status)} · {eng?.folder?.str ?? ''}
					{#if eng?.day_zero}· {safeTranslate('dayZero')}: {eng.day_zero}{/if}
				</p>
			</div>
		</div>
		<div class="flex flex-wrap gap-2">
			<a class="rounded-md bg-primary-500 px-3 py-2 text-sm font-medium text-white hover:bg-primary-600" href="/engagements/{eng?.id}/plan">
				<i class="fa-solid fa-diagram-project mr-1"></i>{safeTranslate('viewPlan')}
			</a>
			<a class="rounded-md border border-surface-300-700 px-3 py-2 text-sm font-medium hover:bg-surface-100-900" href="/engagements/{eng?.id}/eisenhower">
				<i class="fa-solid fa-table-cells-large mr-1"></i>{safeTranslate('eisenhowerMatrix')}
			</a>
			{#if folderId}
				<a class="rounded-md border border-surface-300-700 px-3 py-2 text-sm font-medium hover:bg-surface-100-900" href={kanbanHref}>
					<i class="fa-solid fa-columns mr-1"></i>{safeTranslate('openClientKanban')}
				</a>
			{/if}
			<a class="rounded-md border border-surface-300-700 px-3 py-2 text-sm font-medium hover:bg-surface-100-900" href="/my-assignments">
				<i class="fa-solid fa-list-check mr-1"></i>{safeTranslate('myAssignments')}
			</a>
			<a class="rounded-md border border-surface-300-700 px-3 py-2 text-sm font-medium hover:bg-surface-100-900" href="/engagements/{eng?.id}/export/pptx">
				<i class="fa-solid fa-file-powerpoint mr-1 text-orange-600"></i>{safeTranslate('exportPptx')}
			</a>
		</div>
	</header>

	<!-- capacidade -->
	<section class="rounded-lg border border-surface-200-800 p-4 space-y-3">
		<div class="flex items-center justify-between">
			<h2 class="text-lg font-semibold">{safeTranslate('capacity')}</h2>
			<span class="rounded-full px-3 py-1 text-xs font-semibold {overBudget ? 'bg-red-500/15 text-red-600 dark:text-red-400' : 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400'}">
				{overBudget ? safeTranslate('overBudget') : safeTranslate('withinBudget')} · {utilization}%
			</span>
		</div>
		<div class="h-3 w-full overflow-hidden rounded-full bg-surface-200-800">
			<div class="h-full rounded-full {overBudget ? 'bg-red-500' : 'bg-emerald-500'}" style="width: {barWidth}%"></div>
		</div>
		<div class="grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
			<div><div class="text-surface-600-400">{safeTranslate('contractedHours')}</div><div class="text-lg font-semibold">{cap?.contracted_hours ?? '—'}</div></div>
			<div><div class="text-surface-600-400">{safeTranslate('estimatedHours')}</div><div class="text-lg font-semibold">{cap?.estimated_hours ?? 0}</div></div>
			<div><div class="text-surface-600-400">{safeTranslate('loggedHours')}</div><div class="text-lg font-semibold">{cap?.logged_hours ?? 0}</div></div>
			<div><div class="text-surface-600-400">{safeTranslate('hoursModel')}</div><div class="text-lg font-semibold">{safeTranslate(cap?.hours_model)}</div></div>
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
</div>
