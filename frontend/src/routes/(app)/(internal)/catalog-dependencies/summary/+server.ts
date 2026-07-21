import { BASE_API_URL } from '$lib/utils/constants';
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ fetch }) => {
	const empty = { count: 0, catalogs: 0, withAsset: 0 };
	try {
		const res = await fetch(`${BASE_API_URL}/delivery/catalog-dependencies/?page_size=1000`);
		if (!res.ok) return json(empty);
		const data = await res.json();
		const rows = Array.isArray(data) ? data : (data?.results ?? []);
		const cats = new Set<string>();
		let withAsset = 0;
		for (const r of rows) {
			const cat = r?.catalog?.id ?? r?.catalog;
			if (cat) cats.add(String(cat));
			if (r?.asset) withAsset++;
		}
		return json({ count: rows.length, catalogs: cats.size, withAsset });
	} catch {
		return json(empty);
	}
};
