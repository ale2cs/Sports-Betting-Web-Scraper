import prisma from "../../models/prisma.js";

const impliedProbability = (odds, odds2) => {
  return [odds2 / (odds + odds2), odds / (odds + odds2)];
};

const ev = (winProbability, odds) => {
  return winProbability * (odds - 1) + winProbability - 1;
};

export async function getPositiveEV() {
  const positiveLines = await prisma.$queryRaw`
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
    SELECT L2.line_id, M.market_id, 'home' AS bet_type, M.sport, M.league, M.name, M.type, M.period, M.date, M.spov AS sp, M.home_team AS team,
        L1.home_odds, L1.away_odds,
        L2.sportsbook AS sportsbook, L2.home_odds AS odds
    FROM recent_line AS L1
    JOIN recent_line AS L2 ON L1.market_id = L2.market_id 
    JOIN markets AS M ON L1.market_id = M.market_id
    WHERE L1.sportsbook = 'Pinnacle'
    AND L1.sportsbook <> L2.sportsbook
    AND L2.home_odds > ((L1.home_odds + L1.away_odds) / L1.away_odds)
    AND TO_TIMESTAMP(M.date, 'YYYY-MM-DD"T"HH24:MI:SS"Z"') > NOW() AT TIME ZONE 'UTC'
    UNION
    SELECT L2.line_id, M.market_id, 'away' AS bet_type, M.sport, M.league, M.name, M.type, M.period, M.date, M.spun AS sp, M.away_team AS team,
            L1.home_odds, L1.away_odds,
        L2.sportsbook AS sportsbook, L2.away_odds AS odds
    FROM recent_line AS L1
    JOIN recent_line AS L2 ON L1.market_id = L2.market_id 
    JOIN markets AS M ON L1.market_id = M.market_id
    WHERE L1.sportsbook = 'Pinnacle'
    AND L1.sportsbook <> L2.sportsbook
    AND L2.away_odds > ((L1.home_odds + L1.away_odds) / L1.home_odds)
    AND TO_TIMESTAMP(M.date, 'YYYY-MM-DD"T"HH24:MI:SS"Z"') > NOW() AT TIME ZONE 'UTC'
    `;
  const calc = positiveLines.map((item) => {
    const [homeProbability, awayProbability] = impliedProbability(
      item.home_odds,
      item.away_odds
    );
    const team = item.team;
    const spread = item.sp;
    const odds = item.odds.toFixed(2);
    if (item.bet_type === "home") {
      return {
        ...item,
        ev: `${(ev(homeProbability, item.odds) * 100).toFixed(2)}%`,
        bet:
          item.type === "total"
            ? `Over ${spread} @ ${odds}`
            : item.type === "spread"
            ? `${spread} ${team} @ ${odds}`
            : `${team} @ ${odds}`,
      };
    } else {
      return {
        ...item,
        ev: `${(ev(awayProbability, item.odds) * 100).toFixed(2)}%`,
        bet:
          item.type === "total"
            ? `Under ${spread} @ ${odds}`
            : item.type === "spread"
            ? `${spread} ${team} @ ${odds}`
            : `${team} @ ${odds}`,
      };
    }
  });
  return calc;
}