<script lang="ts">
	import { onMount } from 'svelte';
	import TennisChart from '$lib/TennisChart.svelte';
	import { api, type Ranking, type Player } from '$lib/api';

	let rankings: Ranking[] = [];
	let players: Player[] = [];
	let loading = true;
	let error = '';
	let selectedDateRange = '3months';
	let showPoints = false;

	const dateRanges = {
		'1month': { label: '1 Month', days: 30 },
		'3months': { label: '3 Months', days: 90 },
		'6months': { label: '6 Months', days: 180 },
		'1year': { label: '1 Year', days: 365 }
	};

	function formatDate(date: Date): string {
		return date.toISOString().split('T')[0];
	}

	function getDateRange(days: number) {
		const endDate = new Date();
		const startDate = new Date();
		startDate.setDate(endDate.getDate() - days);
		return {
			startDate: formatDate(startDate),
			endDate: formatDate(endDate)
		};
	}

	async function loadData() {
		try {
			loading = true;
			error = '';

			const { startDate, endDate } = getDateRange(dateRanges[selectedDateRange].days);

			const [rankingsData, playersData] = await Promise.all([
				api.getRankingsRange(startDate, endDate, 10),
				api.getPlayers()
			]);

			rankings = rankingsData;
			players = playersData;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load data';
			console.error('Error loading data:', err);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});

	$: if (selectedDateRange) {
		loadData();
	}
</script>

<svelte:head>
	<title>ATP Tennis Rankings Visualization</title>
	<meta name="description" content="Interactive ATP tennis rankings over time" />
</svelte:head>

