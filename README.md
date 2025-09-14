# Tennis ATP Ranking Visualization

A progressive tennis ATP ranking visualization project built with Svelte, D3.js, FastAPI, and SQLite.

## Project Structure

- `backend/` - FastAPI backend with SQLite database
- `frontend-latest/` - Current visualization (Svelte + D3.js)
- `frontend-evolution/` - Evolution blog site showing project history

## Getting Started

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Latest
```bash
cd frontend-latest
npm install
npm run dev
```

### Frontend Evolution
```bash
cd frontend-evolution
npm install
npm run dev
```

## Features

- Interactive line chart showing ATP top 10 rankings over time
- Player comparison and historical analysis
- Evolution blog showcasing development progression

## Tech Stack

- **Frontend**: Svelte, D3.js
- **Backend**: FastAPI, SQLite
- **Data**: ATP ranking data (dummy → real)