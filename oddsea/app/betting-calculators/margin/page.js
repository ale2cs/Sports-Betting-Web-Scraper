"use client";
import { useEffect, useState } from "react";
import {
  vig,
  noVigOdds,
  impliedProbability,
  convertOdds,
  validInput,
  validOutput,
} from "utils/calculator-utils";
import calcStyles from "styles/calculators.module.css";
import marginStyles from "styles/margin.module.css";
import oddsFormatStyles from "styles/odds-format.module.css";

export default function Margin() {
  const [oddsFormat, setOddsFormat] = useState("decimal");
  const [inputs, setInputs] = useState({
    odds1: "",
    odds2: "",
  });
  const [outputs, setOutputs] = useState({
    margin: 0,
    fairProbability1: 0,
    fairProbability2: 0,
    bookmakerProbability1: 0,
    bookmakerProbability2: 0,
    fairOdds1: 0,
    fairOdds2: 0,
  });

  const changeInputs = (e) => {
    const { name, value } = e.target;
    setInputs((prevValue) => {
      return { ...prevValue, [name]: value };
    });
  };

  const changeOutputs = (key, value) => {
    setOutputs((prevValue) => {
      return { ...prevValue, [key]: value };
    });
  };

  const changeOddsFormat = (e) => {
    const newFormat = e.target.value;
    const convertType = `${oddsFormat}-${newFormat}`;
    let odds1 = inputs.odds1;
    let odds2 = inputs.odds2;

    if (validInput(odds1)) {
      odds1 = convertOdds(convertType, odds1);
    }
    if (validInput(odds2)) {
      odds2 = convertOdds(convertType, odds2);
    }
    setInputs({
      ...inputs,
      odds1: odds1,
      odds2: odds2,
    });
    setOddsFormat(newFormat);
  };

  const convertFairOdds = (odds) => {
    switch (oddsFormat) {
      case "decimal":
        return odds;
      case "american":
        return convertOdds("decimal-american", odds);
      case "fractional":
        return convertOdds("decimal-fractional", odds);
    }
  };

  const calculate = () => {
    let odds1 = null;
    let odds2 = null;
    switch (oddsFormat) {
      case "decimal":
        odds1 = parseFloat(inputs.odds1);
        odds2 = parseFloat(inputs.odds2);
        break;
      case "american":
        odds1 = parseFloat(
          convertOdds("american-decimal", parseFloat(inputs.odds1))
        );
        odds2 = parseFloat(
          convertOdds("american-decimal", parseFloat(inputs.odds2))
        );
        break;
      case "fractional":
        odds1 = parseFloat(convertOdds("fractional-decimal", inputs.odds1));
        odds2 = parseFloat(convertOdds("fractional-decimal", inputs.odds2));
        break;
    }
    let [prob1, prob2] = impliedProbability(odds1, odds2);
    let [fair1, fair2] = noVigOdds(odds1, odds2);

    changeOutputs("margin", vig(odds1, odds2).toFixed(2));
    changeOutputs("bookmakerProbability1", ((1 / odds1) * 100).toFixed(2));
    changeOutputs("bookmakerProbability2", ((1 / odds2) * 100).toFixed(2));
    if (prob1 != 0) {
      changeOutputs("fairProbability2", (prob2 * 100).toFixed(2));
      changeOutputs("fairOdds2", convertFairOdds(fair2));
    }
    if (prob2 != 0) {
      changeOutputs("fairProbability1", (prob1 * 100).toFixed(2));
      changeOutputs("fairOdds1", convertFairOdds(fair1));
    }
  };

  useEffect(() => {
    calculate();
  }, [inputs]);

  return (
    <div>
      <header className={calcStyles["calc-head"]}>
        <h1 className={calcStyles["calc-header"]}>Margin Calculator</h1>
        <aside>
          The Margin Calculator will convert odds into probabilities and
          caclulate the amount a bookmaker is charging for a particular bet.
        </aside>
      </header>
      <main className={calcStyles["main-container"]}>
        <section className={calcStyles["calc-content"]}>
          <div className={oddsFormatStyles.controls}>
            <label className={oddsFormatStyles["select-format-label"]}>
              Odds Format:
            </label>
            <select
              value={oddsFormat}
              className={oddsFormatStyles["select-odds"]}
              onChange={changeOddsFormat}
            >
              <option value="american">American</option>
              <option value="decimal" selected>
                Decimal
              </option>
              <option value="fractional">Fractional</option>
            </select>
          </div>
          <form>
            <ul>
              <li>
                <div className={marginStyles["field-names"]}>
                  <label className={marginStyles["field-label"]}>Odds</label>
                  <label className={marginStyles["field-label"]}>
                    Bookmaker
                  </label>
                  <label className={marginStyles["field-label"]}>Fair</label>
                  <label className={marginStyles["field-label"]}>
                    Fair Odds
                  </label>
                </div>
              </li>
              <li>
                <div className={marginStyles.option}>
                  <label className={marginStyles["option-label"]}>
                    Option 1
                  </label>
                  <input
                    className={marginStyles.odds}
                    name="odds1"
                    placeholder="Enter odds"
                    type="string"
                    id="odds1"
                    onChange={(e) => changeInputs(e)}
                    value={inputs.odds1}
                  ></input>
                  <div className={marginStyles.outputs}>
                    <div className={marginStyles["outputs-small"]}>
                      <label className={marginStyles["field-label-small"]}>
                        Bookmaker
                      </label>
                      <span className={marginStyles["output-span"]}>
                        {validOutput(outputs.bookmakerProbability1)}%
                      </span>
                    </div>
                    <div className={marginStyles["outputs-small"]}>
                      <label className={marginStyles["field-label-small"]}>
                        Fair
                      </label>
                      <span className={marginStyles["output-span"]}>
                        {validOutput(outputs.fairProbability1)}%
                      </span>
                    </div>
                    <div className={marginStyles["outputs-small"]}>
                      <label className={marginStyles["field-label-small"]}>
                        Fair Odds
                      </label>
                      <span className={marginStyles["output-span"]}>
                        {validOutput(outputs.fairOdds1)}
                      </span>
                    </div>
                  </div>
                </div>
              </li>
              <li>
                <div className={marginStyles.option}>
                  <label className={marginStyles["option-label"]}>
                    Option 2
                  </label>
                  <input
                    className={marginStyles.odds}
                    name="odds2"
                    placeholder="Enter odds"
                    type="string"
                    id="odds2"
                    onChange={(e) => changeInputs(e)}
                    value={inputs.odds2}
                  ></input>

                  <div className={marginStyles.outputs}>
                    <div className={marginStyles["outputs-small"]}>
                      <label className={marginStyles["field-label-small"]}>
                        Bookmaker
                      </label>
                      <span className={marginStyles["output-span"]}>
                        {validOutput(outputs.bookmakerProbability2)}%
                      </span>
                    </div>
                    <div className={marginStyles["outputs-small"]}>
                      <label className={marginStyles["field-label-small"]}>
                        Fair
                      </label>
                      <span className={marginStyles["output-span"]}>
                        {validOutput(outputs.fairProbability2)}%
                      </span>
                    </div>
                    <div className={marginStyles["outputs-small"]}>
                      <label className={marginStyles["field-label-small"]}>
                        Fair Odds
                      </label>
                      <span className={marginStyles["output-span"]}>
                        {validOutput(outputs.fairOdds2)}
                      </span>
                    </div>
                  </div>
                </div>
              </li>
            </ul>
          </form>
          <div className={marginStyles.totals}>
            <label className={marginStyles["margin-label"]}>Margin</label>
            <span className={marginStyles["margin-output"]}>
              {validOutput(outputs.margin)}%
            </span>
          </div>
        </section>
        <section className={calcStyles["calc-footer"]}>
          <h2>How to Use the Margin Calculator?</h2>
          <p>
            The Margin Calculator serves multiple purposes: it helps you
            determine the margin of a particular bet, uncover the implied
            probability set by the bookmaker's odds, and reveal the actual
            probabilities of winning each bet. Designed for two-way bets, simply
            enter in an odds pair of a betting line from a sportsbook, and let
            the calculator do the work.{" "}
          </p>
          <p>
            For instance, if you are planning to bet on the Edmonton Oilers
            moneyline, enter the Oilers odds to win as the first odds and the
            oponent's odds as the second.{" "}
          </p>
          <p>
            The <strong>'Bookmaker'</strong> column displays the implied
            probabilites of te odds provided by the bookmaker. It is the implied
            probabilities with margin priced in. When the sum of probabilities
            of the two outcomes exceeds 100%, it implies the margin is greater
            than zero.
          </p>
          <p>
            In the <strong>'Fair'</strong> column you will find the fair
            probabilities of each outcome of a bet, representing the true
            probabilities of each outcome of a bet after the margin has been
            removed. These percentages can be used as the real probabilities of
            the outcomes if the bookmaker is sharp.
          </p>
          <p>
            The <strong>'Fair Odds'</strong> column reveals the 'no-vig odds'
            that the bookermaker should offer if they did not include any
            margin. When a bookmaker is sharp, finding better odds than the
            'no-vig odds' from sharp bookmaker will result in a postive expected
            value bet.
          </p>
          <h2>What is Margin?</h2>
          <p>
            Margin, often referred to as 'vig' (short for vigorish), represents
            the fee imposed by bookmakers when you place a bet. In essence, it
            is the price you pay for sports betting. At their core, sportsbooks
            are businesses, and for sportsbooks to operate profitably, they
            intentionally offer odds that are less favorable than the true odds.
            This means they exaggerate the implied probability of an outcome,
            resulting in reduced payouts for bettors. By applying this strategy
            to both sides of a bet, bookmakers ensure their ability to generate
            profits regardless of the bet's outcome. It's a fundamental aspect
            of the sports betting industry that allows sportsbooks to be
            profitable.
          </p>
          <h2>Why is Margin Important?</h2>
          <p>
            Understanding margin is key to identifying sportsbooks confidence on
            the bets they offer. In general, sportsbooks with lower margins tend
            to be sharper, offering more accurate odds. Lower margins indicate
            their confidence in the odds they provide while still ensuring
            profitability. As an event's start time approaches, margins
            naturally decrease as sportsbooks grow more assured of the true
            odds.
          </p>
          <p>
            Following the principle that sharper sportsbooks generally offer
            more accurate odds and recognizing that sportsbooks lower their
            margins as their confidence in their lines increases, we can use the
            odds they provide as a basis for determining fair odds and
            probabilities when the event is close to starting.
          </p>
          <p>
            Margins can fluctuate based on various factors, including the sport,
            league, type of bet, and time remaining until the event starts. Even
            with the same sportsbook, margins can exhibit significant
            variations. For instance, popular sports leagues like the NBA
            typically have lower margins compared to the WNBA. This discrepancy
            arises from the higher transaction volume and increased analytical
            efforts invested in determining true odds for more prominent
            leagues.
          </p>
          <p>
            In general, lower margins can be indicative of higher confidence in
            a bet's accuracy, allowing us to use them as a reference for the
            best guess of the true odds, often referred to as 'no-vig odds.'
            Betting on markets with lower margins enhances our confidence when
            identifying a edge.
          </p>
        </section>
      </main>
    </div>
  );
}
