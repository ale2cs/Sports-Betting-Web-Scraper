"use client";
import React, { useState, useEffect } from "react";
import styles from "styles/tables.module.css";
import {
  useReactTable,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
} from "@tanstack/react-table";
import * as dayjs from "dayjs";
import * as relativeTime from "dayjs/plugin/relativeTime";
dayjs.extend(relativeTime);

const getPositiveLines = async () => {
  try {
    const resp = await fetch("http://localhost:8080/positive-lines", {
      cache: "no-store",
    });
    if (!resp.ok) {
      throw new Error("Failed to fetch positive lines");
    }
    return resp.json();
  } catch (error) {
    console.error(error);
    return [];
  }
};

export default function ListPositiveLines() {
  const [postiiveLines, setPositiveLines] = useState([]);
  const [sorting, setSorting] = useState([
    {
      id: "date",
      desc: false,
    },
  ]);
  const columns = React.useMemo(
    () => [
      {
        header: "TIME",
        accessorKey: "date",
        cell: (info) => `🕒 ${dayjs(info.getValue()).fromNow()}`,
      },
      {
        header: "EDGE",
        accessorKey: "ev",
      },
      {
        header: "EVENT",
        accessorFn: (row) => [row.name, `${row.sport} | ${row.league}`],
        cell: (info) => {
          const [matchup, league] = info.getValue();
          return (
            <div>
              <div>{matchup}</div>
              <div>{league}</div>
            </div>
          );
        },
        enableSorting: false,
      },
      {
        header: "BOOKMAKER",
        accessorKey: "sportsbook",
        enableSorting: false,
      },
      {
        header: "MARKET",
        accessorKey: "type",
        enableSorting: false,
      },
      {
        header: "BET",
        accessorKey: "bet",
        enableSorting: false,
      },
    ],
    []
  );

  const table = useReactTable({
    columns,
    data: postiiveLines,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    state: {
      sorting: sorting,
    },
    onSortingChange: setSorting,
  });

  useEffect(() => {
    const fetchData = async () => {
      const data = await getPositiveLines();
      setPositiveLines(data);
    };

    fetchData();
  }, []);

  return (
    <div>
      <h2 className={styles["title"]}>Current Positive EV Bets</h2>
      <table className={styles["content-table"]}>
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th
                  key={header.id}
                  onClick={header.column.getToggleSortingHandler()}
                >
                  {flexRender(
                    header.column.columnDef.header,
                    header.getContext()
                  )}
                  {
                    { asc: " 🡡", desc: " 🡣" }[
                      header.column.getIsSorted() ?? null
                    ]
                  }
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id}>
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
