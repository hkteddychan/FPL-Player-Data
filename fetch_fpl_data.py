#!/usr/bin/env python3
"""Fetch FPL player data and generate analysis report."""
import urllib.request
import json
from datetime import datetime

PLAYERS_JSON_URL = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2024-25/players_raw.json"
OUTPUT_FILE = "fpl_player_report.json"

def fetch_fpl_players():
    req = urllib.request.Request(PLAYERS_JSON_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode('utf-8'))

def analyze_players(players):
    """Extract key stats for each player."""
    player_list = []
    
    for key, p in players.items():
        try:
            player_list.append({
                "id": p.get("id"),
                "name": p.get("second_name", ""),
                "full_name": p.get("first_name", "") + " " + p.get("second_name", ""),
                "team": p.get("team"),
                "position": p.get("element_type"),
                "price": p.get("now_cost", 0) / 10,
                "total_points": p.get("total_points", 0),
                "form": float(p.get("form", 0)),
                "goals": p.get("goals_scored", 0),
                "assists": p.get("assists", 0),
                "bonus": p.get("bonus", 0),
                "bps": p.get("bps", 0),
                "selected_by": p.get("selected_by_percent", 0),
                "xG": p.get("expected_goals", 0),
                "xA": p.get("expected_assists", 0),
                "minutes": p.get("minutes", 0),
                "ict": p.get("ict_index", "0"),
                "chance_of_playing": p.get("chance_of_playing_next_round", 100),
            })
        except Exception:
            continue
    
    # Sort by total points
    player_list.sort(key=lambda x: x["total_points"], reverse=True)
    
    # Top players by position
    goalkeepers = [p for p in player_list if p["position"] == 1][:5]
    defenders = [p for p in player_list if p["position"] == 2][:10]
    midfielders = [p for p in player_list if p["position"] == 3][:10]
    forwards = [p for p in player_list if p["position"] == 4][:10]
    
    return {
        "updated": datetime.utcnow().isoformat(),
        "total_players": len(player_list),
        "top_players": player_list[:50],
        "top_goalkeepers": goalkeepers,
        "top_defenders": defenders,
        "top_midfielders": midfielders,
        "top_forwards": forwards,
        "best_value": sorted(player_list, key=lambda x: x["total_points"]/x["price"] if x["price"] > 0 else 0, reverse=True)[:10],
        "most_selected": sorted(player_list, key=lambda x: float(x["selected_by"]), reverse=True)[:10],
    }

def main():
    print(f"[{datetime.now().isoformat()}] Fetching FPL player data...")
    players = fetch_fpl_players()
    print(f"Fetched {len(players)} players")
    
    report = analyze_players(players)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Generated {OUTPUT_FILE} with {report['total_players']} players")

if __name__ == "__main__":
    main()
