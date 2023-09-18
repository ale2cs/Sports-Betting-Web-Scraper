import asyncio
import psycopg2
from psycopg2.extras import execute_values
from sqlite3 import Error
from datetime import datetime
import time
import os
import importlib
from dotenv import load_dotenv

load_dotenv()
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_port = os.getenv("DB_PORT")

from utils.calcs import *
from utils.dates import *
from sportsbooks.bet99 import get_bet99
from sportsbooks.pinnacle import get_pinacle
from sportsbooks.sports_interaction import get_sports_interaction
from sportsbooks.bodog import get_bodog
triple_eight_sport = importlib.import_module('sportsbooks.888sport')
get_888sport = getattr(triple_eight_sport, 'get_888sport')

async def main():
    # create a database connection
    conn = create_conn()

    # create table if not already made
    create_tables(conn)

    done = False
    while not done:
        pinnacle_markets, pinnacle_lines= await get_pinacle()
        add_markets(conn, pinnacle_markets)  # initlaize markets
        add_lines(conn, pinnacle_lines)
        bet99 = await get_bet99()
        add_lines(conn, bet99)
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
        time.sleep(10)

def create_conn():
    conn = None
    try:
        conn = psycopg2.connect(
            host = db_host, 
            dbname = db_name, 
            user = db_user, 
            password = db_password,
            port = db_port
        )
    except Error as e:
        print(e)

    return conn

def create_tables(conn):
    cur = conn.cursor()
    create_markets = """
        CREATE TABLE IF NOT EXISTS markets (
            market_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY, 
            sport TEXT NOT NULL,
            league TEXT NOT NULL,
            name TEXT NOT NULL, 
            type TEXT NOT NULL,
            period SMALLINT NOT NULL, 
            date TEXT NOT NULL, 
            home_team TEXT NOT NULL, 
            away_team TEXT NOT NULL, 
            spov TEXT NOT NULL, 
            spun TEXT NOT NULL,
            CONSTRAINT unique_market UNIQUE (name, type, period, date, spov, spun)
        )
    """
    create_lines = """
        CREATE TABLE IF NOT EXISTS lines (
            line_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            market_id INT NOT NULL,
            sportsbook TEXT NOT NULL,
            home_odds FLOAT NOT NULL,
            away_odds FLOAT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TExT NOT NULL,
            CONSTRAINT fk_market_id
                FOREIGN KEY (market_id)
                REFERENCES markets(market_id)
                ON DELETE CASCADE
        )
    """
    create_lines2 = """
        CREATE TABLE IF NOT EXISTS lines (
            line_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            market_id INT NOT NULL,
            sportsbook TEXT NOT NULL,
            home_odds FLOAT NOT NULL,
            away_odds FLOAT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TExT NOT NULL,
            CONSTRAINT unique_line UNIQUE (market_id, sportsbook),
            CONSTRAINT fk_market_id
                FOREIGN KEY (market_id)
                REFERENCES markets(market_id)
                ON DELETE CASCADE
        )
    
    """
    cur.execute(create_markets)
    cur.execute(create_lines)
    conn.commit()

