"use client";
import React, { useState, useEffect } from "react";

const getLines = async () => {
  try {
    const resp = await fetch("http://localhost:8080/lines", {
      cache: "no-store",
    });
    if (!resp.ok) {
      throw new Error("Failed to fetch lines");
    }
    return resp.json();
  } catch (error) {
    console.error(error);
    return [];
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
      <h1>Lines Table</h1>
      <table border="2">
        <tr>
          <td>Line ID</td>
          <td>Market ID</td>
          <td>Sportsbook</td>
          <td>Home Odds</td>
          <td>Away Odds</td>
        </tr>
        {lines.map((line) => (
          <tr>
            <td>{line.line_id}</td>
            <td>{line.market_id}</td>
            <td>{line.sportsbook}</td>
            <td>{line.home_odds}</td>
            <td>{line.away_odds}</td>
          </tr>
        ))}
      </table>
    </div>
  );
}
