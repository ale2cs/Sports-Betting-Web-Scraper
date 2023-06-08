import cloudscraper
import jmespath
from sportbooks.utils import rnd_dec


def get_sports_interaction():
    # Scrapes Sports Interaction and returns markets
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
        "https://www.sportsinteraction.com/soccer/canada-us/major-league-soccer-betting/",
        "https://www.sportsinteraction.com/basketball/wnba-betting-lines/"
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0",
        "Accept": "text/html, application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "x-momentum": "true",
        "DNT": "1",
        "Alt-Used": "www.sportsinteraction.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }

    scraper = cloudscraper.create_scraper()

    game_urls = scrape_game_urls(sport_urls, headers, scraper)

    return scrape_markets(game_urls, bet_type_dict, headers, scraper)


def scrape_game_urls(sport_urls, headers, scraper):
    game_urls = []

    for url in sport_urls:
        resp = scraper.get(url, headers=headers).json()
        games = resp['props']['games']
        for game in games:
            if (not valid_game_name(game['gameName'])):
                continue
            gamePath = game['gamePath']
            game_urls.append(f"https://www.sportsinteraction.com{gamePath}")

    return game_urls


def scrape_markets(game_urls, bet_type_dict, headers, scraper):
    markets = []
    sportsbook = "Sports Interaction"
    period = 0
    dec = 3
    
    market_exp = "betTypes[0].events[*]"
    for url in game_urls:
        resp = scraper.get(url, headers=headers).json()
        data = resp['props']

        matchup = clean_matchup(data['game']['fullName'])
        if '@' in matchup:
            away_team, home_team = matchup.split(' @ ')
        elif 'v' in matchup:
            home_team, away_team = matchup.split(' v ')
            matchup = f"{away_team} @ {home_team}"
        else:
            continue
        date = data['game']['date']
        date = date.replace('.000', '')

        bet_type_keys = [f'`{key}`' for key in bet_type_dict]
        bet_type_query = f"[{', '.join(bet_type_keys)}]"
        des_bets_exp = (
            f"gameData.betTypeGroups[?contains({bet_type_query}, betTypeId)]"
        )

        bets = jmespath.search(des_bets_exp, data)
        for bet in bets:
            bet_type = bet_type_dict[bet['betTypeId']]
            order = [0, 1] if bet_type == "total" else [1, 0]
            market_data = jmespath.search(market_exp, bet)
            for market in market_data:
                market_id = market['eventId']
                lines = market['runners']
                home, away = lines[order[0]], lines[order[1]]
                home_payout = rnd_dec(home['currentPrice'], dec) + 1
                away_payout = rnd_dec(away['currentPrice'], dec) + 1
                spov, spun = str(home['handicap']), str(away['handicap'])
                if bet_type == 'spread':
                    if spov[0] == '-':
                        spun = f"+{spun}"
                    elif spun[0] == '-':
                        spov = f"+{spov}"
                elif bet_type == 'moneyline':
                    spov = spun = ''
                markets.append((
                    market_id, sportsbook, matchup, bet_type, period, date, 
                    home_team, away_team, home_payout, away_payout, spov, spun
                ))

    return markets

def valid_game_name(game_name):
    # game name cannot exceed 7 words
    words = game_name.split(' ')
    return len(words) <= 7

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