def add_markets(conn, markets):
    cur = conn.cursor()
    # https://stackoverflow.com/questions/63720340/postgres-prevent-serial-incrementation-with-on-conflict-do-nothing?noredirect=1&lq=1
    insert = """
        INSERT INTO markets (sport, league, name, type, period, date, home_team, away_team, spov, spun)
        SELECT sport, league, name, type, period, date, home_team, away_team, spov, spun
        FROM (
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ) AS M1 (sport, league, name, type, period, date, home_team, away_team, spov, spun)
        WHERE NOT EXISTS (
            SELECT 1
            FROM markets M2
            WHERE M1.name = M2.name
            AND M1.type = M2.type
            AND M1.period = M2.period
            AND M1.date = M2.date
            AND M1.spov = M2.spov
            AND M1.spun = M2.spun
        )
    """
    insert2 = """
        INSERT INTO markets (sport, league, name, type, period, date, home_team, away_team, spov, spun)
        VALUES %s
        ON CONFLICT
        DO NOTHING
    """
    insert3 = """
        WITH new_markets (sport, league, name, type, period, date, home_team, away_team, spov, spun) AS (
            VALUES %s
		),
		indexed_new_markets AS (
			SELECT ROW_NUMBER() OVER () AS row_id, I.*
			FROM new_markets I
		),
		duplicates AS (
			SELECT N.row_id
			FROM indexed_new_markets N
            WHERE EXISTS (
                SELECT 1
                FROM markets M
                WHERE N.name = M.name
                AND N.type = M.type
                AND N.period = M.period
                AND N.date = M.date
                AND N.spov = M.spov
                AND N.spun = M.spun
            )
		),
		ins AS (
			SELECT N.*
			FROM indexed_new_markets AS N
			LEFT JOIN duplicates AS D ON N.row_id = D.row_id
			WHERE D.row_id IS NULL
		)
		INSERT INTO markets (sport, league, name, type, period, date, home_team, away_team, spov, spun)
        SELECT sport, league, name, type, period, date, home_team, away_team, spov, spun
       	FROM ins
    """
    execute_values(cur, insert3, markets)
    conn.commit()
    return cur.lastrowid

