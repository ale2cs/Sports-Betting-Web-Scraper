import requests
from requests.adapters import HTTPAdapter, Retry
import jmespath
from sportbooks.utils import epoch_to_iso

def get_bodog():
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

    markets = []
    sportsbook = "Bodog"
    period = 0

    bet_type_keys = [f"'{key}'" for key in bet_type_dict]
    bet_type_query = f"[{', '.join(bet_type_keys)}]"
    des_bets_exp = f"displayGroups[*].markets[?contains({bet_type_query}, description) && (period.description == 'Game' || period.description == 'Regulation Time')]"

    for data in make_requests(): 
        events = data[0]['events']

        reverse = False
        for event in events:
            matchup = event['description']
            if '@' in matchup:
                away_team, home_team = matchup.split(' @ ')
            elif 'vs' in matchup:
                home_team, away_team = matchup.split(' vs ')
                matchup = f"{away_team} @ {home_team}"
                reverse = True
            else:
                continue
            date = epoch_to_iso(event['startTime'] / 1000)
            des_bets = jmespath.search(des_bets_exp, event)
            for group in des_bets:
                for market in group:
                    bet_type = bet_type_dict[market['description']]
                    outcomes = market['outcomes']
                    if ((len(outcomes) % 2) != 0):  # quick fix
                        outcomes.pop(0)
                    for i, value in enumerate(outcomes):
                        if i % 2 != 0:
                            continue 
                        away, home = outcomes[i], outcomes[i+1]
                        market_id = away['id']
                        away, home = away['price'], home['price'] 
                        if bet_type != 'total' and not reverse:
                            home_payout, away_payout = home['decimal'], away['decimal']
                        else:
                            away_payout, home_payout = home['decimal'], away['decimal']

                        if bet_type != 'moneyline':
                            if 'handicap2' in home:
                                spov = str((float(home['handicap']) + float(home['handicap2'])) / 2)
                                spun = str((float(away['handicap']) + float(away['handicap2'])) / 2)
                            else:
                                spov, spun = home['handicap'], away['handicap']
                        else:
                            spov = spun = ''
                        
                        if bet_type == 'spread':
                            if spov[0] == '-':
                                spun = f"+{spun}"
                            elif spun[0] == '-':
                                spov = f"+{spov}"

                        markets.append((market_id, sportsbook, matchup, bet_type, 
                            period, date, home_team, away_team, home_payout, 
                            away_payout, spov, spun
                        ))
    return markets

def make_requests():
    headers = {
        "cookie": "TS014505a4=014b5d5d074621dcb805603f6ecd400ce1005af41531ed96e612911b0ac1d43907fae8b6e0d8487c332e76c9c3ce7978a0e89cfbdf",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
    }
    query = {"preMatchOnly":"true"}
    leagues = (
        'hockey/nhl', 
        'basketball/nba', 
        'baseball/mlb', 
        'soccer/north-america/united-states/mls',
        'baseball/japan/professional-baseball',
        'basketball/wnba',
    )

    responses = []
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504, 429])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    for league in leagues:
        url = f"https://www.bodog.eu/services/sports/event/coupon/events/A/description/{league}"
        resp = session.get(url, headers=headers, params=query)
        if data := resp.json():
            responses.append(data)
    session.close()
    return responses