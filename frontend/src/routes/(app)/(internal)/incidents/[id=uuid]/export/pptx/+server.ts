import { BASE_API_URL } from '$lib/utils/constants';
import { error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ fetch, params }) => {
	const endpoint = `${BASE_API_URL}/delivery/incident-response-plans/report_pptx/?incident=${params.id}`;
	const inc = await fetch(`${BASE_API_URL}/incidents/${params.id}/`).then((r) => r.json());
	const res = await fetch(endpoint);
	if (!res.ok) {
		error(400, 'Error generating incident PIR report');
	}
	const name = inc?.name ?? inc?.str ?? 'incidente';
	const safeName = String(name).replace(/[^a-zA-Z0-9._-]/g, '_');
	const fileName = `pir-${safeName}-${new Date().toISOString().slice(0, 10)}.pptx`;
	return new Response(res.body, {
		headers: {
			'Content-Type':
				'application/vnd.openxmlformats-officedocument.presentationml.presentation',
			'Content-Disposition': `attachment; filename="${fileName}"`,
			'Transfer-Encoding': 'chunked'
		}
	});
};
