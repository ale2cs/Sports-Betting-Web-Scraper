import requests
import jmespath
from sportbooks.utils import epoch_to_iso

def get_bodog():
    bet_type_dict = {
        "Moneyline":"moneyline",
        "Runline":"spread",
        "Spread":"spread",
        "Puckline":"spread",
        "Total":"total",
        "Total Runs O/U":"total",
        "Total Goals O/U":"total",

    }
    leagues = ('hockey/nhl', 'basketball/nba', 'baseball/mlb',)
    query = {"preMatchOnly":"true"}

    markets = []
    sportsbook = "Bodog"
    period = 0

    bet_type_keys = [f"'{key}'" for key in bet_type_dict]
    bet_type_query = f"[{', '.join(bet_type_keys)}]"
    des_bets_exp = f"displayGroups[*].markets[?contains({bet_type_query}, description) && period.description == 'Game']"

    for league in leagues: 
        url = f"https://www.bodog.eu/services/sports/event/coupon/events/A/description/{league}"
        resp = requests.request("GET", url, params=query).json()
        events = resp[0]['events']

        for event in events:
            matchup = event['description']
            away_team, home_team = matchup.split(' @ ')
            date = epoch_to_iso(event['startTime'] / 1000)
            des_bets = jmespath.search(des_bets_exp, event)
            for group in des_bets:
                for market in group:
                    bet_type = bet_type_dict[market['description']]
                    outcomes = market['outcomes']
                    for i, value in enumerate(outcomes):
                        if i % 2 != 0:
                            continue
                        away, home = outcomes[i], outcomes[i+1]
                        market_id = away['id']
                        away, home = away['price'], home['price']
                        if bet_type != 'total':
                            home_payout, away_payout = home['decimal'], away['decimal']
                        else:
                            away_payout, home_payout = home['decimal'], away['decimal']
                        if bet_type == 'moneyline':
                            spov = spun = ''
                        elif bet_type == 'spread':
                            spov, spun = home['handicap'], away['handicap']
                            if spov[0] == '-':
                                spun = f"+{spun}"
                            elif spun[0] == '-':
                                spov = f"+{spov}"
                        else:
                            spov, spun = home['handicap'], away['handicap']
                        markets.append((market_id, sportsbook, matchup, bet_type, 
                            period, date, home_team, away_team, home_payout, 
                            away_payout, spov, spun
                        ))
    return markets

