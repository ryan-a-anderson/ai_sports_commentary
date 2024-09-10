from flask import Flask, render_template, jsonify
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__)

API_KEY = os.environ.get('API_SPORTS_KEY')
API_HOST = 'v1.baseball.api-sports.io'

def get_fixtures():
    url = "https://v1.baseball.api-sports.io/games"
    today = datetime.now().strftime("%Y-%m-%d")
    next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    params = {
        'league': 1,  # MLB
        'season': 2024,
        'date': today,
    }
    headers = {
        'x-rapidapi-host': API_HOST,
        'x-rapidapi-key': API_KEY
    }
    response = requests.get(url, headers=headers, params=params)
    print(f"API Response Status: {response.status_code}")  # Debug print
    if response.status_code == 200:
        games = response.json().get('response', [])
        print(f"Number of games: {len(games)}")  # Debug print
        return games
    print(f"API Error: {response.text}")  # Debug print for non-200 responses
    return []

def fetch_game_data():
    games = get_fixtures()
    print(f"Fetched games: {games}")  # Debug print
    if not games:
        return {"error": "No games found"}
    return {'games': games}

def generate_commentary(data):
    if 'error' in data:
        return data['error']
    
    games = data['games']
    commentary = []
    
    for game in games:
        home_team = game['teams']['home']['name']
        away_team = game['teams']['away']['name']
        start_time = datetime.fromisoformat(game['date'].replace('Z', '+00:00'))
        
        if game['status']['short'] == 'LIVE':
            commentary.append(f"LIVE: {away_team} vs {home_team}. Score: {game['scores']['away']['total']} - {game['scores']['home']['total']}")
        elif game['status']['short'] == 'FT':
            commentary.append(f"Final: {away_team} vs {home_team}. Score: {game['scores']['away']['total']} - {game['scores']['home']['total']}")
        else:
            time_until_start = start_time - datetime.now(start_time.tzinfo)
            days, seconds = time_until_start.days, time_until_start.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            
            commentary.append("Upcoming: {} vs {}. Game starts in {} days, {} hours, and {} minutes.".format(
                away_team, home_team, days, hours, minutes
            ))
    
    return "\n\n".join(commentary)  # Join with double newline for better separation

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/update_commentary')
def update_commentary():
    game_data = fetch_game_data()
    print(f"Game data: {game_data}")  # Debug print
    commentary = generate_commentary(game_data)
    print("Number of games commented:", commentary.count('\n') + 1)
    return jsonify({"commentary": commentary})

if __name__ == '__main__':
    app.run(debug=True)
