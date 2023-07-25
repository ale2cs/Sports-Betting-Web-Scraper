import asyncio
import psycopg2
from sqlite3 import Error
from datetime import datetime, timezone
import time
import os
import importlib

from sportbooks.utils import *
from sportbooks.bet99 import get_bet99
from sportbooks.pinnacle import get_pinacle
from sportbooks.sports_interaction import get_sports_interaction
from sportbooks.bodog import get_bodog
triple_eight_sport = importlib.import_module('sportbooks.888sport')
get_888sport = getattr(triple_eight_sport, 'get_888sport')

async def main():
    # create a database connection
    conn = create_conn()

    # create table if not already made
    create_tables(conn)

    done = False
    while not done:
        # add new markets
        pinacle_markets, pinacle_lines= await get_pinacle()
        add_markets(conn, pinacle_markets)  #initlaize markets
        add_lines(conn, pinacle_lines)
        # bet99 = await get_bet99()
        # add_lines(conn, bet99)
        bodog = await get_bodog()
        add_lines(conn, bodog)
        # eights_sport = await get_888sport()
        # add_lines(conn, eights_sport)
        sports_interaction = get_sports_interaction()
        add_lines(conn, sports_interaction)

        current_time = datetime.now()
        time_format = "%H:%M:%S"  # Example format: HH:MM:SS
        formatted_time = current_time.strftime(time_format)
        clear_terminal()
        print(f"---------- {formatted_time} ----------\n")

        for market in positive_ev(conn):
            if over_max_hours(market[3], 2):
                continue
            stats = MarketStats(market[9], market[10], market[12], market[13])
            bet_type = market[1]
            if stats.home_bet:
                payout = stats.home_payout
                home_away = "home"
            else:
                payout = stats.away_payout
                home_away = "away" 
            if stats.pos_ev < 0.5:
                continue
            print(market) 
            print((home_away, payout), f"Vig:{stats.vig}%", f"EV:{stats.pos_ev}%", f"Wager:${stats.bet_amount}", f"RemTime:{rem_time(market[3])}")
            print('')

        time.sleep(60)

def create_conn():
    conn = None
    try:
        conn = psycopg2.connect(host="localhost", dbname="odds", user="postgres", port=5432)
    except Error as e:
        print(e)

    return conn

def create_tables(conn):
    cur = conn.cursor()
    create_markets = '''
        CREATE TABLE IF NOT EXISTS markets (
            market_id BIGSERIAL PRIMARY KEY, 
            name TEXT, 
            type TEXT,
            period INT, 
            date TEXT, 
            home_team TEXT, 
            away_team TEXT, 
            spov TEXT, 
            spun TEXT,
            CONSTRAINT unique_market UNIQUE (name, type, period, spov, spun)
        )
    '''
    create_lines = '''
        CREATE TABLE IF NOT EXISTS lines (
            line_id BIGSERIAL PRIMARY KEY,
            market_id INT NOT NULL REFERENCES markets,
            sportsbook TEXT,
            home_odds FLOAT,
            away_odds FLOAT,
            created_at TEXT
        )
    '''
    # CONSTRAINT unique_line UNIQUE (market_id, sportsbook, home_odds, away_odds)
    cur.execute(create_markets)
    cur.execute(create_lines)
    conn.commit()

def add_markets(conn, markets):
    cur = conn.cursor()
    insert = """
        INSERT INTO markets (name, type, period, date, home_team, away_team, spov, spun)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """
    cur.executemany(insert, markets)
    conn.commit()
    return cur.lastrowid

def add_lines(conn, lines):
    cur = conn.cursor()
    insert = """
        WITH recent_lines AS (
			SELECT L2.*
			FROM (
            	SELECT Max(line_id) AS line_id
            	FROM lines
            	GROUP BY market_id, sportsbook
			) AS L1
			JOIN lines AS L2
			ON L1.line_id = L2.line_id
        )
        SELECT M.name, M.type, M.period, M.date, M.spov, M.spun, M.home_team, M.away_team,
            L1.sportsbook, L1.home_odds, L1.away_odds,
            L2.sportsbook AS sportsbook_2, L2.home_odds AS home_odds_2, L2.away_odds AS away_odds_
        FROM recent_lines AS L1
        JOIN recent_lines AS L2 ON L1.market_id = L2.market_id
        AND L1.sportsbook = 'Pinnacle'
        AND L1.sportsbook <> L2.sportsbook
        AND (L2.home_odds > ((L1.home_odds + L1.away_odds) / L1.away_odds)
            OR L2.away_odds > ((L1.home_odds + L1.away_odds) / L1.home_odds))
        JOIN markets AS M ON L1.market_id = M.market_id
        WHERE TO_TIMESTAMP(M.date, 'YYYY-MM-DD"T"HH24:MI:SS"Z"') > NOW() 
    """
    cur.executemany(insert, lines)
    conn.commit()

