<script lang="ts">
	import { safeTranslate } from '$lib/utils/i18n';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const q = $derived(
		data.matrix?.quadrants ?? { do: [], schedule: [], delegate: [], eliminate: [] }
	);

	// ordem da grade 2x2: [urgente+importante, importante] / [urgente, resto]
	const cells = [
		{ key: 'do', title: 'quadrantDo', accent: 'border-l-4 border-l-red-500', badge: 'bg-red-500' },
		{ key: 'schedule', title: 'quadrantSchedule', accent: 'border-l-4 border-l-blue-500', badge: 'bg-blue-500' },
		{ key: 'delegate', title: 'quadrantDelegate', accent: 'border-l-4 border-l-amber-500', badge: 'bg-amber-500' },
		{ key: 'eliminate', title: 'quadrantEliminate', accent: 'border-l-4 border-l-surface-400', badge: 'bg-surface-500' }
	];
</script>

<div class="p-4 space-y-4">
	<header class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex items-center gap-3">
			<i class="fa-solid fa-table-cells-large text-2xl text-primary-500"></i>
			<div>
				<h1 class="text-2xl font-bold">{safeTranslate('eisenhowerMatrix')}</h1>
				<p class="text-sm text-surface-600-400">
					{data.engagement?.name ?? ''} · {safeTranslate('horizonDays')}: {data.matrix?.horizon_days ?? 21}
				</p>
			</div>
		</div>
		<a class="rounded-md border border-surface-300-700 px-3 py-2 text-sm font-medium hover:bg-surface-100-900" href="/engagements/{data.engagement?.id}">
			← {safeTranslate('engagement')}
		</a>
	</header>

	<div class="grid grid-cols-1 gap-1 text-center text-xs font-semibold text-surface-600-400 sm:grid-cols-2">
		<div>{safeTranslate('urgent')}</div>
		<div>{safeTranslate('notUrgent')}</div>
	</div>

	<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
		{#each cells as cell (cell.key)}
			<div class="rounded-lg border border-surface-200-800 p-4 {cell.accent}">
				<div class="mb-3 flex items-center justify-between">
					<h2 class="text-sm font-semibold">{safeTranslate(cell.title)}</h2>
					<span class="inline-flex h-6 min-w-6 items-center justify-center rounded-full px-2 text-xs font-bold text-white {cell.badge}">
						{q[cell.key]?.length ?? 0}
					</span>
				</div>
				{#if q[cell.key]?.length}
					<ul class="space-y-1 text-sm">
						{#each q[cell.key] as t (t.id)}
							<li class="flex items-center gap-2">
								<i class="fa-solid fa-circle text-[6px] text-surface-400"></i>
								<span class="truncate">{t.applied_control?.name ?? t.str ?? ''}</span>
							</li>
						{/each}
					</ul>
				{:else}
					<p class="text-xs text-surface-600-400">—</p>
				{/if}
			</div>
		{/each}
	</div>
</div>
