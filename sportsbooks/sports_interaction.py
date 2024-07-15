import httpx
import re
import asyncio

spread_total_pattern = re.compile(r'-?\d+\.?\d*')
multiple_game_day_pattern = re.compile(r'\(Game \d+\)')

bet_type_dict = {
    'Money Line': 'moneyline', 
    'Totals':'total',
    'Total Goals': 'total',
    'Run Line Spread':'spread', 
    'Spread':'spread',
    # 'Draw No Bet': 'dnb',
}
url = "https://sports.sportsinteraction.com/en-ca/sports/api/widget/widgetdata"
leagues = [
    ('Baseball', 'MLB', 23, 'baseball/baseballlobby', None),
    ('Basketball', 'WNBA', 7, 'basketball/nba/sportlobbywnba', None),
    # (4, 'soccer/soccerlobby', 102849) # Soccer
]
sportsbook = "Sports Interaction"

async def get_sports_interaction():
    async with httpx.AsyncClient() as client:
        tasks = [fetch_game_data(client, sport, league, sport_id, layout_name, competition_id) for sport, league, sport_id, layout_name, competition_id in leagues]
        all_results = await asyncio.gather(*tasks)
        return [result for sublist in all_results for result in sublist]

async def fetch_game_data(client, sport, league, sport_id, layout_name, competition_id):
    querystring = {
        "layoutSize": "Large",
        "page": "SportLobby",
        "sportId": f"{sport_id}",
        "competitionId": competition_id,
        "widgetId": f"/mobilesports-v1.0/layout/layout_us/modules/{layout_name}",
        "shouldIncludePayload": "true"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://sports.sportsinteraction.com/en-ca/sports/baseball-23",
        "x-bwin-browser-url": "https://sports.sportsinteraction.com/en-ca/sports/baseball-23",
        "X-App-Context": "default",
        "X-Device-Type": "desktop",
        "X-From-Product": "sports",
        "DNT": "1",
        "Alt-Used": "sports.sportsinteraction.com",
        "Connection": "keep-alive"
    }

    resp = await client.get(url, headers=headers, params=querystring)
    data = resp.json()

    results = []
    games = data['widgets'][0]['payload']['fixtures']
    for game in games:
        game_id = game['sourceId']
        if sport_id == 4:
            game_id = f'2:{game_id}'
        single_game_url = "https://sports.sportsinteraction.com/cds-api/bettingoffer/fixture-view"

        querystring = {
            "x-bwin-accessid": "OGQ2ZTg0MGYtYjkwNS00ZmI1LTlkN2YtZDVmY2Y0ZDNkYmFl",
            "lang": "en-ca",
            "country": "CA",
            "userCountry": "CA",
            "subdivision": "CA-Alberta",
            "offerMapping": "All",
            "scoreboardMode": "Full",
            "fixtureIds": f"{game_id}",
            "state": "Latest",
            "includePrecreatedBetBuilder": "true",
            "supportVirtual": "false",
            "isBettingInsightsEnabled": "false",
            "useRegionalisedConfiguration": "true",
            "includeRelatedFixtures": "false",
            "statisticsModes": "None"
        }

        resp = await client.get(single_game_url, headers=headers, params=querystring)
        single_game = resp.json()
        game_name = single_game['fixture']['name']['value'].replace(' at ', ' @ ').replace(' - ', ' @ ')
        game_name = multiple_game_day_pattern.sub('', game_name).strip()
        date = single_game['fixture']['startDate']
        markets = single_game['fixture']['optionMarkets'] + single_game['fixture']['games']
        period = 0
        for market in markets:
            bet_type = market['name']['value']
            if bet_type in bet_type_dict:
                bet_type = bet_type_dict[bet_type]
                order = [0, 1] if bet_type == "total" else [1, 0]
                if 'options' in market:
                    home, away = market['options'][order[0]], market['options'][order[1]]
                else:
                    home, away = market['results'][order[0]], market['results'][order[1]]
                spov = home['name']['value']
                if 'price' in home:
                    home_odds = home['price']['odds']
                else:
                    home_odds = home['odds']
                spun = away['name']['value']
                if 'price' in away:
                    away_odds = away['price']['odds']
                else:
                    away_odds = away['odds']
                if bet_type == 'moneyline':
                    spov, spun = '', ''
                else:
                    spov = spread_total_pattern.search(spov).group()
                    spun = spread_total_pattern.search(spun).group()
                    if bet_type == 'spread':
                        if spov[0] == '-':
                            spun = f"+{spun}"
                        elif spun[0] == '-':
                            spov = f"+{spov}"

                results.append((sport, league, game_name, bet_type, period, date, spov, spun, sportsbook, home_odds, away_odds))
    return results