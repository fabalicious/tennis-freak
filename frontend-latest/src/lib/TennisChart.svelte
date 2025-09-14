<script lang="ts">
	import { onMount } from 'svelte';
	import * as d3 from 'd3';
	import type { Ranking } from './api';

	export let data: Ranking[] = [];
	export let width = 800;
	export let height = 400;

	let chartContainer: HTMLDivElement;

	const margin = { top: 20, right: 160, bottom: 40, left: 50 };
	const chartWidth = width - margin.left - margin.right;
	const chartHeight = height - margin.top - margin.bottom;

	function drawChart() {
		if (!data.length || !chartContainer) return;

		// Clear previous chart
		d3.select(chartContainer).selectAll('*').remove();

		// Group data by player
		const playerData = d3.group(data, (d) => d.player_name);

		// Parse dates and sort
		const parsedData = Array.from(playerData, ([player, rankings]) => ({
			player,
			rankings: rankings
				.map((d) => ({
					...d,
					parsedDate: d3.timeParse('%Y-%m-%d')(d.date)!
				}))
				.sort((a, b) => a.parsedDate.getTime() - b.parsedDate.getTime())
		}));

		// Set up scales
		const xScale = d3
			.scaleTime()
			.domain(d3.extent(data, (d) => d3.timeParse('%Y-%m-%d')(d.date)!) as [Date, Date])
			.range([0, chartWidth]);

		const yScale = d3
			.scaleLinear()
			.domain([1, d3.max(data, (d) => d.ranking) || 10])
			.range([0, chartHeight]); // Inverted for rankings (1 at top)

		const colorScale = d3
			.scaleOrdinal(d3.schemeCategory10)
			.domain(Array.from(playerData.keys()));

		// Create SVG
		const svg = d3
			.select(chartContainer)
			.append('svg')
			.attr('width', width)
			.attr('height', height);

		const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

		// Add axes
		g.append('g')
			.attr('transform', `translate(0,${chartHeight})`)
			.call(d3.axisBottom(xScale).tickFormat(d3.timeFormat('%d %b')));

		g.append('g').call(
			d3
				.axisLeft(yScale)
				.tickFormat((d) => `#${d}`)
				.ticks(10)
		);

		// Add axis labels
		g.append('text')
			.attr('transform', 'rotate(-90)')
			.attr('y', 0 - margin.left)
			.attr('x', 0 - chartHeight / 2)
			.attr('dy', '1em')
			.style('text-anchor', 'middle')
			.style('font-size', '12px')
			.text('ATP Ranking');

		g.append('text')
			.attr('transform', `translate(${chartWidth / 2}, ${chartHeight + margin.bottom})`)
			.style('text-anchor', 'middle')
			.style('font-size', '12px')
			.text('Date');

		// Line generator
		const line = d3
			.line<any>()
			.x((d) => xScale(d.parsedDate))
			.y((d) => yScale(d.ranking))
			.curve(d3.curveMonotoneX);

		// Draw lines for each player
		parsedData.forEach(({ player, rankings }) => {
			if (rankings.length < 2) return;

			g.append('path')
				.datum(rankings)
				.attr('fill', 'none')
				.attr('stroke', colorScale(player))
				.attr('stroke-width', 2)
				.attr('d', line);

			// Add dots for data points
			g.selectAll(`.dot-${player.replace(/\s+/g, '')}`)
				.data(rankings)
				.enter()
				.append('circle')
				.attr('class', `dot-${player.replace(/\s+/g, '')}`)
				.attr('cx', (d) => xScale(d.parsedDate))
				.attr('cy', (d) => yScale(d.ranking))
				.attr('r', 3)
				.attr('fill', colorScale(player))
				.on('mouseover', function (event, d) {
					// Tooltip
					const tooltip = d3
						.select('body')
						.append('div')
						.attr('class', 'tooltip')
						.style('position', 'absolute')
						.style('padding', '8px')
						.style('background', 'rgba(0,0,0,0.8)')
						.style('color', 'white')
						.style('border-radius', '4px')
						.style('font-size', '12px')
						.style('pointer-events', 'none')
						.style('opacity', 0);

					tooltip.transition().duration(200).style('opacity', 1);

					tooltip
						.html(
							`<strong>${d.player_name}</strong><br/>
							 Ranking: #${d.ranking}<br/>
							 Points: ${d.points.toLocaleString()}<br/>
							 Date: ${d3.timeFormat('%b %d, %Y')(d.parsedDate)}`
						)
						.style('left', event.pageX + 10 + 'px')
						.style('top', event.pageY - 10 + 'px');
				})
				.on('mouseout', function () {
					d3.selectAll('.tooltip').remove();
				});
		});

		// Legend
		const legend = g
			.selectAll('.legend')
			.data(Array.from(playerData.keys()).slice(0, 8)) // Show top 8 players in legend
			.enter()
			.append('g')
			.attr('class', 'legend')
			.attr('transform', (d, i) => `translate(${chartWidth + 10}, ${i * 20})`);

		legend
			.append('rect')
			.attr('x', 0)
			.attr('width', 12)
			.attr('height', 2)
			.style('fill', colorScale);

		legend
			.append('text')
			.attr('x', 16)
			.attr('y', 0)
			.attr('dy', '0.32em')
			.style('font-size', '11px')
			.text((d) => d);
	}

	onMount(() => {
		drawChart();
	});

	$: if (data.length && chartContainer) {
		drawChart();
	}
</script>

<div bind:this={chartContainer} class="chart-container">
	{#if !data.length}
		<div class="loading">Loading tennis rankings...</div>
	{/if}
</div>

<style>
	.chart-container {
		width: 100%;
		height: 100%;
		position: relative;
	}

	.loading {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 400px;
		font-size: 18px;
		color: #666;
	}

	:global(.tooltip) {
		z-index: 1000;
	}
</style>