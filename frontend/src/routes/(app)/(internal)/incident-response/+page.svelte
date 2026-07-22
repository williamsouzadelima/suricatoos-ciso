<script lang="ts">
	import { m } from '$paraglide/messages';
	import { enhance } from '$app/forms';
	import type { PageData, ActionData } from './$types';

	let { data, form }: { data: PageData; form: ActionData } = $props();

	// A API de incidentes devolve severity/status como rótulos de exibição (ex.: "Major",
	// "Ongoing"), não o valor cru — mapeamos por número E por rótulo.
	const SEV: Record<string, { label: string; cls: string }> = {
		'1': { label: 'Critical', cls: 'bg-red-500' },
		'2': { label: 'Major', cls: 'bg-orange-500' },
		'3': { label: 'Moderate', cls: 'bg-amber-500' },
		'4': { label: 'Minor', cls: 'bg-sky-500' },
		'5': { label: 'Low', cls: 'bg-slate-400' },
		'6': { label: '—', cls: 'bg-slate-300' }
	};
	const SEV_BY_LABEL: Record<string, string> = {
		critical: 'bg-red-500',
		major: 'bg-orange-500',
		moderate: 'bg-amber-500',
		minor: 'bg-sky-500',
		low: 'bg-slate-400'
	};
	const sev = (n: number | string) => {
		const byNum = SEV[String(n)];
		if (byNum) return byNum;
		const key = String(n ?? '').toLowerCase();
		return { label: String(n ?? '—'), cls: SEV_BY_LABEL[key] ?? 'bg-slate-300' };
	};

	let seeding = $state(false);
	let resolving = $state(false);

	const selected = $derived(data.selected);
	const notifs = $derived((selected?.notifications ?? []) as any[]);
	const cost = $derived(selected?.cost);
	const summary = $derived(selected?.summary);
</script>

