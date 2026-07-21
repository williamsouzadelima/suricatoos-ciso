<script lang="ts">
	import { safeTranslate } from '$lib/utils/i18n';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const cat = $derived(data.catalog);
	const imp = $derived(data.impact);
	const eng = $derived(cat?.engagement);

	const critColor: Record<string, string> = {
		critical: 'bg-red-500/15 text-red-600 dark:text-red-400',
		high: 'bg-orange-500/15 text-orange-600 dark:text-orange-400',
		medium: 'bg-blue-500/15 text-blue-600 dark:text-blue-400',
		low: 'bg-surface-500/15 text-surface-600-400'
	};

	// parcelas por hora — a composição do total é interno + lucro cessante + regulatório
	const parcels = $derived([
		{
			label: 'internalLoss',
			icon: 'fa-users',
			value: imp?.internal_hourly_fmt,
			color: 'text-blue-600 dark:text-blue-400'
		},
		{
			label: 'lostProfit',
			icon: 'fa-chart-line',
			value: imp?.lost_profit_hourly_fmt,
			color: 'text-emerald-600 dark:text-emerald-400'
		},
		{
			label: 'regulatoryLoss',
			icon: 'fa-scale-balanced',
			value: imp?.regulatory_hourly_fmt,
			color: 'text-amber-600 dark:text-amber-400'
		}
	]);
</script>

