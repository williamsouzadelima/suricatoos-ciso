import { BASE_API_URL } from '$lib/utils/constants';
import { fail } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';

async function j(fetchFn: typeof fetch, url: string, fallback: any) {
	try {
		const r = await fetchFn(url);
		if (!r.ok) return fallback;
		return await r.json();
	} catch {
		return fallback;
	}
}

export const load: PageServerLoad = async ({ fetch, url }) => {
	const incRaw = await j(fetch, `${BASE_API_URL}/incidents/`, { results: [] });
	const notifRaw = await j(fetch, `${BASE_API_URL}/delivery/regulatory-notifications/`, {
		results: []
	});
	const incidents = incRaw.results ?? incRaw ?? [];
	const notifs = notifRaw.results ?? notifRaw ?? [];

	const open = incidents.filter((i: any) => ['new', 'ongoing'].includes(i.status)).length;
	const overdue = notifs.filter((n: any) => n.is_overdue).length;
	const bySeverity: Record<string, number> = {};
	for (const i of incidents) {
		const k = String(i.severity ?? 6);
		bySeverity[k] = (bySeverity[k] ?? 0) + 1;
	}

	const selectedId = url.searchParams.get('incident');
	let selected: any = null;
	if (selectedId) {
		const [summary, cost, notifications] = await Promise.all([
			j(fetch, `${BASE_API_URL}/delivery/incident-response-plans/summary/?incident=${selectedId}`, null),
			j(fetch, `${BASE_API_URL}/delivery/incident-response-plans/cost/?incident=${selectedId}`, null),
			j(fetch, `${BASE_API_URL}/delivery/incident-response-plans/notifications/?incident=${selectedId}`, [])
		]);
		const incident = incidents.find((i: any) => i.id === selectedId) ?? null;
		selected = { id: selectedId, incident, summary, cost, notifications };
	}

	return {
		title: 'Resposta a incidentes',
		incidents,
		open,
		total: incidents.length,
		notifTotal: notifs.length,
		overdue,
		bySeverity,
		selected
	};
};

export const actions: Actions = {
	seed: async ({ fetch, request }) => {
		const fd = await request.formData();
		const incident = fd.get('incident');
		const standard = fd.get('standard') || 'nist-800-61';
		const res = await fetch(`${BASE_API_URL}/delivery/incident-response-plans/seed_plan/`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ incident, standard })
		});
		if (!res.ok) return fail(res.status, { error: (await res.text()).slice(0, 200) });
		return { seeded: await res.json() };
	},
	resolve: async ({ fetch, request }) => {
		const fd = await request.formData();
		const incident = fd.get('incident');
		const res = await fetch(
			`${BASE_API_URL}/delivery/incident-response-plans/seed_notifications/`,
			{
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ incident })
			}
		);
		if (!res.ok) return fail(res.status, { error: (await res.text()).slice(0, 200) });
		return { resolved: await res.json() };
	}
};
