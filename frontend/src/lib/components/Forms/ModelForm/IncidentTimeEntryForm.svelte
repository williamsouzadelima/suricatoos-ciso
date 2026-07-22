<script lang="ts">
	import AutocompleteSelect from '../AutocompleteSelect.svelte';
	import TextField from '$lib/components/Forms/TextField.svelte';
	import NumberField from '$lib/components/Forms/NumberField.svelte';
	import Checkbox from '$lib/components/Forms/Checkbox.svelte';
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
<AutocompleteSelect
	{form}
	optionsEndpoint="applied-controls"
	field="applied_control"
	nullable
	cacheLock={cacheLocks['applied_control']}
	bind:cachedValue={formDataCache['applied_control']}
	label={m.appliedControl()}
/>
<AutocompleteSelect
	{form}
	optionsEndpoint="users"
	field="user"
	nullable
	cacheLock={cacheLocks['user']}
	bind:cachedValue={formDataCache['user']}
	label={m.user()}
/>
<NumberField
	{form}
	field="hours"
	step={0.25}
	label={m.hours()}
	cacheLock={cacheLocks['hours']}
	bind:cachedValue={formDataCache['hours']}
/>
<TextField
	{form}
	type="date"
	field="date"
	label={m.date()}
	cacheLock={cacheLocks['date']}
	bind:cachedValue={formDataCache['date']}
/>
<Checkbox {form} field="billable" label={m.billable()} />
<TextField
	{form}
	field="note"
	label={m.note()}
	cacheLock={cacheLocks['note']}
	bind:cachedValue={formDataCache['note']}
/>
