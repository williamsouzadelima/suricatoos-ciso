<script lang="ts">
	let { children } = $props();
</script>

<!-- Fundo premium animado (gradiente indigo + orbs) — estilos globais em app.css -->
<div class="st-auth-bg" aria-hidden="true">
	<div class="st-auth-orb st-auth-orb-1"></div>
	<div class="st-auth-orb st-auth-orb-2"></div>
</div>

<div class="relative z-10">
	{@render children?.()}
</div>
