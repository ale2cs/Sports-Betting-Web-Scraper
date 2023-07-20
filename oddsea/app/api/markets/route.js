const { PrismaClient } = require("@prisma/client");
const { NextResponse } = require("next/server");

const prisma = new PrismaClient();

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