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
    const resp = await fetch("http://localhost:8080/positive-ev", {
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
  const [positiveLines, setPositiveLines] = useState([]);
  const [listening, setListening] = useState(false);
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
    data: positiveLines,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    state: {
      sorting: sorting,
    },
    onSortingChange: setSorting,
  });

  useEffect(() => {
    if (!listening) {
      const events = new EventSource(
        "http://localhost:8080/socket-connection-request"
      );
      events.onmessage = (event) => {
        const parsedData = JSON.parse(event.data);
        setPositiveLines(parsedData);
      };
      setListening(true);
    }
  }, [listening, positiveLines]);

  return (
    <div className={styles["table-container"]}>
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
