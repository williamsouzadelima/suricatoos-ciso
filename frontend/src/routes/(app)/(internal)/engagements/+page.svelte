<script lang="ts">
	import { safeTranslate } from '$lib/utils/i18n';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
</script>

<div class="p-4 space-y-4">
	<header class="flex items-center gap-3">
		<i class="fa-solid fa-handshake text-2xl text-primary-500"></i>
		<h1 class="text-2xl font-bold">{safeTranslate('engagements')}</h1>
	</header>

	{#if !data.engagements || data.engagements.length === 0}
		<p class="text-surface-600-400">{safeTranslate('noEngagementsYet')}</p>
	{:else}
		<div class="overflow-x-auto rounded-lg border border-surface-200-800">
			<table class="w-full text-sm">
				<thead class="bg-surface-100-900 text-left">
					<tr>
						<th class="p-3">{safeTranslate('name')}</th>
						<th class="p-3">{safeTranslate('status')}</th>
						<th class="p-3">{safeTranslate('hoursModel')}</th>
						<th class="p-3 text-right">{safeTranslate('contractedHours')}</th>
						<th class="p-3 text-right">{safeTranslate('estimatedHours')}</th>
						<th class="p-3">{safeTranslate('domain')}</th>
					</tr>
				</thead>
				<tbody>
					{#each data.engagements as e (e.id)}
						<tr class="border-t border-surface-200-800 hover:bg-surface-100-900">
							<td class="p-3">
								<a class="font-medium text-primary-500 hover:underline" href="/engagements/{e.id}">
									{e.name}
								</a>
							</td>
							<td class="p-3">{safeTranslate(e.status)}</td>
							<td class="p-3">{safeTranslate(e.hours_model)}</td>
							<td class="p-3 text-right">{e.contracted_hours ?? '—'}</td>
							<td class="p-3 text-right">{e.estimated_hours_total ?? 0}</td>
							<td class="p-3">{e.folder?.str ?? ''}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>
