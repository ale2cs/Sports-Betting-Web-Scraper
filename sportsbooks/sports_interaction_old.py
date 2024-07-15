import cloudscraper
from concurrent.futures import ThreadPoolExecutor
from utils.calcs import rnd_dec

scraper = cloudscraper.CloudScraper(
    browser={
        'browser':'firefox', 
        'mobile':True, 
        'platform':'android'
    },
    # delay=10,
    # ssl_context=ssl._create_unverified_context(),
)

def get_sports_interaction():
    # Scrapes Sports Interaction and returns lines
    bet_type_dict = {
        27: "moneyline",
        28: "total",
        75: "moneyline",
        180: "spread",
        252: "spread",
        279: "total",
        704: "total",
        716: "spread",
        795: "spread",
        977: "spread",
        1423: "total",
    }
    sport_urls = [
        "https://www.sportsinteraction.com/hockey/nhl-betting-lines",
        "https://www.sportsinteraction.com/basketball/nba-betting-lines/",
        "https://www.sportsinteraction.com/baseball/mlb-betting-lines/",
        "https://www.sportsinteraction.com/baseball/national-league-betting-lines/",
        "https://www.sportsinteraction.com/basketball/wnba-betting-lines/",
        "https://www.sportsinteraction.com/football/nfl-betting-lines/",
        "https://www.sportsinteraction.com/football/ncaa-betting-lines/",
        # "https://www.sportsinteraction.com/soccer/canada-us/major-league-soccer-betting/",
        # "https://www.sportsinteraction.com/baseball/japanese-betting-lines/"
    ]

    game_urls = scrape_game_urls(sport_urls)
    game_data = scrape_game_data(game_urls) 
    lines = scrape_lines(game_data, bet_type_dict)
    return lines


def scrape_game_urls(sport_urls):
    game_urls = [] 

    with ThreadPoolExecutor() as executor:
        responses = executor.map(scrape, sport_urls)
    for resp in responses:
        games = resp['props']['games']
        for game in games:
            if (not valid_game_name(game['gameName'])):
                continue
            gamePath = game['gamePath']
            game_urls.append(f"https://www.sportsinteraction.com{gamePath}")

    return game_urls


def scrape(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Accept": "text/html, application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "x-momentum": "true",
        "DNT": "1",
        "Alt-Used": "www.sportsinteraction.com",
        "Connection": "keep-alive",
        "Cookie": "split=%7B%22odds_format_signup%22%3A%22decimal%22%2C%22odds_format_switch_to_decimal%22%3A%22decimal%22%2C%22odds_format_switch_to_fraction%22%3A%22decimal%22%2C%22odds_format_switch_to_american%22%3A%22decimal%22%7D; __sia_session=Mx0GoIirwn%2FGZHM1nc278XD5HgAqniFIVaddkj0lE4DMVthY9rDSMp55voXQd8oSvwTY%2FKCnIMRTIkTOC2pLY1mqXkvxoZGMZ3l829q5mcZof%2BcCE27YM9XnJ6lQaOdT7O8mSCR6hvGb5EqAEfTeiIQ2L85RFjRC6GfVqt5d%2BponK788ebM7Of16RWwlsvbOLC4EzEQcpR7V5k4VNPCLg6A7v7z%2BjTziF13M0qOlf1Tralsl9JYase0qnI9fVAj8Op6OkFZwBmAoW%2BbRWOmipCa%2BM15XWehtz0y45GvZILn11o3bZeJVRm6WFmN8UJJC1f2iqqnnZhKk7kr7dD7MHCm%2FuOlChil9L3YgXVzy6izNRtytmMlvqIZC86pGzzogtzI0QQtCKU%2FFH7b1O0Nh4hs4scn%2B%2BiirfHEwh39laseu4K3uXu4H9b270BSpl8ePpCoTLtpB9kD7abXpSI7t%2B6%2B%2BXdIB5j%2FZr21CRZkptRQX6PoO11cgreH0uDMXadXMyOwMphB%2BUMiZybEpVfHfsIzV8URow4mmwFtbrbw699VPV9jvkqebCg4o6XD1hJku0ZJyNgB14lEXMskea3OwzWdIZJuF4rcRQutCUTKOiEFAKZ7igX20HBPWJv7LDwDq3gdPbWFHftTiS1Cx74MiTkv4s5evRdtHwQ0Z4bHvGBq1rJYqxSp5pg3P1R4PXazrdOj41HYUpUeYlhWVF%2BpkH%2B0XtUkfObvJbPKap%2FZ%2FawvYcSdm991cib3TI%2BhO4%2BOYFrChdlbR5KnLCX3N29PuAKVpV2D9DgkH2F3k2kk7mJTtqiKEheQwFZ%2F%2B4HU1GPpDXmpxmNUD5oznx5RxEUIvrF13Wgv10zq0M%2BZb4xS%2FFifIqxK1UdhqZtC2zkd9J4oFxVCBTmM2MI8YP9boZWmoz2bggCZ5fSE%3D--RDM9ywiR%2BoUcM8sq--DeqIIrDS8JaLM09fVwIdQg%3D%3D; __cf_bm=Hy66PYJGt7NQ_y_dtZzr0veaZuSeJ3oA_1AHwe8QiTM-1682900274-0-AVhcGyR0hkffT2V7LIkSCxBObiMxSGtYqjDMSSUuJJapxGLtbQjLvAyzUUl/Y2/n/QPUwmHE3tCmIMD8jJmfyDTBpEfwosHCmvAWJDFnpVSFTNlqqh+MfsfkJTU3HH2rrpOzPJiHVgK5LVQQTCpcDlg=; menu_swipeable_animation_seen=true; SPORTSMENUFAVS=3%2C23",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }
    resp = scraper.get(url, headers=headers)
    return resp.json()


