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
	optionsEndpoint="incidents"
	field="incident"
	cacheLock={cacheLocks['incident']}
	bind:cachedValue={formDataCache['incident']}
	label={m.incident()}
/>
<TextField
	{form}
	field="currency"
	label={m.currency()}
	cacheLock={cacheLocks['currency']}
	bind:cachedValue={formDataCache['currency']}
/>
<NumberField
	{form}
	field="downtime_hours"
	step={0.01}
	label={m.downtimeHours()}
	cacheLock={cacheLocks['downtime_hours']}
	bind:cachedValue={formDataCache['downtime_hours']}
/>
<NumberField
	{form}
	field="vendor_forensics"
	step={0.01}
	label={m.vendorForensics()}
	cacheLock={cacheLocks['vendor_forensics']}
	bind:cachedValue={formDataCache['vendor_forensics']}
/>
<NumberField
	{form}
	field="vendor_legal"
	step={0.01}
	label={m.vendorLegal()}
	cacheLock={cacheLocks['vendor_legal']}
	bind:cachedValue={formDataCache['vendor_legal']}
/>
<NumberField
	{form}
	field="other_external"
	step={0.01}
	label={m.otherExternal()}
	cacheLock={cacheLocks['other_external']}
	bind:cachedValue={formDataCache['other_external']}
/>
<NumberField
	{form}
	field="regulatory_fines"
	step={0.01}
	label={m.regulatoryFines()}
	cacheLock={cacheLocks['regulatory_fines']}
	bind:cachedValue={formDataCache['regulatory_fines']}
/>
<TextField
	{form}
	field="notes"
	label={m.notes()}
	cacheLock={cacheLocks['notes']}
	bind:cachedValue={formDataCache['notes']}
/>