<div class="p-4 space-y-6">
	<!-- Hero -->
	<div
		class="rounded-2xl p-6 text-white shadow-lg"
		style="background: linear-gradient(120deg, #4f46e5 0%, #6366f1 45%, #8b5cf6 100%);"
	>
		<div class="text-xs font-bold uppercase tracking-widest opacity-80">Suricatoos vCISO</div>
		<h1 class="text-3xl font-bold mt-1">{m.incidentResponse()}</h1>
		<p class="opacity-90 mt-1 max-w-2xl text-sm">
			Runbook NIST SP 800-61, times &amp; RACI, relógio regulatório e P&amp;L por incidente.
		</p>
		<div class="grid grid-cols-2 md:grid-cols-4 gap-3 mt-5">
			<div class="rounded-xl bg-white/15 backdrop-blur px-4 py-3">
				<div class="text-2xl font-bold">{data.open}</div>
				<div class="text-xs uppercase tracking-wide opacity-80">{m.openIncidents()}</div>
			</div>
			<div class="rounded-xl bg-white/15 backdrop-blur px-4 py-3">
				<div class="text-2xl font-bold">{data.total}</div>
				<div class="text-xs uppercase tracking-wide opacity-80">{m.incidents()}</div>
			</div>
			<div class="rounded-xl bg-white/15 backdrop-blur px-4 py-3">
				<div class="text-2xl font-bold">{data.notifTotal}</div>
				<div class="text-xs uppercase tracking-wide opacity-80">{m.regulatoryNotifications()}</div>
			</div>
			<div class="rounded-xl bg-white/15 backdrop-blur px-4 py-3">
				<div class="text-2xl font-bold {data.overdue > 0 ? 'text-rose-200' : ''}">{data.overdue}</div>
				<div class="text-xs uppercase tracking-wide opacity-80">{m.overdueObligations()}</div>
			</div>
		</div>
	</div>

	<div class="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.6fr)] gap-6">
		<!-- Incident list -->
		<div class="rounded-xl border border-surface-200-800 bg-surface-50-950 overflow-hidden">
			<div class="px-4 py-3 border-b border-surface-200-800 font-semibold">{m.incidents()}</div>
			<div class="max-h-[70vh] overflow-y-auto divide-y divide-surface-200-800">
				{#each data.incidents as inc (inc.id)}
					<a
						href="?incident={inc.id}"
						class="flex items-center gap-3 px-4 py-3 hover:bg-surface-100-900 transition-colors {selected?.id ===
						inc.id
							? 'bg-surface-100-900'
							: ''}"
					>
						<span class="w-2.5 h-2.5 rounded-full {sev(inc.severity).cls}"></span>
						<span class="flex-1 min-w-0">
							<span class="block truncate font-medium">{inc.name}</span>
							<span class="block text-xs text-surface-500">{inc.folder?.str ?? ''}</span>
						</span>
						<span class="text-xs px-2 py-0.5 rounded-full bg-surface-200-800 capitalize"
							>{inc.status}</span
						>
					</a>
				{:else}
					<div class="px-4 py-8 text-center text-surface-500 text-sm">
						Nenhum incidente. Crie um em <a class="anchor" href="/incidents">/incidents</a>.
					</div>
				{/each}
			</div>
		</div>

		<!-- Console -->
		<div class="rounded-xl border border-surface-200-800 bg-surface-50-950 p-5">
			{#if !selected}
				<div class="text-surface-500 text-center py-16">
					Selecione um incidente à esquerda para abrir o console de resposta.
				</div>
			{:else}
				<div class="flex items-start justify-between gap-4 flex-wrap">
					<div>
						<div class="flex items-center gap-2">
							<span class="w-3 h-3 rounded-full {sev(selected.incident?.severity).cls}"></span>
							<h2 class="text-xl font-bold">{selected.incident?.name ?? 'Incidente'}</h2>
						</div>
						<div class="text-sm text-surface-500 mt-1 capitalize">
							{sev(selected.incident?.severity).label} · {selected.incident?.status ?? ''}
						</div>
					</div>
					<a href="/incidents/{selected.id}" class="btn btn-sm preset-tonal">{m.details()}</a>
				</div>

				{#if form?.error}
					<div class="mt-3 text-sm text-rose-600 bg-rose-500/10 rounded-lg px-3 py-2">
						{form.error}
					</div>
				{/if}

				<!-- Actions -->
				<div class="flex flex-wrap gap-2 mt-4">
					<form
						method="POST"
						action="?/seed"
						use:enhance={() => {
							seeding = true;
							return async ({ update }) => {
								await update();
								seeding = false;
							};
						}}
					>
						<input type="hidden" name="incident" value={selected.id} />
						<input type="hidden" name="standard" value="nist-800-61" />
						<button class="btn btn-sm preset-filled-primary-500" disabled={seeding}>
							{seeding ? m.loading() : m.seedRunbook()}
						</button>
					</form>
					<form
						method="POST"
						action="?/resolve"
						use:enhance={() => {
							resolving = true;
							return async ({ update }) => {
								await update();
								resolving = false;
							};
						}}
					>
						<input type="hidden" name="incident" value={selected.id} />
						<button class="btn btn-sm preset-tonal-secondary" disabled={resolving}>
							{resolving ? m.loading() : m.resolveObligations()}
						</button>
					</form>
					<a
						href="/incidents/{selected.id}/export/pptx"
						class="btn btn-sm preset-tonal"
						target="_blank"
						rel="noopener">{m.generatePir()}</a
					>
				</div>

				<!-- P&L -->
				{#if cost}
					<div class="mt-6">
						<div class="text-xs font-bold uppercase tracking-wide text-surface-500 mb-2">
							{m.incidentPnl()}
						</div>
						<div class="grid grid-cols-2 md:grid-cols-4 gap-3">
							<div class="rounded-lg bg-surface-100-900 px-3 py-2">
								<div class="text-lg font-bold text-indigo-500">{cost.response_effort_fmt}</div>
								<div class="text-xs text-surface-500">{m.responseEffort()}</div>
							</div>
							<div class="rounded-lg bg-surface-100-900 px-3 py-2">
								<div class="text-lg font-bold text-violet-500">{cost.business_impact_fmt}</div>
								<div class="text-xs text-surface-500">{m.businessImpact()}</div>
							</div>
							<div class="rounded-lg bg-surface-100-900 px-3 py-2">
								<div class="text-lg font-bold text-sky-500">{cost.external_vendor_fmt}</div>
								<div class="text-xs text-surface-500">Fornecedores</div>
							</div>
							<div class="rounded-lg bg-surface-100-900 px-3 py-2">
								<div class="text-lg font-bold text-rose-500">{cost.regulatory_fines_fmt}</div>
								<div class="text-xs text-surface-500">{m.regulatoryFines()}</div>
							</div>
						</div>
						<div
							class="mt-3 rounded-lg px-4 py-3 text-white font-semibold flex justify-between items-center"
							style="background:#0f172a;"
						>
							<span>{m.totalEstimatedCost()}</span>
							<span class="text-lg">{cost.total_fmt}</span>
						</div>
					</div>
				{/if}

				<!-- Runbook summary -->
				{#if summary}
					<div class="mt-6">
						<div class="text-xs font-bold uppercase tracking-wide text-surface-500 mb-2">
							{m.responseRunbook()}
						</div>
						{#if summary.has_plan}
							<div class="grid grid-cols-2 md:grid-cols-4 gap-2">
								{#each summary.phases as ph (ph.id)}
									<div class="rounded-lg border border-surface-200-800 px-3 py-2">
										<div class="text-sm font-semibold truncate">{ph.name}</div>
										<div class="text-xs text-surface-500">{ph.tasks_count} atividades</div>
									</div>
								{/each}
							</div>
							<div class="text-xs text-surface-500 mt-2">
								{summary.tasks_total} atividades · {summary.roles_count} papéis · {summary.standard}
							</div>
						{:else}
							<div class="text-sm text-surface-500">
								Sem runbook semeado. Clique em "{m.seedRunbook()}".
							</div>
						{/if}
					</div>
				{/if}

				<!-- Regulatory clock -->
				<div class="mt-6">
					<div class="text-xs font-bold uppercase tracking-wide text-surface-500 mb-2">
						{m.regulatoryClock()}
					</div>
					{#if notifs.length}
						<div class="space-y-2">
							{#each notifs as n (n.id)}
								<div
									class="rounded-lg border px-3 py-2 flex items-start gap-3 {n.is_overdue
										? 'border-rose-400 bg-rose-500/5'
										: 'border-surface-200-800'}"
								>
									<div class="flex-1 min-w-0">
										<div class="font-semibold text-sm">{n.regulator}</div>
										<div class="text-xs text-surface-500">{n.obligation_ref}</div>
										{#if n.qualitative_note}
											<div class="text-xs text-surface-400 mt-1 italic">{n.qualitative_note}</div>
										{/if}
									</div>
									<div class="text-right shrink-0">
										<div class="text-xs font-semibold {n.is_overdue ? 'text-rose-500' : 'text-indigo-500'}">
											{n.deadline_hours ? n.deadline_hours + 'h' : 'tempestivo'}
										</div>
										<div class="text-xs text-surface-500 capitalize">{n.status}</div>
									</div>
								</div>
							{/each}
						</div>
					{:else}
						<div class="text-sm text-surface-500">
							Sem obrigações resolvidas. Clique em "{m.resolveObligations()}".
						</div>
					{/if}
				</div>
			{/if}
		</div>
	</div>
</div>
