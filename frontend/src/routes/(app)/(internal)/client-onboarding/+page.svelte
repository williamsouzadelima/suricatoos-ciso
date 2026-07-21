<script lang="ts">
	import { enhance } from '$app/forms';
	import { safeTranslate } from '$lib/utils/i18n';
	import type { PageData, ActionData } from './$types';

	let { data, form }: { data: PageData; form: ActionData } = $props();

	let step = $state(1);
	let submitting = $state(false);

	let companyName = $state('');
	let website = $state('');
	let subsector = $state('');
	let dayZero = $state('');
	let hours = $state('');
	let hoursModel = $state('budget');
	let modules = $state<string[]>(['lgpd']);
	let createAssessments = $state(true);

	const SUGGEST: Record<string, string[]> = {
		bank: ['lgpd', 'bacen'],
		asset_manager: ['lgpd', 'anbima'],
		broker: ['lgpd', 'cvm'],
		other: ['lgpd']
	};
	const ALL_MODULES = [
		{ key: 'lgpd', label: 'LGPD' },
		{ key: 'bacen', label: 'BACEN' },
		{ key: 'anbima', label: 'ANBIMA (Deveres Básicos)' },
		{ key: 'cvm', label: 'CVM 21' }
	];

	function pickSubsector(v: string) {
		subsector = v;
		modules = SUGGEST[v] ?? ['lgpd'];
	}
	function toggleModule(k: string) {
		modules = modules.includes(k) ? modules.filter((m) => m !== k) : [...modules, k];
	}

	const canNext1 = $derived(companyName.trim().length > 0 && subsector.length > 0);
	const canSubmit = $derived(canNext1 && dayZero.length > 0);

	const subsectorEntries = $derived(Object.entries(data.subsectors ?? {}));
	const hoursModelEntries = $derived(Object.entries(data.hoursModels ?? {}));
</script>