<div class="p-4 space-y-6">
	<!-- header -->
	<header class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex items-center gap-3">
			<i class="fa-solid fa-calculator text-2xl text-primary-500"></i>
			<div>
				<h1 class="text-2xl font-bold">{cat?.name}</h1>
				<p class="text-sm text-surface-600-400">
					{safeTranslate('impactCalculator')}
					{#if cat?.folder?.str}· {cat.folder.str}{/if}
				</p>
			</div>
			{#if cat?.criticality}
				<span class="rounded-full px-3 py-1 text-xs font-semibold {critColor[cat.criticality] ?? critColor.low}">
					{safeTranslate(cat.criticality)}
				</span>
			{/if}
		</div>
		<div class="flex flex-wrap gap-2">
			<a class="rounded-md border border-surface-300-700 px-3 py-2 text-sm font-medium hover:bg-surface-100-900" href="/business-catalogs/{cat?.id}">
				<i class="fa-solid fa-pen-to-square mr-1"></i>{safeTranslate('edit')}
			</a>
			{#if eng?.id}
				<a class="rounded-md border border-surface-300-700 px-3 py-2 text-sm font-medium hover:bg-surface-100-900" href="/engagements/{eng.id}">
					<i class="fa-solid fa-gauge-high mr-1"></i>{safeTranslate('engagement')}
				</a>
			{/if}
		</div>
	</header>

	{#if !imp}
		<div class="rounded-lg border border-dashed border-surface-300-700 p-6 text-sm text-surface-600-400">
			{safeTranslate('impactUnavailable')}
		</div>
	{:else}
		<!-- prejuízo total por hora (destaque) -->
		<section class="rounded-lg border-2 border-primary-500/40 bg-primary-500/5 p-5">
			<div class="flex flex-wrap items-end justify-between gap-3">
				<div>
					<div class="text-sm font-medium text-surface-600-400">{safeTranslate('totalLossPerHour')}</div>
					<div class="text-4xl font-bold text-primary-600 dark:text-primary-400">{imp.total_hourly_fmt}</div>
					<div class="mt-1 text-xs text-surface-600-400">
						{safeTranslate('lossComposition')}
					</div>
				</div>
				<div class="text-right text-xs text-surface-600-400">
					<div>{safeTranslate('grossRevenuePerHour')}: <span class="font-semibold">{imp.gross_revenue_hourly_fmt}</span></div>
					<div class="mt-0.5">{safeTranslate('grossRevenueRef')}</div>
				</div>
			</div>
		</section>

		<!-- 3 parcelas por hora -->
		<section class="grid grid-cols-1 gap-3 sm:grid-cols-3">
			{#each parcels as p}
				<div class="rounded-lg border border-surface-200-800 p-4">
					<div class="flex items-center gap-2 text-sm text-surface-600-400">
						<i class="fa-solid {p.icon} {p.color}"></i>{safeTranslate(p.label)}
					</div>
					<div class="mt-1 text-2xl font-bold {p.color}">{p.value}</div>
					<div class="text-xs text-surface-600-400">{safeTranslate('perHour')}</div>
				</div>
			{/each}
		</section>

		<!-- premissas do cálculo -->
		<section class="grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
			<div class="rounded-lg border border-surface-200-800 p-3">
				<div class="text-surface-600-400">{safeTranslate('collaborators')}</div>
				<div class="text-lg font-semibold">{imp.collaborators}</div>
			</div>
			<div class="rounded-lg border border-surface-200-800 p-3">
				<div class="text-surface-600-400">{safeTranslate('perCollaboratorHourly')}</div>
				<div class="text-lg font-semibold">{imp.per_collaborator_hourly_fmt}</div>
			</div>
			<div class="rounded-lg border border-surface-200-800 p-3">
				<div class="text-surface-600-400">{safeTranslate('profitMargin')}</div>
				<div class="text-lg font-semibold">{imp.profit_margin}%</div>
			</div>
			<div class="rounded-lg border border-surface-200-800 p-3">
				<div class="text-surface-600-400">{safeTranslate('regulatoryFixed')}</div>
				<div class="text-lg font-semibold">{imp.regulatory_fixed_fmt}</div>
			</div>
		</section>

		<!-- prejuízo por duração de indisponibilidade -->
		<section class="space-y-3">
			<h2 class="text-lg font-semibold">{safeTranslate('lossByDowntime')}</h2>
			<div class="overflow-x-auto rounded-lg border border-surface-200-800">
				<table class="w-full text-sm">
					<thead>
						<tr class="border-b border-surface-200-800 text-left text-surface-600-400">
							<th class="p-3 font-medium">{safeTranslate('downtimeHours')}</th>
							<th class="p-3 text-right font-medium">{safeTranslate('internalLoss')}</th>
							<th class="p-3 text-right font-medium">{safeTranslate('lostProfit')}</th>
							<th class="p-3 text-right font-medium">{safeTranslate('regulatoryLoss')}</th>
							<th class="p-3 text-right font-medium">{safeTranslate('total')}</th>
						</tr>
					</thead>
					<tbody>
						{#each imp.by_hours as row (row.hours)}
							<tr class="border-t border-surface-200-800 first:border-t-0">
								<td class="p-3 font-medium">{row.hours}h</td>
								<td class="p-3 text-right">{row.internal_fmt}</td>
								<td class="p-3 text-right">{row.lost_profit_fmt}</td>
								<td class="p-3 text-right">{row.regulatory_fmt}</td>
								<td class="p-3 text-right font-semibold">{row.total_fmt}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
			<p class="text-xs text-surface-600-400">{safeTranslate('regulatoryFixedNote')}</p>
		</section>

		<!-- manutenção anual vs prejuízo -->
		<section class="grid grid-cols-1 gap-3 sm:grid-cols-2">
			<div class="rounded-lg border border-surface-200-800 p-4">
				<div class="flex items-center gap-2 text-sm text-surface-600-400">
					<i class="fa-solid fa-screwdriver-wrench text-surface-500"></i>{safeTranslate('maintenanceCost')}
				</div>
				<div class="mt-1 text-2xl font-bold">{imp.maintenance_annual_fmt}</div>
				<div class="text-xs text-surface-600-400">{safeTranslate('perYear')}</div>
			</div>
			<div class="rounded-lg border border-surface-200-800 p-4">
				<div class="flex items-center gap-2 text-sm text-surface-600-400">
					<i class="fa-solid fa-triangle-exclamation text-red-500"></i>{safeTranslate('lossPerDay')}
				</div>
				<div class="mt-1 text-2xl font-bold text-red-600 dark:text-red-400">
					{imp.by_hours.find((r) => r.hours === 24)?.total_fmt ?? '—'}
				</div>
				<div class="text-xs text-surface-600-400">{safeTranslate('lossPerDayHint')}</div>
			</div>
		</section>
	{/if}
</div>
