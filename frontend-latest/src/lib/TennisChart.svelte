<script lang="ts">
	import { onMount } from 'svelte';
	import * as d3 from 'd3';
	import type { Ranking } from './api';

	export let data: Ranking[] = [];
	export let width = 800;
	export let height = 400;
	export let showPoints = false; // New prop for toggle

	let chartContainer: HTMLDivElement;

	const margin = { top: 20, right: 50, bottom: 40, left: 200 };
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

		// Custom y-scale logic for rankings vs points
		let yScale: d3.ScaleLinear<number, number>;

		if (showPoints) {
			// For points view: create a custom scale where 1st and 10th place stay fixed
			// Find the points range for players ranked 1-10 to keep positions proportional
			const rankedData = data.filter(d => d.ranking >= 1 && d.ranking <= 10);
			const minPoints = d3.min(rankedData, (d) => d.points) || 0;
			const maxPoints = d3.max(rankedData, (d) => d.points) || 10000;

			// Create scale that maps points to chart positions, keeping extremes fixed
			yScale = d3.scaleLinear()
				.domain([maxPoints, minPoints]) // Inverted (higher points at top)
				.range([0, chartHeight]);
		} else {
			// For rankings view: normal ranking scale
			yScale = d3.scaleLinear()
				.domain([1, d3.max(data, (d) => d.ranking) || 10])
				.range([0, chartHeight]); // Inverted for rankings (1 at top)
		}

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
				.tickFormat((d) => showPoints ? d.toLocaleString() : `#${d}`)
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
			.text(showPoints ? 'ATP Points' : 'ATP Ranking');

		g.append('text')
			.attr('transform', `translate(${chartWidth / 2}, ${chartHeight + margin.bottom})`)
			.style('text-anchor', 'middle')
			.style('font-size', '12px')
			.text('Date');

		// Line generator
		const line = d3
			.line<any>()
			.x((d) => xScale(d.parsedDate))
			.y((d) => yScale(showPoints ? d.points : d.ranking))
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
				.attr('cy', (d) => yScale(showPoints ? d.points : d.ranking))
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

		// Create ranking legend data (latest ranking and points for each player)
		const latestDate = d3.max(data, (d) => d.date);
		const latestRankings = data
			.filter(d => d.date === latestDate && d.ranking <= 10)
			.sort((a, b) => a.ranking - b.ranking)
			.slice(0, 10);

		// Left-side ranking legend
		const legend = g
			.selectAll('.legend')
			.data(latestRankings)
			.enter()
			.append('g')
			.attr('class', 'legend')
			.attr('transform', (d, i) => `translate(-180, ${(chartHeight / 10) * i + 20})`);

		// Ranking number
		legend
			.append('text')
			.attr('x', 0)
			.attr('y', 0)
			.attr('dy', '0.35em')
			.style('font-size', '16px')
			.style('font-weight', 'bold')
			.style('fill', '#333')
			.text((d) => `${d.ranking}.`);

		// Color dot
		legend
			.append('circle')
			.attr('cx', 25)
			.attr('cy', 0)
			.attr('r', 6)
			.style('fill', (d) => colorScale(d.player_name));

		// Player name
		legend
			.append('text')
			.attr('x', 35)
			.attr('y', 0)
			.attr('dy', '0.35em')
			.style('font-size', '14px')
			.style('font-weight', '500')
			.style('fill', '#333')
			.text((d) => d.player_name);

		// Points
		legend
			.append('text')
			.attr('x', 35)
			.attr('y', 15)
			.attr('dy', '0.35em')
			.style('font-size', '12px')
			.style('fill', '#666')
			.text((d) => `${d.points.toLocaleString()} points`);
	}

	onMount(() => {
		drawChart();
	});

	$: if (data.length && chartContainer) {
		drawChart();
	}

	$: if (chartContainer && showPoints !== undefined) {
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