"use client";
import React, { useState, useEffect } from "react";

const getLines = async () => {
  try {
    const resp = await fetch("http://localhost:8000/lines", {
      cache: "no-store",
    });
    if (!resp.ok) {
      throw new Error("Failed to fetch lines");
    }
    return resp.json();
  } catch (error) {
    console.error(error);
    return {};
  }
};

export default function ListMarkets() {
  const [lines, setLines] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const data = await getLines();
      setLines(data);
    };

    fetchData();
  }, []);

  return (
    <div>
      {lines.map((line) => (
        <div key={line.line_id}>
          <h3>
            {line.line_id} {line.market_id} {line.sportsbook} {line.home_odds}{" "}
            {line.away_odds}
          </h3>
        </div>
      ))}
    </div>
  );
}
