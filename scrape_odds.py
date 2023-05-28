import requests
import cloudscraper
import sqlite3
import jmespath
from sqlite3 import Error
from datetime import datetime, timezone
import math

def main():
    database = "./odds.db"

    # create a database connection
    conn = create_conn(database)

    # create table if not already made
    create_table(conn)

    # remove old markets
    remove_old_markets(conn)

    # add and update new markets
    # add_markets(conn, get_sports_int())
    # add_markets(conn, get_bet99())

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
    remove_old = '''DELETE FROM markets
                    WHERE date < ?
                 '''
    cur_date = datetime.now(timezone.utc).isoformat()
    cur.execute(remove_old, (cur_date,))
    conn.commit()

    return cur.lastrowid


if __name__ == '__main__':
    main()