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
	optionsEndpoint="actors"
	optionsExtraFields={[['name', 'str']]}
	field="actor"
	cacheLock={cacheLocks['actor']}
	bind:cachedValue={formDataCache['actor']}
	label={m.actor()}
/>
<AutocompleteSelect
	{form}
	field="role"
	options={model.selectOptions?.['role']}
	nullable={false}
	cacheLock={cacheLocks['role']}
	bind:cachedValue={formDataCache['role']}
	label={m.role()}
/>
<AutocompleteSelect
	{form}
	field="raci"
	options={model.selectOptions?.['raci']}
	nullable={false}
	cacheLock={cacheLocks['raci']}
	bind:cachedValue={formDataCache['raci']}
	label={m.raci()}
/>
<TextField
	{form}
	field="note"
	label={m.note()}
	cacheLock={cacheLocks['note']}
	bind:cachedValue={formDataCache['note']}
/>
