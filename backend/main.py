from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import date, datetime
import sqlite3
from pydantic import BaseModel
from database import init_db, get_rankings, get_player_history, get_players

app = FastAPI(title="Tennis ATP Rankings API", version="1.0.0")

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Svelte dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Player(BaseModel):
    id: int
    name: str
    country: str

class Ranking(BaseModel):
    date: str
    player_id: int
    player_name: str
    ranking: int
    points: int
    country: str

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/")
async def root():
    return {"message": "Tennis ATP Rankings API"}

@app.get("/players", response_model=List[Player])
async def get_all_players():
    return get_players()

@app.get("/rankings/{ranking_date}", response_model=List[Ranking])
async def get_rankings_by_date(ranking_date: str, limit: Optional[int] = 10):
    try:
        rankings = get_rankings(ranking_date, limit)
        if not rankings:
            raise HTTPException(status_code=404, detail="No rankings found for this date")
        return rankings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rankings/range/{start_date}/{end_date}", response_model=List[Ranking])
async def get_rankings_range(start_date: str, end_date: str, limit: Optional[int] = 10):
    try:
        rankings = get_rankings(start_date, limit, end_date)
        return rankings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/players/{player_id}/history", response_model=List[Ranking])
async def get_player_ranking_history(player_id: int):
    try:
        history = get_player_history(player_id)
        if not history:
            raise HTTPException(status_code=404, detail="No history found for this player")
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)