<script lang="ts">
	import AutocompleteSelect from '../AutocompleteSelect.svelte';
	import TextField from '$lib/components/Forms/TextField.svelte';
	import NumberField from '$lib/components/Forms/NumberField.svelte';
	import type { SuperValidated } from 'sveltekit-superforms';
	import type { ModelInfo, CacheLock } from '$lib/utils/types';
	import { m } from '$paraglide/messages';

	interface Props {
		form: SuperValidated<any>;
		model: ModelInfo;
		cacheLocks?: Record<string, CacheLock>;
		formDataCache?: Record<string, any>;
		initialData?: Record<string, any>;
		object?: any;
	}

	let {
		form,
		model,
		cacheLocks = {},
		formDataCache = $bindable({}),
		initialData = {},
		object = {}
	}: Props = $props();
</script>

<AutocompleteSelect
	{form}
	optionsEndpoint="business-catalogs"
	field="catalog"
	cacheLock={cacheLocks['catalog']}
	bind:cachedValue={formDataCache['catalog']}
	label={m.catalog()}
/>
<AutocompleteSelect
	{form}
	optionsEndpoint="assets"
	field="asset"
	cacheLock={cacheLocks['asset']}
	bind:cachedValue={formDataCache['asset']}
	label={m.asset()}
/>
<NumberField
	{form}
	field="annual_cost"
	step={0.01}
	label={m.annualCost()}
	cacheLock={cacheLocks['annual_cost']}
	bind:cachedValue={formDataCache['annual_cost']}
/>
<TextField
	{form}
	field="observation"
	label={m.observation()}
	cacheLock={cacheLocks['observation']}
	bind:cachedValue={formDataCache['observation']}
/>
