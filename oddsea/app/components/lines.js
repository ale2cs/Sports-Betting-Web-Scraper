const React = require("react");
const { cache, use } = require("react");

const getLines = cache(() =>
  fetch("http://localhost:3000/api/lines", { cache:'no-store' }).then((res) => res.json())
)

export default function ListLines() {
  let lines = use(getLines());

  return (
    <div>
      {lines.map((line) => (
        <div key={line.line_id}>
          <h3>
            {line.line_id} {line.market_id} {line.sportsbook} {line.home_odds} {line.away_odds}
          </h3>
        </div>
      ))}
    </div>
  );
}

