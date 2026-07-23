<script lang="ts">
	import type { ActionData, PageData } from './$types';
	import Logo from '$lib/components/Logo/Logo.svelte';
	import FormCard from './FormCard.svelte';
	import { m } from '$paraglide/messages';

	interface Props {
		data: PageData;
		form: ActionData;
	}

	let { data, form }: Props = $props();

	const seals = ['BACEN', 'LGPD', 'ISO 27001', 'SUSEP', 'ANS'];
</script>

<svelte:head>
	<title>Suricatoos CISO | {m.login()}</title>
</svelte:head>

<main class="ds-login flex min-h-screen flex-col lg:flex-row">
	<!-- Esquerda: campo índigo — terreno nativo da marca (papel-timbrado) -->
	<section
		class="ds-login-brand relative flex w-full flex-col justify-between overflow-hidden p-8 lg:w-1/2 lg:p-14"
	>
		<div class="ds-login-rail" aria-hidden="true"></div>
		<div class="flex items-center gap-3">
			<Logo height={52} width={52} />
			<span class="ds-eyebrow" style="color: var(--ds-brass-soft)"
				>SURICATOOS &middot; CISO-AS-A-SERVICE</span
			>
		</div>
		<div class="max-w-lg py-10">
			<div class="ds-eyebrow mb-3" style="color: var(--ds-brass-soft)">
				Vigilância executiva de segurança
			</div>
			<h1 class="text-4xl font-semibold leading-tight text-white lg:text-5xl">
				Inteligência e conformidade para instituições reguladas.
			</h1>
			<p class="mt-4 max-w-md text-sm" style="color: var(--ds-on-indigo-muted)">
				Programa de segurança gerido — riscos, conformidade, incidentes e evidências reunidos em um
				dossiê vivo, sempre sob vigília.
			</p>
		</div>
		<div class="flex flex-wrap items-center gap-x-5 gap-y-2">
			{#each seals as s}
				<span class="ds-seal-login ds-mono">{s}</span>
			{/each}
		</div>
	</section>

	<!-- Direita: painel de papel quente com o formulário -->
	<section
		class="ds-login-paper flex w-full items-center justify-center p-8 lg:w-1/2 lg:p-14"
	>
		<div class="w-full max-w-md">
			<FormCard {data} {form} />
		</div>
	</section>
</main>

<style>
	.ds-login-brand {
		background: linear-gradient(160deg, var(--ds-indigo) 0%, var(--ds-indigo-deep) 100%);
		color: var(--ds-on-indigo);
	}
	.ds-login-rail {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		height: 3px;
		background: var(--ds-brass);
	}
	.ds-seal-login {
		font-size: 11px;
		letter-spacing: 0.08em;
		color: var(--ds-on-indigo-muted);
		border-bottom: 1px solid var(--ds-brass);
		padding-bottom: 2px;
	}
	.ds-login-paper {
		background:
			radial-gradient(900px 520px at 92% -12%, oklch(94% 0.02 86deg), transparent 60%),
			linear-gradient(160deg, var(--ds-paper), oklch(93% 0.012 84deg));
	}
	:global(.dark) .ds-login-paper {
		background: linear-gradient(160deg, var(--color-surface-900), var(--color-surface-950));
	}
</style>
