import { BASE_API_URL } from '$lib/utils/constants';
import { json, error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ fetch, params, request }) => {
	const body = await request.json().catch(() => ({}));
	const res = await fetch(`${BASE_API_URL}/delivery/engagements/${params.id}/fetch_logo/`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ domain: body?.domain ?? '' })
	});
	if (!res.ok) {
		const t = await res.text();
		error(res.status, t.slice(0, 200) || 'Falha ao buscar o logo pelo domínio');
	}
	return json(await res.json());
};
