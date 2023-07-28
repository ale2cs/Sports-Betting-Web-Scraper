"use client";
import React, { useState, useEffect } from "react";

const getMarkets = async () => {
  try {
    const resp = await fetch("http://localhost:8000/markets", {
      cache: "no-store",
    });
    if (!resp.ok) {
      throw new Error("Failed to fetch markets");
    }
    return resp.json();
  } catch (error) {
    console.error(error);
    return {};
  }
};

export default function ListMarkets() {
  const [markets, setMarkets] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const data = await getMarkets();
      setMarkets(data);
    };

    fetchData();
  }, []);

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
