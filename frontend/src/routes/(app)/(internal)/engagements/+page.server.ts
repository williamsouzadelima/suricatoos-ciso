import { BASE_API_URL } from '$lib/utils/constants';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	const res = await fetch(`${BASE_API_URL}/delivery/engagements/`);
	const data = res.ok ? await res.json() : { results: [] };
	return { engagements: data.results ?? data };
};
