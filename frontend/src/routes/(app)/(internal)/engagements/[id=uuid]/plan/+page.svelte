<script lang="ts">
	import GanttChart from '$lib/components/Gantt/GanttChart.svelte';
	import { safeTranslate } from '$lib/utils/i18n';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const phaseColors = ['#6366f1', '#8b5cf6', '#0ea5e9', '#10b981'];

	const items = $derived(
		(data.tasks ?? []).map((t: any) => ({
			id: t.id,
			name: t.applied_control?.name ?? t.str ?? '',
			startDate: t.applied_control?.start_date ? new Date(t.applied_control.start_date) : null,
			endDate: t.applied_control?.eta ? new Date(t.applied_control.eta) : null,
			progress: t.applied_control?.progress_field ?? -1,
			type: 'bar' as const,
			category: `phase-${t.phase?.order ?? 0}`,
			categoryLabel: t.phase?.name ?? '',
			folder: t.folder?.str ?? '',
			folderId: t.folder?.id ?? '',
			href: t.applied_control ? `/applied-controls/${t.applied_control.id}` : '',
			color: phaseColors[(((t.phase?.order ?? 1) - 1) % phaseColors.length + phaseColors.length) % phaseColors.length],
			owners: [] as string[]
		}))
	);
</script>

<div class="p-4 space-y-4">
	<header class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex items-center gap-3">
			<i class="fa-solid fa-diagram-project text-2xl text-primary-500"></i>
			<div>
				<h1 class="text-2xl font-bold">{safeTranslate('hundredDayPlan')}</h1>
				<p class="text-sm text-surface-600-400">{data.engagement?.name ?? ''}</p>
			</div>
		</div>
		<a class="rounded-md border border-surface-300-700 px-3 py-2 text-sm font-medium hover:bg-surface-100-900" href="/engagements/{data.engagement?.id}">
			← {safeTranslate('engagement')}
		</a>
	</header>

	{#if items.length}
		<GanttChart {items} zoom="monthly" />
	{:else}
		<p class="text-surface-600-400">{safeTranslate('noTasksYet')}</p>
	{/if}
</div>
