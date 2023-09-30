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
          The Margin Calculator will convert odds into probability and tell you
          how much your bookmaker is charging you.
        </aside>
      </header>
      <main className={calcStyles["main-container"]}>
        <section className={calcStyles["calc-content"]}>
          <div className={marginStyles.controls}>
            <label className={marginStyles["select-format-label"]}>
              Odds Format:
            </label>
            <select
              value={oddsFormat}
              className={marginStyles["select-odds"]}
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
          <h2>What is Margin?</h2>
          <p>
            A bookmaker's margin is essentially what they charge you for placing
            a bet. Sharp bettors will be aware of what a margin is and how to
            work it out but for those that don't, our Margin Calculator will do
            the work for you.
          </p>
          <p>
            Bookmakers make profit by inflating the implied probability of an
            outcome, which decreases the odds you receive. The margin, which
            will vary depending on the bookmaker, is the difference between real
            probability and the odds offered by the bookmaker.
          </p>
          <p>
            If you don't know how to work out a bookmaker's margin, using
            Pinnacle's Margin Calculator is the easiest way to calculate the
            probability and margin for any two-way or three-way bet. Compare our
            margins to other bookmakers and understand why serious bettors bet
            with Pinnacle.
          </p>
        </section>
      </main>
    </div>
  );
}
