const React = require("react");
const { cache, use } = require("react");

const getMarkets = () => (
  fetch("http://localhost:3000/api/markets", { cache:'no-store' }).then((res) => res.json())
);

export default function ListMarkets() {
  let markets = use(getMarkets());

  return (
    <div>
      {markets.map((market) => (
        <div key={market.market_id}>
          <h3>
            {market.name} {market.type} {market.spov} {market.spun}{" "}
          </h3>
        </div>
      ))}
    </div>
  );
}
