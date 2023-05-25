import requests
import cloudscraper
import sqlite3
import pandas as pd
import jmespath
from sqlite3 import Error
from datetime import datetime, timezone
import math
import json
import time

def main():
    database = "./odds.db"

    # create a database connection
    conn = create_conn(database)

    # create table if not already made
    create_table(conn)

    # remove old markets
    remove_old_markets(conn)

    # add and update new markets
    add_markets(conn, get_sports_int())

def create_conn(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def create_table(conn):
    cur = conn.cursor()
    create = '''CREATE TABLE IF NOT EXISTS markets 
                (market_id INT PRIMARY KEY NOT NULL, 
                sportsbook TEXT, 
                game TEXT, 
                type TEXT,
                period TEXT, 
                date TEXT, 
                home_team TEXT, 
                away_team TEXT, 
                home_payout FLOAT,
                away_payout FLOAT, 
                spov TEXT, 
                spun TEXT)
             '''
    cur.execute(create)

def add_markets(conn, markets):
    # https://www.sqlite.org/lang_UPSERT.html
    cur = conn.cursor()
    upsert = '''INSERT INTO markets 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(market_id) 
                DO UPDATE SET home_payout=excluded.home_payout, 
                away_payout=excluded.away_payout,
                spov=excluded.spov, 
                spun=excluded.spun
             '''
    cur.executemany(upsert, markets)
    conn.commit()
    return cur.lastrowid

def remove_old_markets(conn):
    """
    Remove all markets that the current time has passed
    :param conn:
    :param market:
    :return:
    """
    cur = conn.cursor()
    remove_old = '''DELETE FROM markets
                    WHERE date < ?
                 '''
    cur_date = datetime.now(timezone.utc).isoformat()
    cur.execute(remove_old, (cur_date,))
    conn.commit()

    return cur.lastrowid

def rnd_dec(number, decimals):
    # Returns a value rounded down to a specific number of decimal places.
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more")
    elif decimals == 0:
        return math.floor(number)

    factor = 10 ** decimals
    return math.floor(number * factor) / factor

def get_sports_int():
    # Scrapes Sports Interaction and appends results into database
    markets = []
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
    scraper = cloudscraper.create_scraper()

    game_urls = []

    # scrape game urls to access more markets
    for url in sport_urls:
        resp = scraper.get(url, headers=headers).json()
        games = resp['props']['games']
        for game in games:
            gamePath = game['gamePath']
            game_urls.append('https://www.sportsinteraction.com' + gamePath)

    # scrape markets from each game page
    for url in game_urls:
        resp = scraper.get(url, headers=headers).json()
        data = resp['props']
        bet_type_keys = ['`' + str(s) + '`' for s in list(bet_type_dict.keys())]
        bet_type_query = '[' + ", ".join(bet_type_keys) + ']'

        # expressions
        matchup_exp = "game.fullName"
        date_exp = "game.date"
        bets = ("gameData."
               f"betTypeGroups[?contains({bet_type_query}, betTypeId)].")
        bet_ids_exp = bets + "betTypeId"
        market_ids_exp = bets + "betTypes[0].events[0].eventId"
        payouts_exp = bets + "betTypes[0].events[0].runners[*].currentPrice" 
        spread_exp = bets + "betTypes[0].events[0].runners[*].handicap"
        
        # searches
        date = jmespath.search(date_exp, data)
        bet_ids = jmespath.search(bet_ids_exp, data)
        market_ids = jmespath.search(market_ids_exp, data)
        payouts = jmespath.search(payouts_exp, data)
        sp_ttl = jmespath.search(spread_exp, data)
        matchup = jmespath.search(matchup_exp, data)
        to_replace = [' (A)', ' (N)']

        for word in to_replace:
            matchup = matchup.replace(word, '')

        away, home = matchup.split(' @')
        sportsbook = "Sports Interaction"
        period = 0 # only full game including OT 

        # formating data
        for i in range(len(bet_ids)):
            market_id = market_ids[i]
            bet_type = bet_type_dict[bet_ids[i]]
            dec = 3

            if (bet_type == 'total'):
                order = [0, 1]
            else:
                order = [1, 0]

            if (bet_type == 'moneyline'):
                spov = "" 
                spun = ""
            else:
                spov = str(sp_ttl[i][order[0]])
                spun = str(sp_ttl[i][order[1]])

            if (bet_type == 'spread' and spov[0] == '-'):
                spun = '+' + spun
            else:
                spov = '+' + spov

            home_payout = rnd_dec(payouts[i][order[0]], dec)
            away_payout = rnd_dec(payouts[i][order[1]], dec)
            markets.append((market_id, sportsbook, matchup, bet_type, period, 
                            date, home, away, home_payout, away_payout, spun, 
                            spov))
    return markets

if __name__ == '__main__':
    main()