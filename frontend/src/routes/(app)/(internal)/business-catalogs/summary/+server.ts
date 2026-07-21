import { BASE_API_URL } from '$lib/utils/constants';
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ fetch }) => {
	const empty = { count: 0, byCrit: {}, maintenance: 0 };
	try {
		const res = await fetch(`${BASE_API_URL}/delivery/business-catalogs/?page_size=1000`);
		if (!res.ok) return json(empty);
		const data = await res.json();
		const rows = Array.isArray(data) ? data : (data?.results ?? []);
		const byCrit: Record<string, number> = { critical: 0, high: 0, medium: 0, low: 0 };
		let maintenance = 0;
		for (const r of rows) {
			if (r?.criticality && byCrit[r.criticality] !== undefined) byCrit[r.criticality]++;
			maintenance += Number(r?.maintenance_annual_total ?? 0);
		}
		return json({ count: rows.length, byCrit, maintenance });
	} catch {
		return json(empty);
	}
};
