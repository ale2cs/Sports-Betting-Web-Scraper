-- CreateTable
CREATE TABLE "lines" (
    "line_id" BIGSERIAL NOT NULL,
    "market_id" BIGINT NOT NULL,
    "sportsbook" TEXT NOT NULL,
    "home_odds" DOUBLE PRECISION NOT NULL,
    "away_odds" DOUBLE PRECISION NOT NULL,
    "created_at" TEXT NOT NULL,

    CONSTRAINT "lines_pkey" PRIMARY KEY ("line_id")
);

-- CreateTable
CREATE TABLE "markets" (
    "market_id" BIGSERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "period" SMALLINT NOT NULL,
    "date" TEXT NOT NULL,
    "home_team" TEXT NOT NULL,
    "away_team" TEXT NOT NULL,
    "spov" TEXT NOT NULL,
    "spun" TEXT NOT NULL,

    CONSTRAINT "markets_pkey" PRIMARY KEY ("market_id")
);

-- CreateIndex
CREATE UNIQUE INDEX "unique_market" ON "markets"("name", "type", "period", "spov", "spun");

-- AddForeignKey
ALTER TABLE "lines" ADD CONSTRAINT "fk_market_id" FOREIGN KEY ("market_id") REFERENCES "markets"("market_id") ON DELETE CASCADE ON UPDATE NO ACTION;

