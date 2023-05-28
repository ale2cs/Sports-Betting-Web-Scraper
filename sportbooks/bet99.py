import requests
import jmespath


def get_bet99():
    team_dict = {
        # NHL
        'ANA': 'Anaheim', 'ARI': 'Arizona', 'BOS': 'Boston', 
        'BUF': 'Buffalo', 'CAR': 'Carolina', 'CBJ': 'Columbus', 
        'CGY': 'Calgary', 'CHI': 'Chicago', 'COL': 'Colorado', 
        'DAL': 'Dallas', 'DET': 'Detroit', 'EDM': 'Edmonton', 
        'FLA': 'Florida', 'LA': 'Los Angeles', 'MIN': 'Minnesota', 
        'MTL': 'Montreal', 'NJ': 'New Jersey', 'NSH': 'Nashville', 
        'NYI': 'New York', 'NYR': 'New York', 'OTT': 'Ottawa', 
        'PIT': 'Pittsburgh', 'SEA': 'Seattle', 'SJ': 'San Jose', 
        'STL': 'St. Louis', 'TB': 'Tampa Bay', 'TOR': 'Toronto', 
        'VAN': 'Vancouver', 'VGK': 'Vegas', 'WSH': 'Washington', 
        'WPG': 'Winnipeg',
            
        # NBA
        'ATL': 'Atlanta', 'BKN': 'Brooklyn', 'CHA': 'Charlotte', 
        'CLE': 'Cleveland', 'DEN': 'Denver', 'GS': 'Golden State', 
        'HOU': 'Houston', 'IND': 'Indiana', 'LAC': 'Los Angeles', 
        'LAL': 'Los Angeles', 'MEM': 'Memphis', 'MIA': 'Miami', 
        'MIL': 'Milwaukee', 'NOP': 'New Orleans', 'NY': 'New York', 
        'OKC': 'Oklahoma City', 'ORL': 'Orlando', 'PHI': 'Philadelphia', 
        'PHX': 'Phoenix', 'POR': 'Portland', 'SAC': 'Sacramento', 
        'SAS': 'San Antonio', 'UTA': 'Utah',
        
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
    bet_type_keys = [f"'{key}'" for key in bet_type_dict]
    bet_type_query = f"[{', '.join(bet_type_keys)}]"
    des_bets_exp = f"Events[*].Items[?contains({bet_type_query}, Name)]"
    events_exp = "Events[*]"

    for query in sport_queries:
        full_query = gen_query.copy()
        full_query |= query
        resp = requests.request("GET", events_url, params=full_query).json()
        data = resp['Result']['Items'][0]

        # searches
        game_bets = jmespath.search(des_bets_exp, data) 
        events = jmespath.search(events_exp, data)

        for bets, event in zip(game_bets, events):
            matchup = event['Name']
            date = event['EventDate']
            for bet in bets:
                market_id = bet['Id']
                bet_type = bet_type_dict[b['Name']]
                home = bet['Items'][0]
                away = bet['Items'][1]
                home_team, away_team = matchup.split(' vs. ')
                home_abbr = home_team.split(' ')[0] 
                away_abbr = away_team.split(' ')[0] 
                home_team = home_team.replace(home_abbr, team_dict[home_abbr])
                away_team = away_team.replace(away_abbr, team_dict[away_abbr])
                home_payout= home['Price']
                away_payout = away['Price']
                spov = home['SPOV']
                spun = away['SPOV']
                if spun == "spread":
                    spun = f"+{spun[1:]}" if spov.startswith("-") else f"-{spun[1:]}"

                markets.append((
                    market_id, sportsbook, matchup, bet_type, period, date, 
                    home_team, away_team, home_payout, away_payout, spov, spun
                )) 

    return markets