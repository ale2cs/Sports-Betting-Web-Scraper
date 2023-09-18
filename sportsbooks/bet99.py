import asyncio
import httpx
from utils.helpers import add_dec

async def get_bet99():
    bet_type_dict = {
        'Money Line': 'moneyline', 
        'Total':'total', 'Spread':'spread', 
        'Money Line (AL)':'moneyline', 
        'Total (AL)':'total', 
        'Spread (AL)':'spread',
    }
    lines = [] 
    responses = await get_data()

    for resp in responses:
        if not resp['Result']['Items']:
            continue
        data = resp['Result']['Items'][0]
        game_bets = parse_markets(data, bet_type_dict) 
        events = data['Events']

        for bets, event in zip(game_bets, events):
            values = {}
            values['date'] = event['EventDate']
            values['matchup'] = parse_matchup(event)
            for formatted_lines in format_lines(bets, values, bet_type_dict):
                lines.append(formatted_lines)
    return lines


async def get_data():
    url = "https://sb2frontend-altenar2.biahosted.com/api/Sportsbook/GetEvents" 
    gen_query = {
        "langId":"8",
        "configId":"12",
        "integration":"bet99",
        "group":"AllEvents"
    }
    sport_queries = [
        {"sportids":"70", "champids":"3232"},  # NHL
        {"sportids":"67", "champids":"2980"},  # NBA
        {"sportids":"76", "champids":"3286"},  # MLB
        {"sportsid":"66", "champids":"4610"},  # MLS
        {"sportids":"67", "champids":"5519"},  # WNBA
        {"sportids":"75", "champids":"3281"},  # NFL
        {"sportids":"75", "champids":"3284"},  # NCAAF
        # {"sportids":"76", "champids":"4457"},  # NPB
    ]
    async with httpx.AsyncClient() as client:
        tasks = []
        for query in sport_queries:
            full_query = gen_query.copy()
            full_query |= query
            tasks.append(asyncio.ensure_future(make_request(client, url, full_query)))
        responses = await asyncio.gather(*tasks)
    return responses


async def make_request(client, url, query):
    resp = await client.get(url, params=query, timeout=10)
    return resp.json()
    

def parse_markets(data, bet_type_dict):
    markets = []
    events = data['Events']
    for event in events:
        items = []
        for item in event['Items']:
            if item['Name'] in bet_type_dict and item['Status'] != 2:  # No locked market
                items.append(item)
        markets.append(items)
    return markets


def parse_matchup(event):
    team_dict = {
        # NHL
        'ANA':'Anaheim', 'ARI':'Arizona', 'BOS':'Boston', 
        'BUF':'Buffalo', 'CAR':'Carolina', 'CBJ':'Columbus', 
        'CGY':'Calgary', 'CHI':'Chicago', 'COL':'Colorado', 
        'DAL':'Dallas', 'DET':'Detroit', 'EDM':'Edmonton', 
        'FLA':'Florida', 'LA':'Los Angeles', 'MIN':'Minnesota', 
        'MTL':'Montreal', 'NJ':'New Jersey', 'NSH':'Nashville', 
        'NYI':'New York', 'NYR':'New York', 'OTT':'Ottawa', 
        'PIT':'Pittsburgh', 'SEA':'Seattle', 'SJ':'San Jose', 
        'STL':'St. Louis', 'TB':'Tampa Bay', 'TOR':'Toronto', 
        'VAN':'Vancouver', 'VGK':'Vegas', 'WSH':'Washington', 
        'WPG':'Winnipeg',
            
        # NBA
        'ATL':'Atlanta', 'BKN':'Brooklyn', 'CHA':'Charlotte', 
        'CLE':'Cleveland', 'DEN':'Denver', 'GS':'Golden State', 
        'HOU':'Houston', 'IND':'Indiana', 'LAC':'Los Angeles', 
        'LAL':'Los Angeles', 'MEM':'Memphis', 'MIA':'Miami', 
        'MIL':'Milwaukee', 'NOP':'New Orleans', 'NY':'New York', 
        'OKC':'Oklahoma City','ORL': 'Orlando', 'PHI':'Philadelphia', 
        'PHX':'Phoenix', 'POR':'Portland', 'SAC':'Sacramento', 
        'SAS':'San Antonio', 'UTA':'Utah',
        
        # MLB
        'BAL':'Baltimore', 'CIN':"Cincinnati", 'KC':'Kansas',
        'OAK':'Oakland', 'SD':'San Diego', 'SF':'San Francisco',
        'TEX':'Texas', 'WAS':'Washington',

        # NFL
    }
    matchup = event['Name']
    home_team, away_team = matchup.split(' vs. ')
    home_abbr = home_team.split(' ')[0] 
    away_abbr = away_team.split(' ')[0] 
    if home_abbr in team_dict:
        home_team = home_team.replace(home_abbr, team_dict[home_abbr])
    if away_abbr in team_dict:
        away_team = away_team.replace(away_abbr, team_dict[away_abbr])
    return f'{away_team} @ {home_team}'


def format_lines(bets, values, bet_type_dict):
    date, matchup = values.values()
    sportsbook = 'Bet99'
    period = 0  
    for bet in bets:
        bet_type = bet_type_dict[bet['Name']]
        home, away = bet['Items'][0], bet['Items'][1] 
        home_odds, away_odds = home['Price'], away['Price']
        if bet_type == 'moneyline':
            spov = spun = ''
        else:
            spov, spun = home['SPOV'], away['SPOV']
        if bet_type == "spread":
            if spov[0] == '-':
                spun = f"+{add_dec(spun[1:])}"
            else:
                spun = f"-{add_dec(spun[1:])}" 
            spov = f"{spov[0]}{add_dec(spov[1:])}"
        else:
            spov, spun = add_dec(spov), add_dec(spun)
        #yield ({
        #    'matchup':matchup, 'bet_type':bet_type, 'period':period, 
        #    'date':date, 'spov':spov, 'spun':spun, 'sportsbook':sportsbook, 
        #    'home_odds':home_odds, 'away_odds':away_odds
        #})
        yield ((
            matchup, bet_type, period, date, spov, spun, sportsbook, 
            home_odds, away_odds
        ))