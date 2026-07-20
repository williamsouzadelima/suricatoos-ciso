<script lang="ts">
	import { onMount } from 'svelte';

	interface Props {
		name?: string;
		actual?: [string, number][];
		ideal?: [string, number][] | null;
		height?: string;
		labelActual?: string;
		labelIdeal?: string;
	}

	let {
		name = 'eng',
		actual = [],
		ideal = null,
		height = 'h-72',
		labelActual = 'Actual',
		labelIdeal = 'Ideal'
	}: Props = $props();

	const chartId = `${name}_burndown`;

	onMount(async () => {
		const echarts = await import('echarts');
		const el = document.getElementById(chartId);
		if (!el) return;
		const chart = echarts.init(
			el,
			document.documentElement.classList.contains('dark') ? 'dark' : null,
			{ renderer: 'svg' }
		);
		const series: unknown[] = [];
		if (ideal && ideal.length) {
			series.push({
				name: labelIdeal,
				type: 'line',
				symbol: 'none',
				lineStyle: { type: 'dashed', color: '#94a3b8' },
				data: ideal
			});
		}
		series.push({
			name: labelActual,
			type: 'line',
			smooth: true,
			symbol: 'circle',
			lineStyle: { color: '#6366f1', width: 2 },
			itemStyle: { color: '#6366f1' },
			areaStyle: { opacity: 0.12, color: '#6366f1' },
			data: actual
		});
		chart.setOption({
			backgroundColor: 'transparent',
			grid: { left: 44, right: 16, top: 30, bottom: 28 },
			tooltip: { trigger: 'axis' },
			legend: { top: 0, textStyle: { color: '#94a3b8' } },
			xAxis: { type: 'time', axisLabel: { color: '#94a3b8' } },
			yAxis: { type: 'value', min: 0, splitLine: { show: false }, axisLabel: { color: '#94a3b8' } },
			series
		});
		const ro = new ResizeObserver(() => chart.resize());
		ro.observe(el);
	});
</script>

<div id={chartId} class="{height} w-full"></div>
