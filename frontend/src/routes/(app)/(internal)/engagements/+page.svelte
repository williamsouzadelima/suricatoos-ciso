<script lang="ts">
	import { safeTranslate } from '$lib/utils/i18n';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const engs = $derived((data.engagements ?? []) as any[]);
	const total = $derived(engs.length);
	const active = $derived(engs.filter((e) => e.status === 'active').length);
	const onboarding = $derived(engs.filter((e) => e.status === 'onboarding').length);
	const clients = $derived(
		new Set(engs.map((e) => e.folder?.id ?? e.folder?.str).filter(Boolean)).size
	);
	const contracted = $derived(engs.reduce((s, e) => s + Number(e.contracted_hours ?? 0), 0));
	const contractedFmt = $derived(
		new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 0 }).format(contracted)
	);
</script>

<div class="p-4 space-y-4">
	<!-- HERO -->
	<section
		class="overflow-hidden rounded-2xl text-white shadow-xl"
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
						<i class="fa-solid fa-handshake"></i> Módulo · Entrega vCISO
					</div>
					<h1
						class="mt-2 text-3xl font-bold leading-tight sm:text-4xl"
						style="font-family: 'Geist', ui-sans-serif, sans-serif; letter-spacing: -0.02em;"
					>
						{safeTranslate('engagements')}
					</h1>
					<p class="mt-2 max-w-2xl text-sm text-white/80">
						Todos os engajamentos vCISO — clientes atendidos, capacidade contratada e status de cada
						entrega.
					</p>
					<div class="mt-4 flex flex-wrap gap-2">
						<a
							href="/client-onboarding"
							class="inline-flex items-center gap-2 rounded-lg bg-white px-3.5 py-2 text-sm font-semibold text-[#4f46e5] transition hover:bg-white/90"
						>
							<i class="fa-solid fa-user-plus"></i>Novo cliente
						</a>
						<a
							href="/business-catalogs"
							class="inline-flex items-center gap-2 rounded-lg border border-white/20 bg-white/[0.12] px-3.5 py-2 text-sm font-semibold transition-colors hover:bg-white/[0.24]"
						>
							<i class="fa-solid fa-boxes-stacked"></i>Catálogos
						</a>
					</div>
				</div>
				<div class="text-center">
					<div class="text-5xl font-bold" style="font-family: 'Geist', sans-serif;">
						{total}
					</div>
					<div class="text-xs uppercase tracking-wide text-white/70">Engajamentos</div>
				</div>
			</div>
			<div class="relative mt-5 grid grid-cols-2 gap-px overflow-hidden rounded-xl bg-white/10 sm:grid-cols-4">
				<div class="bg-white/[0.04] px-4 py-3">
					<div class="text-2xl font-bold" style="font-family: 'Geist', sans-serif;">{active}</div>
					<div class="text-xs uppercase tracking-wide text-white/70">Ativos</div>
				</div>
				<div class="bg-white/[0.04] px-4 py-3">
					<div class="text-2xl font-bold" style="font-family: 'Geist', sans-serif;">{onboarding}</div>
					<div class="text-xs uppercase tracking-wide text-white/70">Onboarding</div>
				</div>
				<div class="bg-white/[0.04] px-4 py-3">
					<div class="text-2xl font-bold" style="font-family: 'Geist', sans-serif;">{clients}</div>
					<div class="text-xs uppercase tracking-wide text-white/70">Clientes</div>
				</div>
				<div class="bg-white/[0.04] px-4 py-3">
					<div class="text-2xl font-bold" style="font-family: 'Geist', sans-serif;">{contractedFmt}</div>
					<div class="text-xs uppercase tracking-wide text-white/70">Horas contratadas</div>
				</div>
			</div>
		</div>
	</section>

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
