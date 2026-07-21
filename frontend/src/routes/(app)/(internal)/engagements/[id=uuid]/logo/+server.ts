import { BASE_API_URL } from '$lib/utils/constants';
import { json, error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ fetch, params, request }) => {
	const form = await request.formData();
	const res = await fetch(`${BASE_API_URL}/delivery/engagements/${params.id}/upload_logo/`, {
		method: 'POST',
		body: form
	});
	if (!res.ok) error(res.status, 'Falha ao enviar o logo do cliente');
	return json(await res.json());
};

export const DELETE: RequestHandler = async ({ fetch, params }) => {
	const res = await fetch(`${BASE_API_URL}/delivery/engagements/${params.id}/remove_logo/`, {
		method: 'POST'
	});
	if (!res.ok) error(res.status, 'Falha ao remover o logo');
	return json(await res.json());
};
