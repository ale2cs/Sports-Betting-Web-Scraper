import requests
from requests.adapters import HTTPAdapter, Retry
import jmespath
from sportbooks.utils import american_to_decimal

def get_pinacle():
    markets = []
    sportsbook = "Pinnacle"
    bet_type_dict = {"moneyline":0, "total":1, "spread":2} 
    bet_type_keys = [f'`{key}`' for key in bet_type_dict]
    bet_type_query = f"[{', '.join(bet_type_keys)}]"

    games, values = make_requests()

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
                if len(data['prices']) != 2:  # only two outcomes
                    continue
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

def make_requests():
    sport_codes = [
        1456,  # NHL
        487,  # NBA
        246,  # MLB
        2663,  # MLS
        187703,  # NPB
    ]
    header = {
        "X-API-Key": "CmX2KcMrXuFmNg6YFbmTxE0y9CIrOi0R",
    }
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504, 429])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    games = []
    values = []
    for code in sport_codes:
        games_url = (f"https://guest.api.arcadia.pinnacle.com/0.1/leagues/{code}/matchups")
        values_url = f"https://guest.api.arcadia.pinnacle.com/0.1/leagues/{code}/markets/straight"
        game_data = session.get(games_url, headers=header)
        games.append(game_data.json())
        value_data = session.get(values_url, headers=header)
        values.append(value_data.json())
    session.close()
    return games, values

def parse_games(sport):
    # parses desired betting markets
    des_bets_exp = "[?periods[0].period == `0` && parent != None && periods[0].cutoffAt != None][parentId, parent.participants, periods[0]]"
    bets = jmespath.search(des_bets_exp, sport)
    if not bets:
        alt_exp = "[?periods[0].period == `0` && periods[0].cutoffAt != None][id, participants, periods[0]]"
        bets = jmespath.search(alt_exp, sport)
    return remove_duplicate_games(bets)

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