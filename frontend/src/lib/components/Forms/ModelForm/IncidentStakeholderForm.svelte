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
<TextField
	{form}
	field="title"
	label={m.title()}
	cacheLock={cacheLocks['title']}
	bind:cachedValue={formDataCache['title']}
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
	field="contact"
	label={m.contact()}
	cacheLock={cacheLocks['contact']}
	bind:cachedValue={formDataCache['contact']}
/>
<AutocompleteSelect
	{form}
	field="when_to_notify"
	options={model.selectOptions?.['when_to_notify']}
	nullable={false}
	cacheLock={cacheLocks['when_to_notify']}
	bind:cachedValue={formDataCache['when_to_notify']}
	label={m.whenToNotify()}
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
	field="message_template"
	label={m.messageTemplate()}
	cacheLock={cacheLocks['message_template']}
	bind:cachedValue={formDataCache['message_template']}
/>
<TextField
	{form}
	field="note"
	label={m.note()}
	cacheLock={cacheLocks['note']}
	bind:cachedValue={formDataCache['note']}
/>
