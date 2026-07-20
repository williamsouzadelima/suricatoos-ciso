import { BASE_API_URL } from '$lib/utils/constants';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, params }) => {
	const [engRes, tasksRes] = await Promise.all([
		fetch(`${BASE_API_URL}/delivery/engagements/${params.id}/`),
		fetch(`${BASE_API_URL}/delivery/plan-tasks/?engagement=${params.id}`)
	]);
	const engagement = engRes.ok ? await engRes.json() : null;
	const tasksData = tasksRes.ok ? await tasksRes.json() : { results: [] };
	return { engagement, tasks: tasksData.results ?? tasksData };
};
