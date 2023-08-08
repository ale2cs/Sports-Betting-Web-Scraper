"use client";
import { useEffect, useState } from "react";
import { vig, noVigOdds, impliedProbability } from "@/utils/calculator-utils";

export default function NoVig() {
  const [odds1, setOdds1] = useState(0);
  const [odds2, setOdds2] = useState(0);
  const [margin, setMargin] = useState(0);
  const [fairProbability1, setfairProbability1] = useState(0);
  const [fairProbability2, setfairProbability2] = useState(0);
  const [bookmakerProbability1, setBookmakerProbability1] = useState(0);
  const [bookmakerProbability2, setBookmakerProbability2] = useState(0);
  const [fairOdds1, setFairOdds1] = useState(0);
  const [fairOdds2, setFairOdds2] = useState(0);

  const calculate = () => {
    let [prob1, prob2] = impliedProbability(odds1, odds2);
    let [fair1, fair2] = noVigOdds(odds1, odds2);
    setMargin(vig(odds1, odds2));
    setBookmakerProbability1(((1 / odds1) * 100).toFixed(2));
    setBookmakerProbability2(((1 / odds2) * 100).toFixed(2));
    setfairProbability1((prob1 * 100).toFixed(2));
    setfairProbability2((prob2 * 100).toFixed(2));
    setFairOdds1(fair1);
    setFairOdds2(fair2);
  };

  const changeOdds1 = (event) => {
    setOdds1(parseFloat(event.target.value));
  };
  const changeOdds2 = (event) => {
    setOdds2(parseFloat(event.target.value));
  };

  useEffect(() => {
    calculate();
  }, [odds1, odds2]);

  return (
    <main className="main-container">
      <div class="calc-intro-box">
        <h2 class="calc-head">Margin Calculator</h2>
        <p>
          The Margin Calculator will convert Odds into Probability and tell you
          how much your bookmaker is charging you.
        </p>
      </div>
      <div class="calculator">
        <form>
          <ul>
            <li>
              <div class="calc-info">
                <span class="info-span">Odds</span>
                <span class="info-span">Bookmaker</span>
                <span class="info-span">Fair</span>
                <span class="info-span">Fair Odds</span>
              </div>
            </li>
            <li>
              <label class="calc-label">Option 1</label>
              <input
                name="odds1"
                class="odds1"
                placeholder="Enter odds"
                type="string"
                id="odds1"
                onChange={(event) => changeOdds1(event)}
              ></input>
              <div class="calc-outputs">
                <span class="output-span">{bookmakerProbability1}%</span>
                <span class="output-span">{fairProbability1}%</span>
                <span class="output-span">{fairOdds1}</span>
              </div>
            </li>
            <li>
              <label class="calc-label">Option 2</label>
              <input
                name="odds2"
                class="odds2"
                placeholder="Enter odds"
                type="string"
                id="odds2"
                onChange={(event) => changeOdds2(event)}
              ></input>
              <span class="output-span">{bookmakerProbability2}%</span>
              <span class="output-span">{fairProbability2}%</span>
              <span class="output-span">{fairOdds2}</span>
            </li>
          </ul>
        </form>
        <div class="totals">
          <div class="row">
            <label class="calc-label">Margin</label>
            <span class="margin">{margin.toFixed(2)}%</span>
          </div>
        </div>
        <div class="calc-footer">
          <p>
            <br/>
            A bookmaker's margin is essentially what they charge you for 
            placing a bet. Sharp bettors will be aware of what a margin is and 
            how to work it out but for those that don't, our Margin Calculator 
            will do the work for you.
          </p>
          <p>
            <br/>
            Bookmakers make profit by inflating the implied probability of an 
            outcome, which decreases the odds you receive. The margin, which 
            will vary depending on the bookmaker, is the difference between 
            real probability and the odds offered by the bookmaker.
          </p>
          <p>
            <br/>
            If you don't know how to work out a bookmaker's margin, using 
            Pinnacle's Margin Calculator is the easiest way to calculate the 
            probability and margin for any two-way or three-way bet. Compare 
            our margins to other bookmakers and understand why serious bettors 
            bet with Pinnacle.
          </p>
        </div>
      </div>
    </main>
  );
}
