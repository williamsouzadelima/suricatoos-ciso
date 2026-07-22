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
	field="regulator"
	label={m.regulator()}
	cacheLock={cacheLocks['regulator']}
	bind:cachedValue={formDataCache['regulator']}
/>
<TextField
	{form}
	field="obligation_ref"
	label={m.obligationRef()}
	cacheLock={cacheLocks['obligation_ref']}
	bind:cachedValue={formDataCache['obligation_ref']}
/>
<AutocompleteSelect
	{form}
	field="status"
	options={model.selectOptions?.['status']}
	nullable={false}
	cacheLock={cacheLocks['status']}
	bind:cachedValue={formDataCache['status']}
	label={m.status()}
/>
<NumberField
	{form}
	field="deadline_hours"
	label={m.deadlineHours()}
	cacheLock={cacheLocks['deadline_hours']}
	bind:cachedValue={formDataCache['deadline_hours']}
/>
<TextField
	{form}
	field="qualitative_note"
	label={m.qualitativeNote()}
	cacheLock={cacheLocks['qualitative_note']}
	bind:cachedValue={formDataCache['qualitative_note']}
/>
<TextField
	{form}
	field="channel"
	label={m.channel()}
	cacheLock={cacheLocks['channel']}
	bind:cachedValue={formDataCache['channel']}
/>
<TextField
	{form}
	field="template_text"
	label={m.templateText()}
	cacheLock={cacheLocks['template_text']}
	bind:cachedValue={formDataCache['template_text']}
/>
<AutocompleteSelect
	{form}
	multiple
	optionsEndpoint="evidences"
	field="evidences"
	cacheLock={cacheLocks['evidences']}
	bind:cachedValue={formDataCache['evidences']}
	label={m.evidences()}
/>
