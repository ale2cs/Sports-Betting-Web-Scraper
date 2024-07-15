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
        pinnacle_games, pinnacle_markets, pinnacle_lines = await get_pinacle()
        add_games(conn, pinnacle_games)  # initalize games
        add_markets(conn, pinnacle_markets)  # initlaize markets
        add_lines(conn, pinnacle_lines)
        bodog_lines = await get_bodog()
        add_lines(conn, bodog_lines)
        sports_interaction_lines = await get_sports_interaction()
        add_lines(conn, sports_interaction_lines)
        # bet99 = await get_bet99()
        # add_lines(conn, bet99)
        # eights_sport = await get_888sport()
        # add_lines(conn, eights_sport)

        current_time = datetime.now()
        time_format = "%H:%M:%S"  # Example format: HH:MM:SS
        formatted_time = current_time.strftime(time_format)
        # clear_terminal()
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
        done = True
        if not done:
            time.sleep(60)

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
    create_games = """
        CREATE TABLE IF NOT EXISTS games (
            game_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            sport TEXT NOT NULL,
            league TEXT NOT NULL,
            name TEXT NOT NULL, 
            date TEXT NOT NULL, 
            home_team TEXT NOT NULL, 
            away_team TEXT NOT NULL, 
            CONSTRAINT unique_game UNIQUE (sport, league, name, date, home_team, away_team)
        );
    """
    create_markets = """
        CREATE TABLE IF NOT EXISTS markets (
            market_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY, 
            game_id INT NOT NULL,
            type TEXT NOT NULL,
            period SMALLINT NOT NULL, 
            spov TEXT NOT NULL, 
            spun TEXT NOT NULL,
            CONSTRAINT fk_game_id
                FOREIGN KEY (game_id)
                REFERENCES games(game_id)
                ON DELETE CASCADE,
            CONSTRAINT unique_market UNIQUE (game_id, type, period, spov, spun)
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
    cur.execute(create_games)
    cur.execute(create_markets)
    cur.execute(create_lines)
    conn.commit()


def add_games(conn, games):
    cur = conn.cursor()
    # https://stackoverflow.com/questions/63720340/postgres-prevent-serial-incrementation-with-on-conflict-do-nothing?noredirect=1&lq=1
    insert = """
        /* Only insert records that are not in games. Replaced INSERT ON 
        CONFLICT IGNORE query since it causes SERIAL/IDENTITY to increment while 
        attempting to inserting existing records. Scraping frequently causes the
        primary key to increase rapidly and introduces gaps whiile using INSERT 
        ON CONFLICT IGNORE. Query being used fixes these problems by only 
        inserting new records without incrementing SERIAL/IDENTITY.*/
        WITH new_games (sport, league, name, date, home_team, away_team) AS (
            VALUES %s
		),
		indexed_new_games AS (
			SELECT ROW_NUMBER() OVER () AS row_id, I.*
			FROM new_games I
		),
		duplicates AS (
			SELECT N.row_id
			FROM indexed_new_games N
            WHERE EXISTS (
                SELECT 1
                FROM games G
                WHERE N.name = G.name
                AND N.sport = G.sport
                AND N.league = G.league
                AND N.date = G.date
                AND N.home_team = G.home_team
                AND N.away_team = G.away_team
            )
		),
		ins AS (
			SELECT N.*
			FROM indexed_new_games AS N
			LEFT JOIN duplicates AS D ON N.row_id = D.row_id
			WHERE D.row_id IS NULL
		)
		INSERT INTO games (sport, league, name, date, home_team, away_team)
        SELECT DISTINCT sport, league, name, date, home_team, away_team
       	FROM ins
    """
    execute_values(cur, insert, games)
    conn.commit()
    return cur.lastrowid

def add_markets(conn, markets):
    cur = conn.cursor()
    # https://stackoverflow.com/questions/63720340/postgres-prevent-serial-incrementation-with-on-conflict-do-nothing?noredirect=1&lq=1
    insert = """
        /* Only insert records that are not in markets. Replaced INSERT ON 
        CONFLICT IGNORE query since it causes SERIAL/IDENTITY to increment while 
        attempting to inserting existing records. Scraping frequently causes the
        primary key to increase rapidly and introduces gaps whiile using INSERT 
        ON CONFLICT IGNORE. Query being used fixes these problems by only 
        inserting new records without incrementing SERIAL/IDENTITY.*/
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
                FROM games AS G
                JOIN markets AS M ON G.game_id = M.game_id     
                WHERE N.name = G.name
                AND N.type = M.type
                AND N.period = M.period
                AND N.date = G.date
                AND N.sport = G.sport
                AND N.league = G.league
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
        INSERT INTO markets (game_id, type, period, spov, spun)
        SELECT
            (SELECT game_id 
            FROM games AS G
            WHERE G.name = I.name 
            AND G.sport = I.sport 
            AND G.league = I.league 
            AND G.date = I.date
            ), 
            I.type, I.period, I.spov, I.spun
        FROM ins AS I;
    """
    execute_values(cur, insert, markets)
    conn.commit()
    return cur.lastrowid

def add_lines(conn, lines):
    cur = conn.cursor()
    upsert = """
        /*Inserts records when they don't exist in lines or when the odds change 
        for those lines. If the records do exist in lines but the odds are the 
        same, the records will be updated on their updated_at columns to the
        current time. This query is used over a query like INSERT ON CONFLICT
        DO UPDATE since keeping track of the history of odds for each line is 
        important.*/
        CREATE TEMP TABLE vals (sport, league, name, type, period, date, spov, spun, sportsbook, home_odds, away_odds) AS (
            VALUES %s 
		);
        CREATE TEMP TABLE recent_lines AS (
            SELECT Max(line_id) AS line_id
            FROM lines
            GROUP BY market_id, sportsbook
        );
		CREATE TEMP TABLE proper_vals AS (
        	SELECT M.market_id, V.sportsbook, V.home_odds, V.away_odds
        	FROM games AS G
            JOIN vals AS V ON G.name = V.name
            JOIN markets AS M ON G.game_id = M.game_id
            WHERE G.sport = V.sport
            AND G.league = V.league
            AND M.type = V.type
        	AND M.period = V.period
            AND ABS(EXTRACT(EPOCH FROM AGE(
            	TO_TIMESTAMP(G.date, 'YYYY-MM-DD"T"HH24:MI:SS"Z"'), 
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
    execute_values(cur, upsert, lines)
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
        SELECT G.name, M.type, M.period, G.date, M.spov, M.spun, G.home_team, G.away_team,
            L1.sportsbook, L1.home_odds, L1.away_odds,
            L2.sportsbook AS sportsbook_2, L2.home_odds AS home_odds_2, L2.away_odds AS away_odds_2
        FROM recent_line AS L1
        JOIN recent_line AS L2 ON L1.market_id = L2.market_id 
        JOIN markets AS M ON L1.market_id = M.market_id
        JOIN games AS G ON G.game_id = M.game_id
        WHERE L1.sportsbook = 'Pinnacle'
        AND L1.sportsbook <> L2.sportsbook
        AND (L2.home_odds > ((L1.home_odds + L1.away_odds) / L1.away_odds)
            OR L2.away_odds > ((L1.home_odds + L1.away_odds) / L1.home_odds))
        AND TO_TIMESTAMP(G.date, 'YYYY-MM-DD"T"HH24:MI:SS"Z"') > NOW() AT TIME ZONE 'UTC'
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
