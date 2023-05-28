import requests
import jmespath


def get_bet99():
    team_dict = {
        # NHL
        "ANA":"Anaheim", "ARI":"Arizona", "BOS":"Boston", 
        "BUF":"Buffalo", "CAR":"Carolina", "CGY":"Calgary", 
        "CBJ":"Columbus", "CHI":"Chicago", "COL":"Colorado", 
        "DET":"Detroit", "DAL":"Dallas", "FLA":"Florida", 
        "EDM":"Edmonton", "MTL":"Montreal", "LA":"Los Angeles", 
        "NJ":"New Jersey", "MIN":"Minnesota", "NYI":"New York", 
        "NSH":"Nashville", "NYR":"New York", "SEA":"Seattle", 
        "OTT":"Ottawa", "SJ":"San Jose", "PIT":"Pittsburgh", 
        "STL":"St. Louis", "TB":"Tampa Bay", "VAN":"Vancouver", 
        "TOR":"Toronto", "VGK":"Vegas", "WSH":"Washington", 
        "WPG":"Winnipeg",
            
        # NBA
        "ATL":"Atlanta", "BKN":"Brooklyn", "CHA":"Charlotte",
        "CLE":"Cleveland", "DEN":"Denver", "GS":"Golden State",
        "HOU":"Houston", "IND":"Indiana", "LAC":"Los Angeles",
        "LAL":"Los Angeles", "MEM":"Memphis", "MIA":"Miami",
        "MIL":"Milwaukee", "NOP":"New Orleans", "NY":"New York",
        "OKC":"Okalahoma City", "ORL":"Orlando", "PHI":"Philadelphia",
        "PHX":"Phoenix", "POR":"Portland", "SAC":"Sacremento",
        "SAS":"San Antonio", "UTA":"Utah",
        
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
    events_url = "https://sb2frontend-altenar2.biahosted.com/api/Sportsbook/GetEvents" 
    markets = []
    sportsbook = "Bet99"
    period = 0  
 
    # expressions
    bet_type_keys = [f'`{key}`' for key in bet_type_dict]
    bet_type_query = f"[{', '.join(bet_type_keys)}]"
    des_bets = f"Events[*].Items[?contains({bet_type_query}, Name)]."
    matchup_exp = "Events[*].Name"
    date_exp = "Events[*].EventDate"
    matchup_ids_exp = f"{des_bets}Id"
    bet_types_exp = f"{des_bets}Name"
    payouts_exp = f"{des_bets}Items[*].Price"
    sp_ttl_exp = f"{des_bets}Items[*].SPOV"

    for query in sport_queries:
        full_query = gen_query.copy()
        full_query |= query
        resp = requests.request("GET", events_url, params=full_query).json()
        data = resp['Result']['Items'][0]

        # searches
        matchups = jmespath.search(matchup_exp, data)
        dates = jmespath.search(date_exp, data)
        matchup_ids = jmespath.search(matchup_ids_exp, data) 
        bet_types = jmespath.search(bet_types_exp, data) 
        payouts = jmespath.search(payouts_exp, data)
        sp_totals = jmespath.search(sp_ttl_exp, data)
        
        for matchup, date, m_ids, b_types, pays, sptos in zip(
                matchups, dates, matchup_ids, bet_types, payouts, sp_totals):
            home, away = matchup.split(' vs. ')
            home_abbr = home.split(' ')[0] 
            away_abbr = away.split(' ')[0] 
            home = home.replace(home_abbr, team_dict[home_abbr])
            away = away.replace(away_abbr, team_dict[away_abbr])
            matchup = f"{away} @ {home}"
            for m_id, b_type, pay, spto in zip(m_ids, b_types, pays, sptos):
                b_type = bet_type_dict[b_type]
                home_payout = pay[0]
                away_payout = pay[1] 
                spov = spto[0]
                spun = spto[1]
                if spun == "spread":
                    spun = f"+{spun[1:]}" if spov.startswith("-") else f"-{spun[1:]}"
                markets.append((m_id, sportsbook, matchup, b_type, period, 
                    date, home, away, home_payout, away_payout, spov, spun
                ))

    return markets