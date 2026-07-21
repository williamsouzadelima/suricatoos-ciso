import { BASE_API_URL } from '$lib/utils/constants';
import { m } from '$paraglide/messages';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	const res = await fetch(`${BASE_API_URL}/delivery/engagements/`);
	const data = res.ok ? await res.json() : { results: [] };
	return { engagements: data.results ?? data, title: m.engagements() };
};
