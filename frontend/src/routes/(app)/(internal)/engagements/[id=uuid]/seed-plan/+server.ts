import { BASE_API_URL } from '$lib/utils/constants';
import { json, error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ fetch, params, request }) => {
	const body = await request.json().catch(() => ({}));
	const res = await fetch(`${BASE_API_URL}/delivery/engagements/${params.id}/seed_plan/`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({
			template: body?.template ?? 'vciso-100d',
			modules: Array.isArray(body?.modules) ? body.modules : []
		})
	});
	if (!res.ok) {
		const t = await res.text();
		error(res.status, t.slice(0, 200) || 'Falha ao semear o plano');
	}
	return json(await res.json());
};
