import asyncio
import httpx
from utils.dates import epoch_to_iso

async def get_bodog():
    bet_type_dict = {
        "Moneyline":"moneyline",
        "Runline":"spread",
        "Spread":"spread",
        "Puckline":"spread",
        "Goal Spread":"spread",
        "Draw No Bet":"moneyline",
        "Total":"total",
        "Total Runs O/U":"total",
        "Total Goals O/U":"total",
    }
    period_dict = {
        'G':0,
        'RT':0,
        # '1H':1,
    }
    lines = []
    responses = await get_data()

    for data, sport, league_name in responses: 
        if not data:
            continue
        events = data[0]['events']

        for event in events:
            market_values = {}
            matchup = event['description']
            reverse, cleaned_matchup = clean_matchup(matchup)
            market_values['reverse'] = reverse
            market_values['matchup'] = cleaned_matchup
            market_values['date'] = epoch_to_iso(event['startTime'] / 1000)
            market_values['sport'] = sport
            market_values['league'] = league_name
            parsed_markets = parse_markets(event, bet_type_dict, period_dict)
            for line in parse_lines(parsed_markets, market_values, bet_type_dict, period_dict):
                lines.append(line)
    return lines


async def get_data():
    leagues = (
        ('hockey/nhl', 'Hockey', 'NHL'), 
        ('basketball/nba', 'Basketball', 'NBA'), 
        ('baseball/mlb', 'Baseball', 'MLB'), 
        ('soccer/north-america/united-states/mls', 'Soccer', 'MLS'),
        ('basketball/wnba', 'Basketball', 'WNBA'),
        ('football/nfl', 'Football', 'NFL'),
        # 'football/college-football',
        # 'baseball/japan/professional-baseball',
        # 'soccer/fifa-womens-world-cup/women-s-world-cup-matches',
    )
    async with httpx.AsyncClient() as client: 
        tasks = []
        for league, sport, league_name in leagues:
            url = f"https://www.bodog.eu/services/sports/event/coupon/events/A/description/{league}"
            tasks.append(asyncio.ensure_future(make_request(client, url, sport, league_name)))
        responses = await asyncio.gather(*tasks) 
    return responses


async def make_request(client, url, sport, league_name):
    headers = {
        "cookie": "TS014505a4=014b5d5d074621dcb805603f6ecd400ce1005af41531ed96e612911b0ac1d43907fae8b6e0d8487c332e76c9c3ce7978a0e89cfbdf",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
    }
    query = {"preMatchOnly":"true"}
    resp = await client.get(url, headers=headers, params=query, timeout=15)
    return (resp.json(), sport, league_name)


def clean_matchup(matchup):
    reverse = False
    if 'vs' in matchup:
        no_w = matchup.replace(' (W)', '')
        home_team, away_team = no_w.split( 'vs' )
        matchup = f'{away_team} @ {home_team}'
        reverse = True 
    return reverse, matchup


def parse_markets(event, bet_type_dict, period_dict):
    parsed_markets = []
    groups = event['displayGroups']
    for group in groups:
        for market in group['markets']:
            if (market['description'] in bet_type_dict 
                and market['status'] == 'O'
                and (market['period']['abbreviation'] in period_dict)):
                parsed_markets.append(market)
    return parsed_markets


def parse_lines(parsed_markets, market_values, bet_type_dict, period_dict):
    sportsbook = "Bodog"
    reversed, matchup, date, sport, league =  market_values.values()
    for market in parsed_markets:
        bet_type = bet_type_dict[market['description']]
        period = period_dict[market['period']['abbreviation']]
        outcomes = market['outcomes']
        if (len(outcomes) % 2) != 0:  # Only two outcome markets
            outcomes.pop(0)
        for i in range(len(outcomes)):
            if i % 2 != 0:
                continue 
            away, home = outcomes[i], outcomes[i+1]
            away, home = away['price'], home['price'] 
            home_odds, away_odds = clean_totals(bet_type, home, away, reversed)
            spov, spun = clean_spreads(bet_type, home, away, reversed)

            #yield ({
            #    'matchup':matchup, 'bet_type':bet_type, 'period':period, 
            #    'date':date, 'spov':spov, 'spun':spun, 'sportsbook':sportsbook, 
            #    'home_odds':home_odds, 'away_odds':away_odds
            #})
            yield ((
                sport, league, matchup, bet_type, period, date, spov, spun, sportsbook, 
                home_odds, away_odds
            ))


def clean_totals(bet_type, home, away, reversed):
    home_odds, away_odds = home['decimal'], away['decimal']    
    if bet_type == 'total' or (bet_type == 'spread' and reversed):
        away_odds, home_odds = float(home['decimal']), float(away['decimal'])
    return home_odds, away_odds


def clean_spreads(bet_type, home, away, reversed):
    if bet_type != 'moneyline':
        if bet_type == 'spread' and reversed:
            home, away, = away, home

        if 'handicap2' in home:
            spov = str((float(home['handicap']) + float(home['handicap2'])) / 2)
            spun = str((float(away['handicap']) + float(away['handicap2'])) / 2)
        else:
            spov, spun = home['handicap'], away['handicap']
    else:
        spov = spun = ''
    
    if bet_type == 'spread':
        if spov[0] == '-':
            spun = f'+{spun}'
        elif spun[0] == '-':
            spov = f'+{spov}'
    return spov, spun

