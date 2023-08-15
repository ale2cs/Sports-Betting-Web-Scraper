import express from "express";
import cors from "cors";
import bodyParser from "body-parser"
import positiveEV from "./app/positive-ev/positive-ev-route.js";

const app = express();
const PORT = 8080;

app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: false}));

app.use(positiveEV);

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
