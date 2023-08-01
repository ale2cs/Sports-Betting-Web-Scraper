const { prisma } = require("@/lib/prisma")
const { NextResponse } = require("next/server");

export async function GET(request) {
  const markets = await prisma.markets.findMany();
  return NextResponse.json(markets);
}

export async function POST(request) {
  const json = await request.json();

  const created = await prisma.markets.create({
    data: json,
  });

  return new NextResponse(JSON.stringify(created), { status: 201 });
}