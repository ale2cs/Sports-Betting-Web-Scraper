import asyncio
import httpx
import jmespath
from sportbooks.utils import american_to_decimal

async def get_pinacle():
    markets = []
    lines = []
    games, values = await get_data()
    sportsbook = "Pinnacle"
    bet_type_dict = {"moneyline":0, "total":1, "spread":2} 
    bet_type_keys = [f'`{key}`' for key in bet_type_dict]
    bet_type_query = f"[{', '.join(bet_type_keys)}]"

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
                home_odds = american_to_decimal(home['price']) 
                away_odds = american_to_decimal(away['price'])
                if ('points' in home):
                    spov, spun = str(home['points']), str(away['points'])
                    if (spov[0] == '-'):
                        spun = f"+{spun}"
                    elif (spun[0] == '-'):
                        spov = f"+{spov}"
                else:
                    spov = spun = ''
                markets.append((
                    matchup, bet_type, period, date, home_team, away_team, 
                    spov, spun
                ))
                lines.append((
                    matchup, bet_type, period, date, spov, spun, sportsbook, 
                    home_odds, away_odds
                ))

    return markets, lines

async def get_data():
    sport_codes = [
        1456,  # NHL
        487,  # NBA
        246,  # MLB
        #2663,  # MLS
        #187703,  # NPB
    ] 
    async with httpx.AsyncClient() as client: 
        game_tasks = []
        value_tasks =[]
        for code in sport_codes:
            games_url = (f"https://guest.api.arcadia.pinnacle.com/0.1/leagues/{code}/matchups")
            values_url = f"https://guest.api.arcadia.pinnacle.com/0.1/leagues/{code}/markets/straight"
            game_tasks.append(asyncio.ensure_future(make_request(client, games_url)))
            value_tasks.append(asyncio.ensure_future(make_request(client, values_url)))
        games = await asyncio.gather(*game_tasks)    
        values = await asyncio.gather(*value_tasks)    
    return games, values

async def make_request(client, url):
    header = {
            "X-API-Key": "CmX2KcMrXuFmNg6YFbmTxE0y9CIrOi0R",
    }
    resp = await client.get(url, headers=header, timeout=10)
    return resp.json()

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