<script lang="ts">
	import { safeTranslate } from '$lib/utils/i18n';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const cat = $derived(data.catalog);
	const imp = $derived(data.impact);
	const eng = $derived(cat?.engagement);

	const critDot: Record<string, string> = {
		critical: '#f87171',
		high: '#fb923c',
		medium: '#60a5fa',
		low: '#cbd5e1'
	};

	// parcelas por hora — a composição do total é interno + lucro cessante + regulatório
	const parcels = $derived([
		{ label: 'internalLoss', icon: 'fa-users', value: imp?.internal_hourly_fmt },
		{ label: 'lostProfit', icon: 'fa-chart-line', value: imp?.lost_profit_hourly_fmt },
		{ label: 'regulatoryLoss', icon: 'fa-scale-balanced', value: imp?.regulatory_hourly_fmt }
	]);
</script>

<div class="p-4 space-y-6">
	<!-- HERO — prejuízo na cara -->
	<section
		class="overflow-hidden rounded-2xl text-white shadow-xl"
		style="background: linear-gradient(135deg, oklch(45% 0.19 300deg), oklch(47% 0.20 338deg) 55%, oklch(50% 0.19 358deg));"
	>
		<div class="relative p-6 sm:p-8">
			<div
				class="pointer-events-none absolute inset-0"
				style="background: radial-gradient(520px 240px at 88% -10%, rgba(255,255,255,.18), transparent 60%), radial-gradient(420px 220px at -5% 115%, rgba(129,127,245,.28), transparent 55%);"
			></div>
			<div class="relative flex flex-wrap items-start justify-between gap-6">
				<div class="min-w-0">
					<div class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-white/70">
						<i class="fa-solid fa-calculator"></i>
						{safeTranslate('impactCalculator')}
					</div>
					<h1
						class="mt-2 text-3xl font-bold leading-tight sm:text-4xl"
						style="font-family: 'Bricolage Grotesque', ui-sans-serif, sans-serif; letter-spacing: -0.02em;"
					>
						{cat?.name}
					</h1>
					<div class="mt-2 flex flex-wrap items-center gap-2 text-sm text-white/80">
						{#if cat?.criticality}
							<span
								class="inline-flex items-center gap-1.5 rounded-full border border-white/25 bg-white/15 px-3 py-0.5 text-xs font-semibold"
							>
								<span class="h-2 w-2 rounded-full" style="background: {critDot[cat.criticality] ?? '#cbd5e1'};"></span>
								{safeTranslate(cat.criticality)}
							</span>
						{/if}
						{#if cat?.folder?.str}<span>{cat.folder.str}</span>{/if}
					</div>
					<div class="mt-4 flex flex-wrap gap-2">
						<a
							class="inline-flex items-center gap-2 rounded-lg border border-white/20 bg-white/[0.12] px-3.5 py-2 text-sm font-semibold transition-colors hover:bg-white/[0.24]"
							href="/business-catalogs/{cat?.id}"
						>
							<i class="fa-solid fa-pen-to-square"></i>{safeTranslate('edit')}
						</a>
						{#if eng?.id}
							<a
								class="inline-flex items-center gap-2 rounded-lg border border-white/20 bg-white/[0.12] px-3.5 py-2 text-sm font-semibold transition-colors hover:bg-white/[0.24]"
								href="/engagements/{eng.id}"
							>
								<i class="fa-solid fa-gauge-high"></i>{safeTranslate('engagement')}
							</a>
						{/if}
					</div>
				</div>
				{#if imp}
					<div class="text-right">
						<div class="text-xs font-semibold uppercase tracking-wide text-white/70">
							{safeTranslate('totalLossPerHour')}
						</div>
						<div class="text-4xl font-bold sm:text-5xl" style="font-family: 'Bricolage Grotesque', sans-serif;">
							{imp.total_hourly_fmt}
						</div>
						<div class="mt-1 text-xs text-white/60">
							{safeTranslate('grossRevenuePerHour')}: {imp.gross_revenue_hourly_fmt} · {safeTranslate('grossRevenueRef')}
						</div>
					</div>
				{/if}
			</div>
			{#if imp}
				<div class="relative mt-5 grid grid-cols-1 gap-px overflow-hidden rounded-xl bg-white/10 sm:grid-cols-3">
					{#each parcels as p}
						<div class="bg-white/[0.04] px-4 py-3">
							<div class="flex items-center gap-2 text-xs uppercase tracking-wide text-white/70">
								<i class="fa-solid {p.icon}"></i>{safeTranslate(p.label)}
							</div>
							<div class="mt-1 text-2xl font-bold" style="font-family: 'Bricolage Grotesque', sans-serif;">
								{p.value}
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	</section>

	{#if !imp}
		<div class="rounded-lg border border-dashed border-surface-300-700 p-6 text-sm text-surface-600-400">
			{safeTranslate('impactUnavailable')}
		</div>
	{:else}
		<!-- premissas do cálculo -->
		<section class="grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
			<div class="card rounded-lg border border-surface-200-800 p-3">
				<div class="text-surface-600-400">{safeTranslate('collaborators')}</div>
				<div class="text-lg font-semibold">{imp.collaborators}</div>
			</div>
			<div class="card rounded-lg border border-surface-200-800 p-3">
				<div class="text-surface-600-400">{safeTranslate('perCollaboratorHourly')}</div>
				<div class="text-lg font-semibold">{imp.per_collaborator_hourly_fmt}</div>
			</div>
			<div class="card rounded-lg border border-surface-200-800 p-3">
				<div class="text-surface-600-400">{safeTranslate('profitMargin')}</div>
				<div class="text-lg font-semibold">{imp.profit_margin}%</div>
			</div>
			<div class="card rounded-lg border border-surface-200-800 p-3">
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
			<div class="card rounded-lg border border-surface-200-800 p-4">
				<div class="flex items-center gap-2 text-sm text-surface-600-400">
					<i class="fa-solid fa-screwdriver-wrench text-surface-500"></i>{safeTranslate('maintenanceCost')}
				</div>
				<div class="mt-1 text-2xl font-bold">{imp.maintenance_annual_fmt}</div>
				<div class="text-xs text-surface-600-400">{safeTranslate('perYear')}</div>
			</div>
			<div class="card rounded-lg border border-surface-200-800 p-4">
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
