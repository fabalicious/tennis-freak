export interface Player {
	id: number;
	name: string;
	country: string;
}

export interface Ranking {
	date: string;
	player_id: number;
	player_name: string;
	ranking: number;
	points: number;
	country: string;
}

const API_BASE = 'http://localhost:8000';

class TennisAPI {
	async getPlayers(): Promise<Player[]> {
		const response = await fetch(`${API_BASE}/players`);
		if (!response.ok) {
			throw new Error(`Failed to fetch players: ${response.statusText}`);
		}
		return response.json();
	}

	async getRankings(date: string, limit: number = 10): Promise<Ranking[]> {
		const response = await fetch(`${API_BASE}/rankings/${date}?limit=${limit}`);
		if (!response.ok) {
			throw new Error(`Failed to fetch rankings: ${response.statusText}`);
		}
		return response.json();
	}

	async getRankingsRange(startDate: string, endDate: string, limit: number = 10): Promise<Ranking[]> {
		const response = await fetch(`${API_BASE}/rankings/range/${startDate}/${endDate}?limit=${limit}`);
		if (!response.ok) {
			throw new Error(`Failed to fetch ranking range: ${response.statusText}`);
		}
		return response.json();
	}

	async getPlayerHistory(playerId: number): Promise<Ranking[]> {
		const response = await fetch(`${API_BASE}/players/${playerId}/history`);
		if (!response.ok) {
			throw new Error(`Failed to fetch player history: ${response.statusText}`);
		}
		return response.json();
	}
}

export const api = new TennisAPI();