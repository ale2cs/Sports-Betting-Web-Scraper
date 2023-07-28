const { PrismaClient } = require("@prisma/client");
//const { prisma } = require("./prisma");
const express = require("express");
const cors = require("cors");

const prisma = new PrismaClient();
const app = express();
app.use(cors());

const PORT = 8000;

app.get("/", async (req, res) => {
  res.send("hello world");
});

app.get("/markets", async (req, res) => {
  try {
    const markets = await prisma.markets.findMany();
    res.json(markets);
  } catch (error) {
    res.status(500).json({
      message: "Something went wrong",
    });
  }
});

app.get("/lines", async (req, res) => {
  try {
    const lines = await prisma.lines.findMany();
    res.json(lines);
  } catch (error) {
    res.status(500).json({
      message: "Something went wrong",
    });
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
