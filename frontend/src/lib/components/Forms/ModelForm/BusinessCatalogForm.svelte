<script lang="ts">
	import AutocompleteSelect from '../AutocompleteSelect.svelte';
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
	field="criticality"
	options={model.selectOptions?.['criticality']}
	nullable={false}
	cacheLock={cacheLocks['criticality']}
	bind:cachedValue={formDataCache['criticality']}
	label={m.criticality()}
/>
<AutocompleteSelect
	{form}
	field="currency"
	options={model.selectOptions?.['currency']}
	cacheLock={cacheLocks['currency']}
	bind:cachedValue={formDataCache['currency']}
	label={m.currency()}
/>
<AutocompleteSelect
	{form}
	optionsEndpoint="engagements"
	field="engagement"
	cacheLock={cacheLocks['engagement']}
	bind:cachedValue={formDataCache['engagement']}
	label={m.engagement()}
/>
<NumberField
	{form}
	field="collaborators"
	label={m.collaborators()}
	cacheLock={cacheLocks['collaborators']}
	bind:cachedValue={formDataCache['collaborators']}
/>
<NumberField
	{form}
	field="collaborator_hourly_cost"
	step={0.01}
	label={m.collaboratorHourlyCost()}
	cacheLock={cacheLocks['collaborator_hourly_cost']}
	bind:cachedValue={formDataCache['collaborator_hourly_cost']}
/>
<NumberField
	{form}
	field="hourly_revenue"
	step={0.01}
	label={m.hourlyRevenue()}
	cacheLock={cacheLocks['hourly_revenue']}
	bind:cachedValue={formDataCache['hourly_revenue']}
/>
<NumberField
	{form}
	field="profit_margin"
	step={0.01}
	label={m.profitMargin()}
	cacheLock={cacheLocks['profit_margin']}
	bind:cachedValue={formDataCache['profit_margin']}
/>
<NumberField
	{form}
	field="regulatory_hourly"
	step={0.01}
	label={m.regulatoryHourly()}
	cacheLock={cacheLocks['regulatory_hourly']}
	bind:cachedValue={formDataCache['regulatory_hourly']}
/>
<NumberField
	{form}
	field="regulatory_fixed"
	step={0.01}
	label={m.regulatoryFixed()}
	cacheLock={cacheLocks['regulatory_fixed']}
	bind:cachedValue={formDataCache['regulatory_fixed']}
/>
<NumberField
	{form}
	field="maintenance_extra_annual"
	step={0.01}
	label={m.maintenanceExtraAnnual()}
	cacheLock={cacheLocks['maintenance_extra_annual']}
	bind:cachedValue={formDataCache['maintenance_extra_annual']}
/>
