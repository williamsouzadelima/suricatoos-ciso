import { BASE_API_URL } from '$lib/utils/constants';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, params }) => {
	const [engRes, eisRes] = await Promise.all([
		fetch(`${BASE_API_URL}/delivery/engagements/${params.id}/`),
		fetch(`${BASE_API_URL}/delivery/plan-tasks/eisenhower/?engagement=${params.id}`)
	]);
	return {
		engagement: engRes.ok ? await engRes.json() : null,
		matrix: eisRes.ok
			? await eisRes.json()
			: { horizon_days: 21, quadrants: { do: [], schedule: [], delegate: [], eliminate: [] } }
	};
};
