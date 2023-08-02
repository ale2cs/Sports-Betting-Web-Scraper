"use client";
import React, { useState, useEffect } from "react";
import { useTable } from "react-table";
import * as dayjs from "dayjs";
import * as relativeTime from "dayjs/plugin/relativeTime";
dayjs.extend(relativeTime);

const getPositiveLines = async () => {
  try {
    const resp = await fetch("http://localhost:8080/positive-lines-test", {
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
        Header: "Time From Now",
        accessor: "date",
        Cell: ({ cell: { value } }) => {
          return `🕒 ${dayjs(value).fromNow()}`;
        },
      },
      {
        Header: "Event",
        accessor: "name",
      },
      {
        Header: "Bookmaker",
        accessor: "sportsbook",
      },
      {
        Header: "Market",
        accessor: "type",
      },
      {
        Header: "Bet",
        accessor: "bet",
      },
      {
        Header: "Edge",
        accessor: "ev",
      },
    ],
    []
  );

  const { getTableProps, getTableBodyProps, headerGroups, rows, prepareRow } =
    useTable({ columns, data: postiiveLines });

  useEffect(() => {
    const fetchData = async () => {
      const data = await getPositiveLines();
      setPositiveLines(data);
    };

    fetchData();
  }, []);

  return (
    <div>
      <div>
        <table {...getTableProps()}>
          <thead>
            {headerGroups.map((headerGroup) => (
              <tr {...headerGroup.getHeaderGroupProps()}>
                {headerGroup.headers.map((column) => (
                  <th {...column.getHeaderProps()}>
                    {column.render("Header")}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody {...getTableBodyProps()}>
            {rows.map((row) => {
              prepareRow(row);
              return (
                <tr {...row.getRowProps()}>
                  {row.cells.map((cell) => (
                    <td {...cell.getCellProps()}>{cell.render("Cell")}</td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
