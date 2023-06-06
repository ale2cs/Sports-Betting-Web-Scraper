import sqlite3
from sqlite3 import Error
from datetime import datetime, timezone
import time
import os

from sportbooks.utils import *
from sportbooks.bet99 import get_bet99
from sportbooks.pinnacle import get_pinacle
from sportbooks.sports_interaction import get_sports_interaction
from sportbooks.bodog import get_bodog

def main():
    database = "./odds.db"

    # create a database connection
    conn = create_conn(database)

    # create table if not already made
    create_table(conn)

    while True:
        # remove old markets
        remove_old_markets(conn)

        # add and update new markets
        add_markets(conn, get_pinacle())
        add_markets(conn, get_sports_interaction())
        add_markets(conn, get_bet99())
        add_markets(conn, get_bodog())

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

def create_conn(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def create_table(conn):
    cur = conn.cursor()
    create = '''
        CREATE TABLE IF NOT EXISTS markets 
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
    upsert = '''
        INSERT INTO markets 
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
    cur = conn.cursor()
    remove_old = '''
        DELETE FROM markets
        WHERE date < ?
    '''
    cur_date = datetime.now(timezone.utc).isoformat()
    cur.execute(remove_old, (cur_date,))
    conn.commit()

    return cur.lastrowid

def positive_ev(conn):
    find_markets = '''
        SELECT M1.game, M1.type, M1.period, M1.date, M1.spov, M1.spun, 
            M1.home_team, M1.away_team, M1.sportsbook, M1.home_payout, 
            M1.away_payout, M2.sportsbook, M2.home_payout, M2.away_payout 
        From markets AS M1, markets AS M2
        WHERE M1.sportsbook = "Pinnacle" 
        AND M1.sportsbook <> M2.sportsbook
        AND M1.game = M2.game 
        AND M1.type = M2.type 
        AND M1.period = M2.period
        AND M1.spov = M2.spov 
        AND M1.spun = M2.spun 
        AND M1.home_team = M2.home_team 
        AND M1.away_team = M2.away_team 
        AND (abs(julianday(M1.date) - julianday(M2.date)) * 24 * 60) < 60 
        AND ((M2.home_payout > ((M1.home_payout + M1.away_payout) / M1.away_payout))
        OR (M2.away_payout > ((M1.home_payout + M1.away_payout) / M1.home_payout)))'''
    cur = conn.cursor() 
    return cur.execute(find_markets)


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
    main()