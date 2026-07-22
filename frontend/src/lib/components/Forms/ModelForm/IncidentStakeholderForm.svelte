<script lang="ts">
	import AutocompleteSelect from '../AutocompleteSelect.svelte';
	import TextField from '$lib/components/Forms/TextField.svelte';
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
	field="party"
	options={model.selectOptions?.['party']}
	nullable={false}
	cacheLock={cacheLocks['party']}
	bind:cachedValue={formDataCache['party']}
	label={m.party()}
/>
<AutocompleteSelect
	{form}
	optionsEndpoint="actors"
	optionsExtraFields={[['name', 'str']]}
	field="actor"
	nullable
	cacheLock={cacheLocks['actor']}
	bind:cachedValue={formDataCache['actor']}
	label={m.actor()}
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
	field="cadence"
	label={m.cadence()}
	cacheLock={cacheLocks['cadence']}
	bind:cachedValue={formDataCache['cadence']}
/>
<TextField
	{form}
	field="note"
	label={m.note()}
	cacheLock={cacheLocks['note']}
	bind:cachedValue={formDataCache['note']}
/>
