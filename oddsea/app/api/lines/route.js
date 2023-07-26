const { prisma } = require("@/lib/prisma")
const { NextResponse } = require("next/server");

export async function GET(request) {
  const lines = await prisma.lines.findMany();
  return NextResponse.json(lines);
}

export async function POST(request) {
  const json = await request.json();

  const created = await prisma.lines.create({
    data: json,
  });

  return new NextResponse(JSON.stringify(created), { status: 201 });
}