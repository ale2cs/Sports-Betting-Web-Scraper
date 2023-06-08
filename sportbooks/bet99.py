import asyncio
import httpx
import jmespath

async def get_bet99():
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
        "BAL":"Baltimore", "CIN":"Cincinnati", "KC":"Kansas",
        "OAK":"Oakland", "SD":"San Diego", "SF":"San Francisco",
        "TEX":"Texas", "WAS":"Washington",
    }
    bet_type_dict = {
        "Money Line": "moneyline", 
        "Total":"total", "Spread":"spread", 
        "Money Line (AL)":"moneyline", 
        "Total (AL)":"total", 
        "Spread (AL)":"spread",
    }
    markets = []
    sportsbook = "Bet99"
    period = 0  
 
    # expressions
    bet_type_keys = [f"'{key}'" for key in bet_type_dict]
    bet_type_query = f"[{', '.join(bet_type_keys)}]"
    des_bets_exp = f"Events[*].Items[?contains({bet_type_query}, Name)]"
    events_exp = "Events[*]"
    
    responses = await get_data()
    for resp in responses:
        if not resp['Result']['Items']:
            continue
        data = resp['Result']['Items'][0]
        # searches
        game_bets = jmespath.search(des_bets_exp, data) 
        events = jmespath.search(events_exp, data)

        for bets, event in zip(game_bets, events):
            matchup = event['Name']
            date = event['EventDate']
            home_team, away_team = matchup.split(' vs. ')
            home_abbr = home_team.split(' ')[0] 
            away_abbr = away_team.split(' ')[0] 
            home_team = home_team.replace(home_abbr, team_dict[home_abbr])
            away_team = away_team.replace(away_abbr, team_dict[away_abbr])
            matchup = f'{away_team} @ {home_team}'
            for bet in bets:
                market_id = bet['Id']
                bet_type = bet_type_dict[bet['Name']]
                home, away = bet['Items'][0], bet['Items'][1] 
                home_payout, away_payout = home['Price'], away['Price']
                spov, spun = home['SPOV'], away['SPOV']
                if bet_type == "spread":
                    if spov[0] == '-':
                        spun = f"+{add_dec(spun[1:])}"
                    else:
                        spun = f"-{add_dec(spun[1:])}" 
                    spov = f"{spov[0]}{add_dec(spov[1:])}"
                else:
                    spov, spun = add_dec(spov), add_dec(spun)
                markets.append((
                    market_id, sportsbook, matchup, bet_type, period, date, 
                    home_team, away_team, home_payout, away_payout, spov, spun
                )) 

    return markets

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
    resp = await client.get(url, params=query)
    return resp.json()

def add_dec(string):
    if string.isdigit():
        string = f"{string}.0"
    return string