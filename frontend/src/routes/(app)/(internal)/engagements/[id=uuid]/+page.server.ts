import { error } from '@sveltejs/kit';
import { BASE_API_URL } from '$lib/utils/constants';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, params }) => {
	const engRes = await fetch(`${BASE_API_URL}/delivery/engagements/${params.id}/`);
	if (!engRes.ok) throw error(engRes.status, 'Engagement not found');
	const [dashRes, capRes, trRes, bdRes] = await Promise.all([
		fetch(`${BASE_API_URL}/delivery/engagements/${params.id}/dashboard/`),
		fetch(`${BASE_API_URL}/delivery/engagements/${params.id}/capacity/`),
		fetch(`${BASE_API_URL}/delivery/engagements/${params.id}/team_resources/`),
		fetch(`${BASE_API_URL}/delivery/engagements/${params.id}/burn_down/`)
	]);
	return {
		engagement: await engRes.json(),
		dashboard: dashRes.ok ? await dashRes.json() : null,
		capacity: capRes.ok ? await capRes.json() : null,
		teamResources: trRes.ok ? await trRes.json() : null,
		burnDown: bdRes.ok ? await bdRes.json() : null
	};
};