def add_lines(conn, lines):
    cur = conn.cursor()
    insert = """
        WITH market AS (
            SELECT market_id
            FROM markets
            WHERE name = %(matchup)s
            AND type = %(bet_type)s
            AND period = %(period)s
            AND ABS(EXTRACT(EPOCH FROM AGE(
                TO_TIMESTAMP(date, 'YYYY-MM-DD"T"HH24:MI:SS"Z"'), 
                TO_TIMESTAMP(%(date)s, 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
            ))) / 3600 < 1
            AND spov = %(spov)s
            AND spun = %(spun)s
        ),
        recent_lines AS (
            SELECT Max(line_id) AS line_id
            	FROM lines
            	GROUP BY market_id, sportsbook
        ),
        recent_line AS (
			SELECT L2.*
			FROM market M, recent_lines L1
			JOIN lines AS L2 ON L1.line_id = L2.line_id
            WHERE L2.market_id = M.market_id 
            AND L2.sportsbook = %(sportsbook)s
        ),
        updated_row AS (
            UPDATE lines L1
            SET updated_at = TO_CHAR(NOW() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
            FROM recent_line AS L2
            WHERE L1.line_id = L2.line_id
            AND L1.home_odds = %(home_odds)s
            AND L1.away_odds = %(away_odds)s
            RETURNING *
        )
        INSERT INTO lines (market_id, sportsbook, home_odds, away_odds, created_at, updated_at) 
        SELECT M.market_id, %(sportsbook)s, %(home_odds)s, %(away_odds)s, 
            TO_CHAR(NOW() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'), 
            TO_CHAR(NOW() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
        FROM market M
        WHERE NOT EXISTS (
            SELECT 1
            FROM updated_row
        )
    """
    insert2 = """
        WITH vals (name, type, period, date, spov, spun, sportsbook, home_odds, away_odds) AS (
            VALUES %s 
        ),
        recent_lines AS (
            SELECT Max(line_id) AS line_id
            	FROM lines
            	GROUP BY market_id, sportsbook
        ),
        upd AS (
            SELECT M.market_id, V.sportsbook, V.home_odds, V.away_odds
            UPDATE lines L
            SET updated_at = TO_CHAR(NOW() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
            FROM vals AS V
            WHERE L.name = V.name
            AND L.type = V.type
            AND L.period = V.period
            AND L.spov = V.spov
            AND L.spun = V.spun
        )
        INSERT INTO lines (market_id, sportsbook, home_odds, away_odds, created_at, updated_at) 
        SELECT M.market_id, L.sportsbook, L.home_odds, L.away_odds, 
            TO_CHAR(NOW() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'), 
            TO_CHAR(NOW() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
        FROM markets AS M JOIN ins AS L 
        ON M.name = L.name
        AND M.type = L.type
        AND M.period = L.period
        AND M.spov = L.spov
        AND M.spun = L.spun
        INSERT INTO lines (market_id, sportsbook, home_odds, away_odds, created_at, updated_at) 
        SELECT V.market_id, V.sportsbook, V.home_odds, V.away_odds, 
            TO_CHAR(NOW() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'), 
            TO_CHAR(NOW() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
		FROM upd AS U
        LEFT JOIN proper_vals AS V ON V.market_id = U.market_id
		WHERE V.market_id IS NULL
		RETURNING *
    """
    insert3 = """
        WITH vals (name, type, period, date, spov, spun, sportsbook, home_odds, away_odds) AS (
            VALUES %s
		),
        recent_lines AS (
            SELECT Max(line_id) AS line_id
            FROM lines
            GROUP BY market_id, sportsbook
        ),
		proper_vals AS (
        	SELECT M.market_id, V.sportsbook, V.home_odds, V.away_odds
        	FROM markets AS M JOIN vals AS V
        	ON M.name = V.name
        	AND M.type = V.type
        	AND M.period = V.period
            AND ABS(EXTRACT(EPOCH FROM AGE(
            	TO_TIMESTAMP(M.date, 'YYYY-MM-DD"T"HH24:MI:SS"Z"'), 
            	TO_TIMESTAMP(V.date, 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
            ))) / 3600 < 1
        	AND M.spov = V.spov
        	AND M.spun = V.spun
		),
		upd AS (
            UPDATE lines L1
            SET updated_at = TO_CHAR(NOW() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
            FROM recent_lines L2, proper_vals AS P
            WHERE L1.line_id = L2.line_id
			AND L1.market_id = P.market_id
			AND L1.home_odds = P.home_odds::double precision
            AND L1.away_odds = P.away_odds::double precision 
			RETURNING P.*
        ),
		ins AS (
			SELECT P.*
			FROM proper_vals AS P
			LEFT JOIN upd AS U ON P.market_id = U.market_id
			WHERE U.market_id IS NULL
		)
		INSERT INTO lines (market_id, sportsbook, home_odds, away_odds, created_at, updated_at) 
        SELECT I.market_id, I.sportsbook, I.home_odds::double precision, I.away_odds::double precision, 
            TO_CHAR(NOW() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'), 
            TO_CHAR(NOW() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
		FROM ins I
    """
    insert4 = """
        WITH vals (name, type, period, date, spov, spun, sportsbook, home_odds, away_odds) AS (
            VALUES %s
		),
        proper_vals AS (
        	SELECT M.market_id, V.sportsbook, V.home_odds, V.away_odds
        	FROM markets AS M JOIN vals AS V
        	ON M.name = V.name
        	AND M.type = V.type
        	AND M.period = V.period
            AND ABS(EXTRACT(EPOCH FROM AGE(
            	TO_TIMESTAMP(M.date, 'YYYY-MM-DD"T"HH24:MI:SS"Z"'), 
            	TO_TIMESTAMP(V.date, 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
            ))) / 3600 < 1
        	AND M.spov = V.spov
        	AND M.spun = V.spun
		)
		INSERT INTO lines (market_id, sportsbook, home_odds, away_odds, created_at, updated_at) 
        SELECT market_id, sportsbook, home_odds, away_odds,
            TO_CHAR(NOW() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'), 
            TO_CHAR(NOW() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
        FROM proper_vals
        ON CONFLICT (market_id, sportsbook) DO  
        UPDATE SET 
            updated_at = TO_CHAR(NOW() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'),
            home_odds = excluded.home_odds,
            away_odds = excluded.away_odds
    """
    insert5 = """
        CREATE TEMP TABLE vals (name, type, period, date, spov, spun, sportsbook, home_odds, away_odds) AS (
            VALUES %s 
		);
        CREATE TEMP TABLE recent_lines AS (
            SELECT Max(line_id) AS line_id
            FROM lines
            GROUP BY market_id, sportsbook
        );
		CREATE TEMP TABLE proper_vals AS (
        	SELECT M.market_id, V.sportsbook, V.home_odds, V.away_odds
        	FROM markets AS M JOIN vals AS V
        	ON M.name = V.name
        	AND M.type = V.type
        	AND M.period = V.period
            AND ABS(EXTRACT(EPOCH FROM AGE(
            	TO_TIMESTAMP(M.date, 'YYYY-MM-DD"T"HH24:MI:SS"Z"'), 
            	TO_TIMESTAMP(V.date, 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
            ))) / 3600 < 1
        	AND M.spov = V.spov
        	AND M.spun = V.spun
		);
		CREATE TEMP TABLE upd AS (
			WITH up AS (
            UPDATE lines L1
            SET updated_at = TO_CHAR(NOW() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
            FROM recent_lines L2, proper_vals AS P
            WHERE L1.line_id = L2.line_id
			AND L1.market_id = P.market_id
			AND L1.home_odds = P.home_odds::double precision
            AND L1.away_odds = P.away_odds::double precision 
			RETURNING P.market_id
			)
			SELECT *
			FROM up
        );
		CREATE INDEX upd_market_id_idx ON upd (market_id);
		CREATE TEMP TABLE ins AS (
			SELECT P.*
			FROM proper_vals AS P
			LEFT JOIN upd AS U ON P.market_id = U.market_id
			WHERE U.market_id IS NULL
		);

		INSERT INTO lines (market_id, sportsbook, home_odds, away_odds, created_at, updated_at) 
        SELECT I.market_id, I.sportsbook, I.home_odds::double precision, I.away_odds::double precision, 
            TO_CHAR(NOW() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'), 
            TO_CHAR(NOW() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
		FROM ins I;

		DROP TABLE IF EXISTS vals;
        DROP TABLE IF EXISTS recent_lines;
		DROP TABLE IF EXISTS proper_vals;
		DROP TABLE IF EXISTS upd;
		DROP TABLE IF EXISTS ins;
    """
    # cur.executemany(insert, lines)
    execute_values(cur, insert5, lines)
    conn.commit()