<div class="container">
	<header>
		<h1>🎾 ATP Tennis Rankings</h1>
		<p>Interactive visualization of ATP men's tennis rankings over time</p>
	</header>

	<div class="controls">
		<div class="control-group">
			<label for="dateRange">Time Period:</label>
			<select id="dateRange" bind:value={selectedDateRange}>
				{#each Object.entries(dateRanges) as [key, range]}
					<option value={key}>{range.label}</option>
				{/each}
			</select>
		</div>
		<div class="control-group">
			<label for="viewToggle">Y-Axis:</label>
			<button
				id="viewToggle"
				class="toggle-button {showPoints ? 'active' : ''}"
				on:click={() => showPoints = !showPoints}
			>
				{showPoints ? 'Points' : 'Rankings'}
			</button>
		</div>
	</div>

	{#if error}
		<div class="error">
			<h3>⚠️ Error</h3>
			<p>{error}</p>
			<button on:click={loadData}>Try Again</button>
		</div>
	{:else if loading}
		<div class="loading">
			<div class="spinner"></div>
			<p>Loading ATP rankings data...</p>
		</div>
	{:else}
		<div class="chart-section">
			<h2>Top 10 ATP {showPoints ? 'Points' : 'Rankings'} ({dateRanges[selectedDateRange].label})</h2>
			<TennisChart data={rankings} width={900} height={500} {showPoints} />
		</div>

		<div class="stats">
			<div class="stat-card">
				<h3>Data Points</h3>
				<p class="stat-value">{rankings.length.toLocaleString()}</p>
			</div>
			<div class="stat-card">
				<h3>Players Tracked</h3>
				<p class="stat-value">{players.length}</p>
			</div>
			<div class="stat-card">
				<h3>Time Span</h3>
				<p class="stat-value">{dateRanges[selectedDateRange].label}</p>
			</div>
		</div>

		<div class="info">
			<h3>About This Visualization</h3>
			<ul>
				<li>Shows ATP top 10 rankings over time with interactive line chart</li>
				<li>Hover over data points to see detailed information</li>
				<li>Each player has a unique color with legend on the right</li>
				<li>Rankings are inverted (lower is better) - #1 at top</li>
				<li>Data includes realistic fluctuations in rankings and points</li>
			</ul>
		</div>
	{/if}
</div>

<style>
	.container {
		max-width: 1200px;
		margin: 0 auto;
		padding: 20px;
		font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
	}

	header {
		text-align: center;
		margin-bottom: 40px;
	}

	h1 {
		font-size: 2.5rem;
		color: #2c5530;
		margin: 0 0 10px 0;
	}

	header p {
		font-size: 1.2rem;
		color: #666;
		margin: 0;
	}

	.controls {
		display: flex;
		justify-content: center;
		margin-bottom: 30px;
		gap: 20px;
		flex-wrap: wrap;
	}

	.control-group {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	label {
		font-weight: 600;
		color: #333;
	}

	select {
		padding: 8px 12px;
		border: 2px solid #ddd;
		border-radius: 6px;
		font-size: 14px;
		background: white;
	}

	select:focus {
		outline: none;
		border-color: #2c5530;
	}

	.toggle-button {
		padding: 8px 16px;
		border: 2px solid #ddd;
		border-radius: 6px;
		font-size: 14px;
		background: white;
		color: #333;
		cursor: pointer;
		transition: all 0.2s ease;
		min-width: 80px;
	}

	.toggle-button:hover {
		border-color: #2c5530;
		background: #f8f9fa;
	}

	.toggle-button.active {
		background: #2c5530;
		color: white;
		border-color: #2c5530;
	}

	.toggle-button:focus {
		outline: none;
		box-shadow: 0 0 0 2px rgba(44, 85, 48, 0.2);
	}

	.error {
		text-align: center;
		padding: 40px;
		background: #fee;
		border: 1px solid #fcc;
		border-radius: 8px;
		margin: 20px 0;
	}

	.error h3 {
		color: #c33;
		margin: 0 0 15px 0;
	}

	.error button {
		background: #c33;
		color: white;
		border: none;
		padding: 10px 20px;
		border-radius: 6px;
		cursor: pointer;
		margin-top: 15px;
	}

	.error button:hover {
		background: #a22;
	}

	.loading {
		text-align: center;
		padding: 60px 20px;
	}

	.spinner {
		width: 40px;
		height: 40px;
		border: 4px solid #f3f3f3;
		border-top: 4px solid #2c5530;
		border-radius: 50%;
		animation: spin 1s linear infinite;
		margin: 0 auto 20px;
	}

	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}

	.chart-section {
		background: white;
		border-radius: 12px;
		box-shadow: 0 4px 12px rgba(0,0,0,0.1);
		padding: 30px;
		margin-bottom: 30px;
	}

	.chart-section h2 {
		margin: 0 0 20px 0;
		color: #2c5530;
		font-size: 1.8rem;
	}

	.stats {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 20px;
		margin-bottom: 30px;
	}

	.stat-card {
		background: linear-gradient(135deg, #2c5530, #3a6b3e);
		color: white;
		padding: 25px;
		border-radius: 12px;
		text-align: center;
		box-shadow: 0 4px 12px rgba(44, 85, 48, 0.3);
	}

	.stat-card h3 {
		margin: 0 0 10px 0;
		font-size: 1rem;
		opacity: 0.9;
	}

	.stat-value {
		font-size: 2rem;
		font-weight: bold;
		margin: 0;
	}

	.info {
		background: #f8f9fa;
		padding: 25px;
		border-radius: 12px;
		border-left: 4px solid #2c5530;
	}

	.info h3 {
		margin: 0 0 15px 0;
		color: #2c5530;
	}

	.info ul {
		margin: 0;
		padding-left: 20px;
	}

	.info li {
		margin-bottom: 8px;
		color: #555;
		line-height: 1.5;
	}

	@media (max-width: 768px) {
		.container {
			padding: 15px;
		}

		h1 {
			font-size: 2rem;
		}

		.controls {
			flex-direction: column;
			align-items: center;
		}

		.chart-section {
			padding: 20px;
		}
	}
</style>
