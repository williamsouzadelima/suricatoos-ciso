import { BASE_API_URL } from '$lib/utils/constants';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, params }) => {
	const [catRes, impRes] = await Promise.all([
		fetch(`${BASE_API_URL}/delivery/business-catalogs/${params.id}/`),
		fetch(`${BASE_API_URL}/delivery/business-catalogs/${params.id}/impact/`)
	]);
	if (!catRes.ok) throw error(catRes.status, 'Catálogo não encontrado');
	return {
		catalog: await catRes.json(),
		impact: impRes.ok ? await impRes.json() : null
	};
};
