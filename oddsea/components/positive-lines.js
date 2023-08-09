"use client";
import React, { useState, useEffect } from "react";
import {
  useReactTable,
  flexRender,
  getCoreRowModel,
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
  const columns = React.useMemo(
    () => [
      {
        header: "Time",
        accessorKey: "date",
        cell: info => `🕒 ${dayjs(info.getValue()).fromNow()}`
      },
      {
        header: "Event",
        accessorKey: "name",
      },
      {
        header: "Bookmaker",
        accessorKey: "sportsbook",
      },
      {
        header: "Market",
        accessorKey: "type",
      },
      {
        header: "Bet",
        accessorKey: "bet",
      },
      {
        header: "Edge",
        accessorKey: "ev",
      },
    ],
    []
  );

  const table = useReactTable({ 
    columns, 
    data: postiiveLines,
    getCoreRowModel: getCoreRowModel(),
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
      <table>
        <thead>
          {table.getHeaderGroups().map(headerGroup => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map(header => <th key={header.id}>
                {flexRender(header.column.columnDef.header, header.getContext())}
              </th>)}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map(row => (
            <tr key={row.id}>
              {row.getVisibleCells().map(cell => (
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
