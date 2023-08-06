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
    lines = []
    responses = await get_data()

    for data in responses: 
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
            parsed_markets = parse_markets(event, bet_type_dict)
            for line in parse_lines(parsed_markets, market_values, bet_type_dict):
                lines.append(line)
    return lines


async def get_data():
    leagues = (
        'hockey/nhl', 
        'basketball/nba', 
        'baseball/mlb', 
        'soccer/north-america/united-states/mls',
        'baseball/japan/professional-baseball',
        'basketball/wnba',
        'soccer/fifa-womens-world-cup/women-s-world-cup-matches',
    )
    async with httpx.AsyncClient() as client: 
        tasks = []
        for league in leagues:
            url = f"https://www.bodog.eu/services/sports/event/coupon/events/A/description/{league}"
            tasks.append(asyncio.ensure_future(make_request(client, url)))
        responses = await asyncio.gather(*tasks) 
    return responses


def clean_matchup(matchup):
    reverse = False
    if 'vs' in matchup:
        no_w = matchup.replace(' (W)', '')
        home_team, away_team = no_w.split( 'vs' )
        matchup = f'{away_team} @ {home_team}'
        reverse = True 
    return reverse, matchup


async def make_request(client, url):
    headers = {
        "cookie": "TS014505a4=014b5d5d074621dcb805603f6ecd400ce1005af41531ed96e612911b0ac1d43907fae8b6e0d8487c332e76c9c3ce7978a0e89cfbdf",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
    }
    query = {"preMatchOnly":"true"}
    resp = await client.get(url, headers=headers, params=query, timeout=15)
    return resp.json()


def parse_markets(event, bet_type_dict):
    parsed_markets = []
    groups = event['displayGroups']
    for group in groups:
        for market in group['markets']:
            description = market['period']['description']
            if (market['description'] in bet_type_dict 
                and market['status'] == 'O'
                and (description == 'Game' or description == 'Regulation Time')):
                parsed_markets.append(market)
    return parsed_markets


def parse_lines(parsed_markets, market_values, bet_type_dict):
    sportsbook = "Bodog"
    period = 0
    reversed, matchup, date =  market_values.values()
    for market in parsed_markets:
        bet_type = bet_type_dict[market['description']]
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

            yield ({
                'matchup':matchup, 'bet_type':bet_type, 'period':period, 
                'date':date, 'spov':spov, 'spun':spun, 'sportsbook':sportsbook, 
                'home_odds':home_odds, 'away_odds':away_odds
            })


def clean_totals(bet_type, home, away, reversed):
    home_odds, away_odds = home['decimal'], away['decimal']    
    if bet_type == 'total' or (bet_type == 'spread' and reversed):
        away_odds, home_odds = home['decimal'], away['decimal']
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