def valid_game_name(game_name):
    # game name cannot exceed 7 words
    words = game_name.split(' ')
    return len(words) <= 7


def scrape_game_data(game_urls):
    with ThreadPoolExecutor(max_workers=100) as executor:
        responses = executor.map(scrape, game_urls)
    return responses


def scrape_lines(game_data, bet_type_dict):
    lines = []    
    for resp in game_data:
        market_values = {}
        data = resp['props']
        market_values['matchup'] = clean_matchup(data['game']['fullName'])
        date = data['game']['date']
        market_values['date'] = date.replace('.000', '')
        markets = parse_markets(data, bet_type_dict) 

        for bet in markets:
            bet_type = bet_type_dict[bet['betTypeId']]
            market_values['bet_type'] = bet_type
            market_values['order'] = [0, 1] if bet_type == "total" else [1, 0]
            market_data = bet['betTypes'][0]['events']
            for parsed_lines in parse_lines(market_data, market_values):
                lines.append(parsed_lines)
    return lines


def clean_matchup(matchup):
    unusual_team_name = {
        "LA Anaheim":"Los Angeles",
    }

    for key, value in unusual_team_name.items():
        if key in matchup:
            matchup = matchup.replace(key, value)

    to_replace = [' (A)', ' (N)']
    for word in to_replace:
        matchup = matchup.replace(word, '')
    return matchup


def parse_markets(data, bet_type_dict):
    markets = []
    if 'betTypeGroups' in data['gameData']:
        for market in data['gameData']['betTypeGroups']:
            if market['betTypeId'] in bet_type_dict:
                markets.append(market)
    return markets


def parse_lines(market_data, market_values):
    sportsbook = "Sports Interaction"
    period = 0
    dec = 3
    matchup, date, bet_type, order = market_values.values()
    for market in market_data:
        if market['live'] == False:  # Market is locked
            continue
        line = market['runners']
        # over/under and spread can swap home and away values
        # if bet['betTypeId'] == 704 or bet['betTypeId'] == 795:
        #    away, home = line[order[0]], line[order[1]]
        # else:
        home, away = line[order[0]], line[order[1]]
        home_odds = rnd_dec(home['currentPrice'], dec) + 1
        away_odds = rnd_dec(away['currentPrice'], dec) + 1
        spov, spun = str(home['handicap']), str(away['handicap'])
        if bet_type == 'spread':
            if spov[0] == '-':
                spun = f"+{spun}"
            elif spun[0] == '-':
                spov = f"+{spov}"
        elif bet_type == 'moneyline':
            spov = spun = ''

        #yield ({
        #    'matchup':matchup, 'bet_type':bet_type, 'period':period, 
        #    'date':date, 'spov':spov, 'spun':spun, 'sportsbook':sportsbook, 
        #    'home_odds':home_odds, 'away_odds':away_odds
        #})
        yield ((
            matchup, bet_type, period, date, spov, spun, sportsbook, 
            home_odds, away_odds
        ))