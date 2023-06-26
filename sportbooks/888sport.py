import asyncio
import httpx

async def get_888sport():
    url = "https://spectate-web.888sport.com/spectate/sportsbook-req/getUpcomingMatchesEventsAjax/baseball"

    bet_type_dict = {
        "Run Line":"spread",
        "Total Runs Over/Under":"total",
        "Money Line":"moneyline",

    }
    markets = []
    sportsbook = "888Sport"
    period = 0
    async with httpx.AsyncClient() as client:
        data = await make_request(client, url, 'POST')
        games = data['events']

    responses = await get_data(games)
    for data in responses: 
        event = data['event']['details']['event']
        lines = data['event']['markets']['markets_selections']
        des_lines = data['event']['markets']['markets_selections']['gameLineMarket']['group_markets']
        matchup = event['name']
        date = event['scheduled_start']
        away_team, home_team = matchup.split(' @ ') 
        for line_id in des_lines:
            market = lines[line_id]
            if 'options' in market:
                options = market['options']
                selections = market['selections']
                for option in options:
                    line = selections[option][option]
                    home, away = line
                    home_odds, away_odds = home['decimal_price'], away['decimal_price']
                    bet_type = bet_type_dict[home['market_name']]
                    spov = home['special_odds_value']
                    spun = away['special_odds_value']
                    lines.append((
                        matchup, bet_type, period, date, spov, spun, sportsbook, 
                        home_odds, away_odds
                    ))
            else:
                home, away = line
                home_odds, away_odds = home['decimal_price'], away['decimal_price']
                bet_type = bet_type_dict[home['market_name']]
                spov = spun = ''
                lines.append((
                    matchup, bet_type, period, date, spov, spun, sportsbook, 
                    home_odds, away_odds
                ))


    return markets

async def get_data(games):
    async with httpx.AsyncClient() as client:
        tasks = []
        for game_id in games:
            game_url = f"https://spectate-web.888sport.com/spectate/sportsbook/getEventData{games[game_id]['event_url']}/{game_id}"
            if 'mlb' not in game_url:
                continue
            game_url = game_url.replace('mlb', 'major-league-baseball')
            tasks.append(asyncio.ensure_future(make_request(client, game_url, 'GET'))) 
        responses = await asyncio.gather(*tasks)
    return responses

async def make_request(client, url, type):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.888sport.com/",
        "x-spectateclient-v": "2.27",
        "Origin": "https://www.888sport.com",
        "DNT": "1",
        "Connection": "keep-alive",
        "Cookie": "888Attribution=1; 888Cookie=lang%3Den%26OSR%3D1927680; 888TestData=%7B%22orig-lp%22%3A%22https%3A%2F%2Fwww.888sport.com%2F%22%2C%22currentvisittype%22%3A%22Unknown%22%2C%22strategy%22%3A%22UnknownStrategy%22%2C%22strategysource%22%3A%22currentvisit%22%2C%22datecreated%22%3A%222023-06-21T15%3A49%3A36.457Z%22%2C%22expiredat%22%3A%22Wed%2C%2028%20Jun%202023%2015%3A49%3A00%20GMT%22%7D; bbsess=Vl0r8kEl00%2Cj8nY%2C69xZSRwA56V; lang=enu; anon_hash=d3fd5ba36aec57816aa9c2957e8d32c2; spectate_session=15f04c9a-c180-47f6-a16c-5cb283168524%3Aanon; odds_format=DECIMAL",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers",
        "content-type": "multipart/form-data; boundary=---011000010111000001101001"
    }
    if type == 'GET':
        resp = await client.get(url, headers=headers)
    elif type == 'POST':
        resp = await client.post(url, headers=headers)
    return resp.json()