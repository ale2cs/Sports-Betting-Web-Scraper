const { PrismaClient } = require("@prisma/client");
const React = require("react");
const { cache, use } = require("react");

const prisma = new PrismaClient();

const getMarkets = cache(() =>
  fetch("http://localhost:3000/api/markets").then((res) => res.json())
);

export default function ListUsers() {
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
