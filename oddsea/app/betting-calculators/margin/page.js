"use client";
import { useEffect, useState } from "react";
import { vig, noVigOdds, impliedProbability } from "utils/calculator-utils";
import calcStyles from "styles/calculators.module.css";
import marginStyles from "styles/margin.module.css";

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
    setMargin(vig(odds1, odds2).toFixed(2));
    setBookmakerProbability1(((1 / odds1) * 100).toFixed(2));
    setBookmakerProbability2(((1 / odds2) * 100).toFixed(2));
    if (prob1 != 0) {
      setfairProbability2((prob2 * 100).toFixed(2));
      setFairOdds2(fair2);
    }
    if (prob2 != 0) {

      setfairProbability1((prob1 * 100).toFixed(2));
      setFairOdds1(fair1);
    }
  };

  const validate = (number) => {
    let display;
    if (isNaN(number) || !isFinite(number)) {
      display = "0.00";
    } else {
      display = number;
    }
    return display;
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
    <main className={calcStyles["main-container"]}>
      <div className={calcStyles["calc-head"]}>
        <h2 className={calcStyles["calc-header"]}>Margin Calculator</h2>
        <p>
          The Margin Calculator will convert Odds into probability and tell you
          how much your bookmaker is charging you.
        </p>
      </div>
      <section className={marginStyles["margin-calc"]}>
        <div className={marginStyles["calc-controls"]}></div>
        <div className={marginStyles["calc-content"]}>
          <form>
            <ul>
              <li>
                <div className={marginStyles["margin-info"]}>
                  <span className={marginStyles["info-span"]}>Odds</span>
                  <span className={marginStyles["info-span"]}>Bookmaker</span>
                  <span className={marginStyles["info-span"]}>Fair</span>
                  <span className={marginStyles["info-span"]}>Fair Odds</span>
                </div>
              </li>
              <li>
                <label className={marginStyles["margin-label"]}>Option 1</label>
                <input
                  className={marginStyles.odds1}
                  name="odds1"
                  placeholder="Enter odds"
                  type="string"
                  id="odds1"
                  onChange={(event) => changeOdds1(event)}
                ></input>
                <div className={marginStyles["margin-outputs"]}>
                  <span className={marginStyles["output-span"]}>
                    {validate(bookmakerProbability1)}
                    %
                  </span>
                  <span className={marginStyles["output-span"]}>
                    {validate(fairProbability1)}%
                  </span>
                  <span className={marginStyles["output-span"]}>
                    {validate(fairOdds1)}
                  </span>
                </div>
              </li>
              <li>
                <label className={marginStyles["margin-label"]}>Option 2</label>
                <input
                  className={marginStyles.odds2}
                  name="odds2"
                  placeholder="Enter odds"
                  type="string"
                  id="odds2"
                  onChange={(event) => changeOdds2(event)}
                ></input>
                <span className={marginStyles["output-span"]}>
                  {validate(bookmakerProbability2)}%
                </span>
                <span className={marginStyles["output-span"]}>
                  {validate(fairProbability2)}%
                </span>
                <span className={marginStyles["output-span"]}>{validate(fairOdds2)}</span>
              </li>
            </ul>
          </form>
          <div className={marginStyles.totals}>
            <div className={marginStyles.row}>
              <label className={marginStyles["margin-label"]}>Margin</label>
              <span className={marginStyles["margin-output"]}>
                {validate(margin)}%
              </span>
            </div>
          </div>
        </div>
        <div className={calcStyles["calc-footer"]}>
          <p>
            <br />A bookmaker's margin is essentially what they charge you for
            placing a bet. Sharp bettors will be aware of what a margin is and
            how to work it out but for those that don't, our Margin Calculator
            will do the work for you.
          </p>
          <p>
            <br />
            Bookmakers make profit by inflating the implied probability of an
            outcome, which decreases the odds you receive. The margin, which
            will vary depending on the bookmaker, is the difference between real
            probability and the odds offered by the bookmaker.
          </p>
          <p>
            <br />
            If you don't know how to work out a bookmaker's margin, using
            Pinnacle's Margin Calculator is the easiest way to calculate the
            probability and margin for any two-way or three-way bet. Compare our
            margins to other bookmakers and understand why serious bettors bet
            with Pinnacle.
          </p>
        </div>
      </section>
    </main>
  );
}
