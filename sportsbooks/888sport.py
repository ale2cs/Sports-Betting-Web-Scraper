import asyncio
import httpx
from playwright.async_api import async_playwright

async def get_888sport():
    base_url = "https://www.888sport.com"
    url = "https://spectate-web.888sport.com/spectate/sportsbook-req/getTournamentMatches/baseball/united-states-of-america/major-league-baseball"
    bet_type_dict = {
        "Run Line":"spread",
        "Total Runs Over/Under":"total",
        "Money Line":"moneyline",

    }
    lines = []
    cookies = await get_cookies(base_url)

    async with httpx.AsyncClient() as client:
        data = await make_request(client, url, cookies,  'POST')
        games = data['events']

    responses = await get_data(games, cookies)
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


async def get_cookies(base_url):
    valid_cookies = ['888Cookie', '888TestData', 'bbsess', 'lang', 'anon_hash', 'spectate_session', 'odds_format']
    async with async_playwright() as playwright:
        browser = await playwright.firefox.launch()
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'
        )
        page = await context.new_page()
        await page.goto(base_url)
        await page.wait_for_timeout(1000)
        cookies_list = await context.cookies()
        valid_cookies_list = []
        for cookie in cookies_list:
            name = cookie['name']
            if name in valid_cookies:
                valid_cookies_list.append(f"{name}={cookie['value']}")
        cookies = "; ".join(valid_cookies_list)
        await browser.close()
    return cookies


async def make_request(client, url, cookies, method):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "x-spectateclient-v": "2.32",
        "content-type": "multipart/form-data; boundary=---011000010111000001101001"

    } 
    headers['Cookie'] = cookies
    if method == 'GET':
        resp = await client.get(url, headers=headers, timeout=30)
    elif method == 'POST':
        resp = await client.post(url, headers=headers)
    return resp.json()


async def get_data(games, cookies):
    async with httpx.AsyncClient() as client:
        tasks = []
        for game_id in games:
            game_url = f"https://spectate-web.888sport.com/spectate/sportsbook/getEventData{games[game_id]['event_url']}/{game_id}"
            if 'mlb' not in game_url:
                continue
            game_url = game_url.replace('mlb', 'major-league-baseball')
            tasks.append(asyncio.ensure_future(make_request(client, game_url, cookies, 'GET'))) 
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