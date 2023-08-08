import asyncio
import httpx

async def get_888sport():
    url = "https://spectate-web.888sport.com/spectate/sportsbook-req/getTournamentMatches/baseball/united-states-of-america/major-league-baseball"
    bet_type_dict = {
        "Run Line":"spread",
        "Total Runs Over/Under":"total",
        "Money Line":"moneyline",

    }
    lines = []

    async with httpx.AsyncClient() as client:
        data = await make_request(client, url, 'POST')
        games = data['events']

    responses = await get_data(games)
    for data in responses: 
        event = data['event']['details']['event']
        markets = data['event']['markets']['markets_selections']
        des_lines = data['event']['markets']['markets_selections']['gameLineMarket']['group_markets']
        market_values = {}
        market_values['matchup'] = event['name']
        market_values['date'] = event['scheduled_start']
        for parsed_lines in parse_lines(des_lines, markets, market_values, bet_type_dict):
            lines.append(parsed_lines)
    return lines


async def make_request(client, url, type):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0",
        "x-spectateclient-v": "2.32",
        "Cookie": "888Cookie=lang%3Den%26OSR%3D1911954; 888TestData=%7B%22referrer%22%3A%22https%3A%2F%2Fwww.google.com%2F%22%2C%22last-referrer%22%3A%22https%3A%2F%2Fwww.google.com%2F%22%2C%22orig-lp%22%3A%22https%3A%2F%2Fwww.888sport.com%2F%22%2C%22currentvisittype%22%3A%22SEO%22%2C%22strategy%22%3A%22SeoStrategy%22%2C%22strategysource%22%3A%22currentvisit%22%2C%22publisher%22%3A%22SearchEngine%22%2C%22datecreated%22%3A%222023-08-04T16%3A10%3A56.985Z%22%2C%22expiredat%22%3A%22Fri%2C%2011%20Aug%202023%2016%3A10%3A00%20GMT%22%7D; bbsess=v8cTjCGxR3w-LXeOl7TTsZwQSwz; lang=enu; anon_hash=d3fd5ba36aec57816aa9c2957e8d32c2; spectate_session=0f3c1e90-718a-461b-9ef0-73c444f1ff6d%3Aanon; odds_format=DECIMAL",
        "content-type": "multipart/form-data; boundary=---011000010111000001101001"
    }
    if type == 'GET':
        resp = await client.get(url, headers=headers, timeout=15)
    elif type == 'POST':
        resp = await client.post(url, headers=headers)
    return resp.json()


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


def parse_lines(des_lines, markets, market_values, bet_type_dict):
    sportsbook = "888Sport"
    period = 0
    matchup, date = market_values.values()

    for line_id in des_lines:
        if line_id not in markets:
            continue
        market = markets[line_id]
        if 'options' in market:
            options = market['options']
            selections = market['selections']
            for option in options:
                line = selections[option][option]
                away, home = line
                bet_type = bet_type_dict[home['market_name']]
                if bet_type == 'total':
                    away_odds, home_odds = home['decimal_price'], away['decimal_price']
                else:
                    home_odds, away_odds = home['decimal_price'], away['decimal_price']
                spov = home['special_odds_value']
                spun = away['special_odds_value'] 
                if bet_type == 'spread':
                    if spov[0] == '-':
                        spun = f'+{spun}'
                    else:
                        spov = f'+{spov}' 
                yield ({
                    'matchup':matchup, 'bet_type':bet_type, 'period':period, 
                    'date':date, 'spov':spov, 'spun':spun, 'sportsbook':sportsbook, 
                    'home_odds':home_odds, 'away_odds':away_odds
                })

        else:
            away, home = market
            home_odds, away_odds = home['decimal_price'], away['decimal_price']
            bet_type = bet_type_dict[home['market_name']]
            spov = spun = ''
            yield ({
                'matchup':matchup, 'bet_type':bet_type, 'period':period, 
                'date':date, 'spov':spov, 'spun':spun, 'sportsbook':sportsbook, 
                'home_odds':home_odds, 'away_odds':away_odds
            })