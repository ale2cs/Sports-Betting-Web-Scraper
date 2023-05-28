import cloudscraper
import jmespath
from utils import rnd_dec


bet_type_dict = {
    27:"moneyline",
    28:"total",
    180:"spread", 
    704:"total", 
    716:"spread", 
    795:"spread", 
    977:"spread", 
}
sport_urls = [
    "https://www.sportsinteraction.com/hockey/nhl-betting-lines", 
    "https://www.sportsinteraction.com/basketball/nba-betting-lines/", 
    "https://www.sportsinteraction.com/baseball/mlb-betting-lines/",
    "https://www.sportsinteraction.com/baseball/national-league-betting-lines/",
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

def get_sports_interaction():
    # Scrapes Sports Interaction and appends results into database
    markets = []
   
    scraper = cloudscraper.create_scraper()

    game_urls = []

    # scrape game urls to access more markets
    for url in sport_urls:
        resp = scraper.get(url, headers=headers).json()
        games = resp['props']['games']
        for game in games:
            gamePath = game['gamePath']
            game_urls.append(f"https://www.sportsinteraction.com{gamePath}")

    sportsbook = "Sports Interaction"
    period = 0  # only full game including OT 
    dec = 3     # rounding down payouts

    # expressions
    bet_type_keys = [f'`{key}`' for key in bet_type_dict]
    bet_type_query = f"[{', '.join(bet_type_keys)}]"
    des_bets = ("gameData."
                f"betTypeGroups[?contains({bet_type_query}, betTypeId)]")
    market_exp = "betTypes[0].events[*].runners[*]"

    # scrape markets from each game page
    for url in game_urls:
        resp = scraper.get(url, headers=headers).json()
        data = resp['props']

        matchup = data['game']['fullName']
        to_replace = [' (A)', ' (N)']
        for word in to_replace:
            matchup = matchup.replace(word, '')
        away, home = matchup.split(' @')

        date = data['game']['date']
        date = date.replace('.000', '')

        # searches
        bets = jmespath.search(des_bets, data)
        for bet in bets:
            bet_type = bet_type_dict[bet['betTypeId']]
            order = [0, 1] if bet_type == "total" else [1, 0]
            market_data = jmespath.search(market_exp, bet)
            for market in market_data:
                market_id = market['eventId']
                home_payout = rnd_dec(market[order[0]]['currentPrice'], dec)
                away_payout = rnd_dec(market[order[1]]['currentPrice'], dec)
                spov = market[order[0]]['handicap']
                spun = market[order[1]]['handicap']
                if bet_type == 'spread':
                    if (spov[0] == '-'):
                        spun = f"-{spun}"
                    elif (spun[0] == '-'):
                        spov = f"+{spov}"
                markets.append((market_id, sportsbook, matchup, bet_type, 
                    period, date, home, away, home_payout, away_payout, spun, 
                    spov
                ))
    return markets

def get_games():
    pass     