import requests
import jmespath
from sportbooks.utils import american_to_decimal

def get_pinacle():
    sport_codes = [
        1456,  # nhl
        487,  # nba
        246,  # mlb
    ]
    header = {
        "X-API-Key": "CmX2KcMrXuFmNg6YFbmTxE0y9CIrOi0R",
    }
    games = []
    values = []
    markets = []
    sportsbook = "Pinnacle"
    bet_type_dict = {"moneyline":0, "total":1, "spread":2} 
    bet_type_keys = [f'`{key}`' for key in bet_type_dict]
    bet_type_query = f"[{', '.join(bet_type_keys)}]"
    for code in sport_codes:
        games_url = (f"https://guest.api.arcadia.pinnacle.com/0.1/leagues/{code}/matchups")
        values_url = f"https://guest.api.arcadia.pinnacle.com/0.1/leagues/{code}/markets/straight"
        game_data = requests.request("GET", games_url, headers=header)
        games.append(game_data.json())
        value_data = requests.request("GET", values_url, headers=header)
        values.append(value_data.json())

    for sport, prices in zip(games, values):
        for game_id, teams, time in parse_games(sport):
            home_team, away_team = teams[0]['name'], teams[1]['name']
            matchup = f"{away_team} @ {home_team}"
            date = time['cutoffAt']
            period = time['period']
            matching_id_exp = f"[?matchupId == `{game_id}` && period == `0` && contains({bet_type_query}, type)]"
            market_data = jmespath.search(matching_id_exp, prices)
            for data in market_data:
                bet_type = data['type']
                home, away = data['prices'][0], data['prices'][1]
                home_payout = american_to_decimal(home['price']) 
                away_payout = american_to_decimal(away['price'])
                if ('points' in home):
                    spov, spun = str(home['points']), str(away['points'])
                    if (spov[0] == '-'):
                        spun = f"+{spun}"
                    elif (spun[0] == '-'):
                        spov = f"+{spov}"
                else:
                    spov = spun = ''
                market_id = create_market_id(game_id, bet_type, bet_type_dict, 
                    period, spov)
                markets.append((market_id, sportsbook, matchup, bet_type, period, 
                    date, home_team, away_team, home_payout, away_payout, spov, 
                    spun
                ))
    return markets


def parse_games(sport):
    # parses desired betting markets
    des_bets_exp = "[?periods[0].period == `0` && parent != None && periods[0].cutoffAt != None][parentId, parent.participants, periods[0]]"
    return remove_duplicate_games(jmespath.search(des_bets_exp, sport))

def remove_duplicate_games(games):
    unique_ids = []
    unique_games = []
    for item in games:
        game_id = item[0]
        if game_id not in unique_ids:
            unique_ids.append(game_id)
            unique_games.append(item)
    return unique_games

def create_market_id(game_id, bet_type, bet_type_dict, period, spov):
    market_id = (game_id * 1000000) + 1000
    market_id += bet_type_dict[bet_type] * 100000
    market_id += period * 10000

    if bet_type in ['spread', 'total']:
        market_id += int(2 * float(spov))

    return market_id