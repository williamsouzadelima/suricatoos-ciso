import { BASE_API_URL } from '$lib/utils/constants';
import { json, error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ fetch, request }) => {
	const form = await request.formData();
	const res = await fetch(`${BASE_API_URL}/delivery/engagements/provider_logo/`, {
		method: 'POST',
		body: form
	});
	if (!res.ok) error(res.status, 'Falha ao enviar o logo do provedor');
	return json(await res.json());
};
