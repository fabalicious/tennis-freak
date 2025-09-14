import sqlite3
from datetime import datetime, timedelta
import random
from typing import List, Optional

DATABASE_PATH = "tennis_rankings.db"

def get_connection():
    return sqlite3.connect(DATABASE_PATH)

def init_db():
    """Initialize the database with tables and dummy data"""
    conn = get_connection()
    cursor = conn.cursor()

    # Create players table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            country TEXT NOT NULL
        )
    ''')

    # Create rankings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rankings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            player_id INTEGER NOT NULL,
            ranking INTEGER NOT NULL,
            points INTEGER NOT NULL,
            FOREIGN KEY (player_id) REFERENCES players (id)
        )
    ''')

    # Create indexes for better query performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_rankings_date ON rankings(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_rankings_player_date ON rankings(player_id, date)')

    conn.commit()

    # Check if we already have data
    cursor.execute('SELECT COUNT(*) FROM players')
    if cursor.fetchone()[0] == 0:
        populate_dummy_data(conn)

    conn.close()

def populate_dummy_data(conn):
    """Populate database with realistic dummy ATP ranking data"""
    cursor = conn.cursor()

    # Top tennis players with realistic data
    players = [
        ("Novak Djokovic", "SRB"),
        ("Carlos Alcaraz", "ESP"),
        ("Daniil Medvedev", "RUS"),
        ("Jannik Sinner", "ITA"),
        ("Andrey Rublev", "RUS"),
        ("Stefanos Tsitsipas", "GRE"),
        ("Alexander Zverev", "GER"),
        ("Holger Rune", "DEN"),
        ("Taylor Fritz", "USA"),
        ("Casper Ruud", "NOR"),
        ("Hubert Hurkacz", "POL"),
        ("Alex de Minaur", "AUS"),
        ("Tommy Paul", "USA"),
        ("Cameron Norrie", "GBR"),
        ("Lorenzo Musetti", "ITA")
    ]

    # Insert players
    cursor.executemany('INSERT INTO players (name, country) VALUES (?, ?)', players)

    # Generate weekly rankings for the last year
    start_date = datetime.now() - timedelta(days=365)
    current_date = start_date

    # Initial points distribution (roughly realistic)
    initial_points = [9800, 8400, 7600, 6900, 5800, 5400, 4800, 4200, 3800, 3400, 3000, 2800, 2600, 2400, 2200]

    while current_date <= datetime.now():
        date_str = current_date.strftime('%Y-%m-%d')

        # Simulate ranking changes over time
        for i, (player_name, country) in enumerate(players):
            player_id = i + 1
            base_ranking = i + 1
            base_points = initial_points[i] if i < len(initial_points) else 2000

            # Add some realistic fluctuation
            ranking_variance = random.randint(-2, 2) if i < 10 else random.randint(-5, 5)
            points_variance = random.randint(-200, 200) if i < 5 else random.randint(-400, 400)

            current_ranking = max(1, min(base_ranking + ranking_variance, 15))
            current_points = max(0, base_points + points_variance +
                               random.randint(-100, 100))  # Weekly fluctuation

            cursor.execute('''
                INSERT INTO rankings (date, player_id, ranking, points)
                VALUES (?, ?, ?, ?)
            ''', (date_str, player_id, current_ranking, current_points))

        current_date += timedelta(weeks=1)

    conn.commit()

def get_players():
    """Get all players"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, country FROM players')
    players = [{"id": row[0], "name": row[1], "country": row[2]} for row in cursor.fetchall()]
    conn.close()
    return players

def get_rankings(date: str, limit: int = 10, end_date: Optional[str] = None):
    """Get rankings for a specific date or date range"""
    conn = get_connection()
    cursor = conn.cursor()

    if end_date:
        # Date range query
        query = '''
            SELECT r.date, r.player_id, p.name, r.ranking, r.points, p.country
            FROM rankings r
            JOIN players p ON r.player_id = p.id
            WHERE r.date >= ? AND r.date <= ?
            ORDER BY r.date, r.ranking
            LIMIT ?
        '''
        cursor.execute(query, (date, end_date, limit * 100))  # Allow more results for date ranges
    else:
        # Single date query
        query = '''
            SELECT r.date, r.player_id, p.name, r.ranking, r.points, p.country
            FROM rankings r
            JOIN players p ON r.player_id = p.id
            WHERE r.date = ?
            ORDER BY r.ranking
            LIMIT ?
        '''
        cursor.execute(query, (date, limit))

    rankings = []
    for row in cursor.fetchall():
        rankings.append({
            "date": row[0],
            "player_id": row[1],
            "player_name": row[2],
            "ranking": row[3],
            "points": row[4],
            "country": row[5]
        })

    conn.close()
    return rankings

def get_player_history(player_id: int):
    """Get ranking history for a specific player"""
    conn = get_connection()
    cursor = conn.cursor()

    query = '''
        SELECT r.date, r.player_id, p.name, r.ranking, r.points, p.country
        FROM rankings r
        JOIN players p ON r.player_id = p.id
        WHERE r.player_id = ?
        ORDER BY r.date
    '''
    cursor.execute(query, (player_id,))

    history = []
    for row in cursor.fetchall():
        history.append({
            "date": row[0],
            "player_id": row[1],
            "player_name": row[2],
            "ranking": row[3],
            "points": row[4],
            "country": row[5]
        })

    conn.close()
    return history