def positive_ev(conn):
    positive_ev = """
        WITH recent_line AS (
			SELECT L2.*
			FROM (
            	SELECT Max(line_id) AS line_id
            	FROM lines
                WHERE ABS(EXTRACT(EPOCH FROM AGE(
                    TO_TIMESTAMP(updated_at, 'YYYY-MM-DD"T"HH24:MI:SS"Z"'), NOW() AT TIME ZONE 'UTC'
                ))) / 60 < 2
            	GROUP BY market_id, sportsbook
			) AS L1
			JOIN lines AS L2
			ON L1.line_id = L2.line_id
        )
        SELECT M.name, M.type, M.period, M.date, M.spov, M.spun, M.home_team, M.away_team,
            L1.sportsbook, L1.home_odds, L1.away_odds,
            L2.sportsbook AS sportsbook_2, L2.home_odds AS home_odds_2, L2.away_odds AS away_odds_2
        FROM recent_line AS L1
        JOIN recent_line AS L2 ON L1.market_id = L2.market_id 
        JOIN markets AS M ON L1.market_id = M.market_id
        WHERE L1.sportsbook = 'Pinnacle'
        AND L1.sportsbook <> L2.sportsbook
        AND (L2.home_odds > ((L1.home_odds + L1.away_odds) / L1.away_odds)
            OR L2.away_odds > ((L1.home_odds + L1.away_odds) / L1.home_odds))
        AND TO_TIMESTAMP(M.date, 'YYYY-MM-DD"T"HH24:MI:SS"Z"') > NOW() AT TIME ZONE 'UTC'
    """
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