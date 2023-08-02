import asyncio
import httpx
from utils.calcs import american_to_decimal
from utils.helpers import flatten

async def get_pinacle():
    markets = []
    lines = []
    bet_type_dict = {'moneyline':0, 'total':1, 'spread':2}  # Desired markets
    games, values = await get_data()

    for sport, prices in zip(games, values):
        for game_id, league, teams, time in parse_games(sport):
            market_values = {} 
            home_team, away_team = teams[0]['name'], teams[1]['name']
            market_values['league'] = league['name']
            market_values['sport'] = league['sport']['name']
            market_values['home_team'] = home_team
            market_values['away_team'] = away_team
            market_values['matchup'] = f"{away_team} @ {home_team}"
            market_values['date'] = time['cutoffAt']
            market_values['period'] = time['period']
            market_data = parse_markets(prices, game_id, bet_type_dict)
            parsed_markets, parsed_lines = parse_market_data(market_data, market_values)
            markets.append(parsed_markets)
            lines.append(parsed_lines)
    return flatten(markets), flatten(lines)


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
    bets = []
    for line in sport:
        periods = line['periods'][0]
        if (periods['period'] == 0 and
            line['parent'] != None and
            periods['cutoffAt'] != None):
                bets.append([line['parentId'], line['league'], line['parent']['participants'], periods]) 
    # Loop may not be necessary
    if not bets:
        for line in sport:
            periods = line['periods'][0]
            if (periods['period'] == 0 and
                periods['cutoffAt'] != None and
                line['participants'][0]['alignment'] != 'neutral'):
                bets.append([line['id'], line['league'], line['participants'], periods])
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


def parse_markets(prices, game_id, bet_type_dict):
    markets = []
    for price in prices:
        if (price['matchupId'] == game_id and 
            price['period'] == 0 and  # Only full game markets
            price['type'] in bet_type_dict):
            markets.append(price)
    return markets 


def parse_market_data(market_data, market_values):
    markets = []
    lines = []
    sportsbook = 'Pinnacle'
    league, sport, home_team, away_team, matchup, date, period = market_values.values()
    for data in market_data:
        bet_type = data['type']
        if len(data['prices']) != 2:  # Only markets with two outcomes
            continue
        home, away = data['prices'][0], data['prices'][1]
        home_odds = american_to_decimal(home['price']) 
        away_odds = american_to_decimal(away['price'])
        if ('points' in home):
            spov, spun = str(home['points']), str(away['points'])
            if (spov[0] == '-'):
                spun = f'+{spun}'
            elif (spun[0] == '-'):
                spov = f'+{spov}'
        else:
            spov = spun = ''
        markets.append((
            sport, league, matchup, bet_type, period, date, home_team, 
            away_team, spov, spun
        ))
        lines.append({
            'matchup':matchup, 'bet_type':bet_type, 'period':period, 
            'date':date, 'spov':spov, 'spun':spun, 'sportsbook':sportsbook, 
            'home_odds':home_odds, 'away_odds':away_odds
        })
    return markets, lines