def positive_ev(conn):
    positive_ev = '''
        WITH recent_lines AS (
            SELECT market_id, sportsbook, MAX(line_id) AS line_id
            FROM lines
            WHERE TO_TIMESTAMP(created_at, 'YYYY-MM-DD"T"HH24:MI:SS"Z"') > (NOW() - INTERVAL '2 minute')
            GROUP BY market_id, sportsbook
        ),
        data_lines AS (
            SELECT L2.line_id, L2.market_id, L2.sportsbook, L2.home_odds, L2.away_odds
            FROM recent_lines AS L1
            JOIN lines AS L2 ON L1.line_id = L2.line_id
        )
        SELECT M.name, M.type, M.period, M.date, M.spov, M.spun, M.home_team, M.away_team,
            L1.sportsbook, L1.home_odds, L1.away_odds,
            L2.sportsbook AS sportsbook_2, L2.home_odds AS home_odds_2, L2.away_odds AS away_odds_
        FROM data_lines AS L1
        JOIN data_lines AS L2 ON L1.market_id = L2.market_id
        AND L1.sportsbook = 'Pinnacle'
        AND L1.sportsbook <> L2.sportsbook
        AND (L2.home_odds > ((L1.home_odds + L1.away_odds) / L1.away_odds)
            OR L2.away_odds > ((L1.home_odds + L1.away_odds) / L1.home_odds))
        JOIN markets AS M ON L1.market_id = M.market_id
        WHERE TO_TIMESTAMP(M.date, 'YYYY-MM-DD"T"HH24:MI:SS"Z"') > NOW() 
    '''
    cur = conn.cursor()
    cur.execute(positive_ev)
    return cur.fetchall()


def clear_terminal():
    # Check the operating system and execute the appropriate command
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For UNIX/Linux/Mac
        os.system('clear')

class MarketStats:
    def __init__(self, pin_home_payout, pin_away_payout, home_payout, away_payout):
        self.bankroll = 10000
        self.percent_kelly = 0.3
        self.dec = 2
        self.pin_home_payout = pin_home_payout
        self.pin_away_payout = pin_away_payout
        self.home_payout = home_payout
        self.away_payout = away_payout
        self.vig = self.vig()
        self.home_prob, self.away_prob = self.imp_prob()
        self.home_ev, self.away_ev = self.ev()
        self.home_bet = self.is_home_bet()
        self.pos_ev = self.pos_ev()
        self.bet_amount = self.wager()

    def imp_prob(self):
        denominator = (self.pin_home_payout + self.pin_away_payout)
        return (self.pin_away_payout / denominator), (self.pin_home_payout / denominator)

    def vig(self):
        return rnd_dec(((1 / self.pin_home_payout) + (1 / self.pin_away_payout) - 1) * 100, self.dec)

    def no_vig_odds(self): 
        return (1 / self.home_prob), (1 / self.away_prob) 

    def ev(self):
        home_ev = rnd_dec(((self.home_prob * (self.home_payout - 1)) + self.home_prob - 1) * 100, self.dec)
        away_ev = rnd_dec(((self.away_prob * (self.away_payout - 1)) + self.away_prob - 1) * 100, self.dec)
        return home_ev, away_ev 

    def is_home_bet(self): 
        return self.home_ev > self.away_ev

    def pos_ev(self):
        return self.home_ev if self.home_bet else self.away_ev

    def kelly_criterion(self):
        if self.home_bet:
            return self.home_prob - ((1 - self.home_prob) / (self.home_payout - 1))
        return self.away_prob - ((1 - self.away_prob) / (self.away_payout - 1))

    def wager(self): 
        kelly = self.kelly_criterion()
        return rnd_dec(self.percent_kelly * kelly * self.bankroll, self.dec)
    


if __name__ == '__main__':
    asyncio.run(main())