<div class="mx-auto max-w-3xl space-y-6 p-4">
	<header class="flex items-center gap-3">
		<i class="fa-solid fa-user-plus text-2xl text-primary-500"></i>
		<div>
			<h1 class="text-2xl font-bold">{safeTranslate('clientOnboarding')}</h1>
			<p class="text-sm text-surface-600-400">{safeTranslate('onboardingWizardHint')}</p>
		</div>
	</header>

	<!-- stepper -->
	<ol class="flex items-center gap-2 text-sm">
		{#each [1, 2, 3] as s (s)}
			<li class="flex items-center gap-2">
				<span class="flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold {step >= s ? 'bg-primary-500 text-white' : 'bg-surface-200-800 text-surface-600-400'}">{s}</span>
				<span class={step === s ? 'font-semibold' : 'text-surface-600-400'}>
					{safeTranslate(s === 1 ? 'stepClient' : s === 2 ? 'stepContract' : 'stepReview')}
				</span>
				{#if s < 3}<span class="mx-1 text-surface-400">›</span>{/if}
			</li>
		{/each}
	</ol>

	{#if form?.error}
		<div class="rounded-lg border border-red-300 bg-red-500/10 p-3 text-sm text-red-600 dark:text-red-400">{form.error}</div>
	{/if}

	<form
		method="POST"
		use:enhance={() => {
			submitting = true;
			return async ({ update }) => {
				await update();
				submitting = false;
			};
		}}
		class="space-y-6"
	>
		<!-- carriers ocultos (submetem independentemente do passo visível) -->
		<input type="hidden" name="company_name" value={companyName} />
		<input type="hidden" name="website" value={website} />
		<input type="hidden" name="subsector" value={subsector} />
		<input type="hidden" name="day_zero" value={dayZero} />
		<input type="hidden" name="contracted_hours" value={hours} />
		<input type="hidden" name="hours_model" value={hoursModel} />
		{#each modules as m (m)}<input type="hidden" name="modules" value={m} />{/each}
		{#if createAssessments}<input type="hidden" name="create_assessments" value="on" />{/if}

		{#if step === 1}
			<section class="space-y-4 rounded-lg border border-surface-200-800 p-5">
				<label class="block space-y-1">
					<span class="text-sm font-medium">{safeTranslate('companyName')} *</span>
					<input class="w-full rounded-md border border-surface-300-700 bg-transparent p-2" bind:value={companyName} placeholder="Razão social" />
				</label>
				<label class="block space-y-1">
					<span class="text-sm font-medium">{safeTranslate('website')}</span>
					<input class="w-full rounded-md border border-surface-300-700 bg-transparent p-2" bind:value={website} placeholder="ex.: cliente.com.br" />
					<span class="block text-xs text-surface-600-400">{safeTranslate('websiteHint')}</span>
				</label>
				<div class="space-y-1">
					<span class="text-sm font-medium">{safeTranslate('subsector')} *</span>
					<div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
						{#each subsectorEntries as [val, label] (val)}
							<button type="button" onclick={() => pickSubsector(val)}
								class="rounded-md border p-3 text-left text-sm {subsector === val ? 'border-primary-500 bg-primary-500/10' : 'border-surface-300-700 hover:bg-surface-100-900'}">
								{safeTranslate(label)}
							</button>
						{/each}
					</div>
				</div>
			</section>
		{/if}

		{#if step === 2}
			<section class="space-y-4 rounded-lg border border-surface-200-800 p-5">
				<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
					<label class="block space-y-1">
						<span class="text-sm font-medium">{safeTranslate('dayZero')} *</span>
						<input type="date" class="w-full rounded-md border border-surface-300-700 bg-transparent p-2" bind:value={dayZero} />
					</label>
					<label class="block space-y-1">
						<span class="text-sm font-medium">{safeTranslate('contractedHours')}</span>
						<input type="number" min="0" step="1" class="w-full rounded-md border border-surface-300-700 bg-transparent p-2" bind:value={hours} placeholder="opcional" />
					</label>
				</div>
				<label class="block space-y-1">
					<span class="text-sm font-medium">{safeTranslate('hoursModel')}</span>
					<select class="w-full rounded-md border border-surface-300-700 bg-transparent p-2" bind:value={hoursModel}>
						{#each hoursModelEntries as [val, label] (val)}
							<option value={val}>{safeTranslate(label)}</option>
						{/each}
					</select>
				</label>
				<div class="space-y-2">
					<span class="text-sm font-medium">{safeTranslate('regulatoryModules')}</span>
					<div class="flex flex-wrap gap-2">
						{#each ALL_MODULES as m (m.key)}
							<button type="button" onclick={() => toggleModule(m.key)}
								class="rounded-full border px-3 py-1 text-sm {modules.includes(m.key) ? 'border-primary-500 bg-primary-500/10 font-medium' : 'border-surface-300-700 text-surface-600-400'}">
								{modules.includes(m.key) ? '✓ ' : ''}{m.label}
							</button>
						{/each}
					</div>
				</div>
				<label class="flex items-center gap-2 text-sm">
					<input type="checkbox" bind:checked={createAssessments} />
					{safeTranslate('createGapAssessments')}
				</label>
			</section>
		{/if}

		{#if step === 3}
			<section class="space-y-3 rounded-lg border border-surface-200-800 p-5 text-sm">
				<h2 class="text-base font-semibold">{safeTranslate('stepReview')}</h2>
				<div class="grid grid-cols-2 gap-2">
					<span class="text-surface-600-400">{safeTranslate('companyName')}</span><span class="font-medium">{companyName}</span>
					<span class="text-surface-600-400">{safeTranslate('subsector')}</span><span class="font-medium">{safeTranslate(data.subsectors?.[subsector] ?? subsector)}</span>
					<span class="text-surface-600-400">{safeTranslate('dayZero')}</span><span class="font-medium">{dayZero}</span>
					<span class="text-surface-600-400">{safeTranslate('contractedHours')}</span><span class="font-medium">{hours || '—'}</span>
					<span class="text-surface-600-400">{safeTranslate('hoursModel')}</span><span class="font-medium">{safeTranslate(data.hoursModels?.[hoursModel] ?? hoursModel)}</span>
					<span class="text-surface-600-400">{safeTranslate('regulatoryModules')}</span><span class="font-medium">{modules.join(', ') || '—'}</span>
					<span class="text-surface-600-400">{safeTranslate('createGapAssessments')}</span><span class="font-medium">{createAssessments ? 'Sim' : 'Não'}</span>
				</div>
				<p class="text-xs text-surface-600-400">{safeTranslate('onboardingReviewNote')}</p>
			</section>
		{/if}

		<!-- navegação -->
		<div class="flex items-center justify-between">
			<button type="button" class="rounded-md border border-surface-300-700 px-4 py-2 text-sm {step === 1 ? 'invisible' : ''}" onclick={() => (step = Math.max(1, step - 1))}>
				← {safeTranslate('back')}
			</button>
			{#if step < 3}
				<button type="button" class="rounded-md bg-primary-500 px-4 py-2 text-sm font-medium text-white hover:bg-primary-600 disabled:opacity-50"
					disabled={step === 1 ? !canNext1 : false} onclick={() => (step = step + 1)}>
					{safeTranslate('next')} →
				</button>
			{:else}
				<button type="submit" class="rounded-md bg-primary-500 px-4 py-2 text-sm font-medium text-white hover:bg-primary-600 disabled:opacity-50" disabled={!canSubmit || submitting}>
					{submitting ? '…' : safeTranslate('provisionClient')}
				</button>
			{/if}
		</div>
	</form>
</div>
