-- CreateTable
CREATE TABLE "lines" (
    "line_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "market_id" INTEGER,
    "sportsbook" TEXT,
    "home_odds" REAL,
    "away_odds" REAL,
    "date_created" TEXT
);

-- CreateTable
CREATE TABLE "markets" (
    "market_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" TEXT,
    "type" TEXT,
    "period" TEXT,
    "date" TEXT,
    "home_team" TEXT,
    "away_team" TEXT,
    "spov" TEXT,
    "spun" TEXT
);

-- CreateIndex
Pragma writable_schema=1;
CREATE UNIQUE INDEX "sqlite_autoindex_markets_1" ON "markets"("name", "type", "period", "spov", "spun");
Pragma writable_schema=0;

