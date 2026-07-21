import { BASE_API_URL } from '$lib/utils/constants';
import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	const [ssRes, hmRes] = await Promise.all([
		fetch(`${BASE_API_URL}/delivery/client-intakes/subsector/`),
		fetch(`${BASE_API_URL}/delivery/engagements/hours_model/`)
	]);
	return {
		subsectors: ssRes.ok ? await ssRes.json() : {},
		hoursModels: hmRes.ok ? await hmRes.json() : {}
	};
};

export const actions: Actions = {
	default: async ({ fetch, request }) => {
		const fd = await request.formData();
		const body = {
			company_name: String(fd.get('company_name') ?? '').trim(),
			website: String(fd.get('website') ?? '').trim(),
			subsector: String(fd.get('subsector') ?? ''),
			day_zero: String(fd.get('day_zero') ?? ''),
			contracted_hours: fd.get('contracted_hours') ? Number(fd.get('contracted_hours')) : null,
			hours_model: String(fd.get('hours_model') ?? 'budget'),
			modules: fd.getAll('modules').map(String),
			create_assessments: fd.get('create_assessments') === 'on'
		};
		if (!body.company_name || !body.day_zero) {
			return fail(400, { error: 'Razão social e data de início são obrigatórias.', values: body });
		}
		const res = await fetch(`${BASE_API_URL}/delivery/engagements/onboard/`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(body)
		});
		if (!res.ok) {
			const txt = await res.text();
			return fail(res.status, {
				error: `Falha no provisionamento (${res.status}): ${txt.slice(0, 200)}`,
				values: body
			});
		}
		const out = await res.json();
		redirect(303, `/engagements/${out.engagement}`);
	}
};
