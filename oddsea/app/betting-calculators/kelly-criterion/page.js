"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import calcStyles from "styles/calculators.module.css";
import kellyStyles from "styles/kelly.module.css";
import oddsFormatStyles from "styles/odds-format.module.css";
import {
  ev,
  kellyCriterion,
  validInput,
  validOutput,
  convertOdds,
} from "utils/calculator-utils";

export default function KellyCriterion() {
  const [oddsFormat, setOddsFormat] = useState("decimal");
  const [inputs, setInputs] = useState({
    multiplier: 0,
    bankroll: 0,
    odds: "",
    winProbability: 0,
  });
  const [outputs, setOutputs] = useState({
    evPercentage: "0.00",
    wagerPercentage: "0.00",
    evDollar: "0.00",
    wagerDollar: "0.00",
  });

  const changeInputs = (e) => {
    const { name, value } = e.target;
    setInputs((prevValues) => {
      return { ...prevValues, [name]: value };
    });
  };

  const changeOutputs = (key, value) => {
    setOutputs((prevValues) => {
      return { ...prevValues, [key]: value };
    });
  };

  const changeOddsFormat = (e) => {
    const newFormat = e.target.value;
    const convertType = `${oddsFormat}-${newFormat}`;
    let odds = inputs.odds;

    if (validInput(odds)) {
      odds = convertOdds(convertType, odds);
    }
    setInputs({
      ...inputs,
      odds: odds,
    });
    setOddsFormat(newFormat);
  };

  const calculate = () => {
    let multiplier = inputs.multiplier;
    let bankroll = inputs.bankroll;
    let odds = inputs.odds;
    switch (oddsFormat) {
      case "decimal":
        odds = parseFloat(odds);
        break;
      case "american":
        odds = parseFloat(convertOdds("american-decimal", parseFloat(odds)));
        break;
      case "fractional":
        odds = parseFloat(convertOdds("fractional-decimal", odds));
        break;
    }
    let winProbability = inputs.winProbability;
    let expectedValue = ev(winProbability / 100, odds);
    let kelly = kellyCriterion(winProbability / 100, odds);

    changeOutputs("evPercentage", (expectedValue * 100).toFixed(2));
    if (expectedValue > 0) {
      changeOutputs("wagerPercentage", (multiplier * kelly * 100).toFixed(2));
      changeOutputs(
        "evDollar",
        (expectedValue * multiplier * kelly * bankroll).toFixed(2)
      );
      changeOutputs("wagerDollar", (multiplier * kelly * bankroll).toFixed(2));
    } else {
      changeOutputs("wagerPercentage", "0.00");
      changeOutputs("evDollar", "0.00");
      changeOutputs("wagerDollar", "0.00");
    }
  };

  useEffect(() => {
    calculate();
  }, [inputs]);

  return (
    <div>
      <header className={calcStyles["calc-head"]}>
        <h1 className={calcStyles["calc-header"]}>
          Kelly Criterion Calculator
        </h1>
        <aside>
          The Kelly Criterion Calculator will calculate the expected value of
          your bet and tell you how much to wager.
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
          <div className={kellyStyles["content"]}>
            <form>
              <ul className={kellyStyles["field"]}>
                <li>
                  <label>Kelly Multiplier</label>
                  <input
                    name="multiplier"
                    placeholder="0.3"
                    type="string"
                    id="american"
                    onChange={(e) => changeInputs(e)}
                  ></input>
                </li>
                <li>
                  <label>Bankroll</label>
                  <input
                    name="bankroll"
                    placeholder="5000"
                    type="string"
                    id="american"
                    onChange={(e) => changeInputs(e)}
                  ></input>
                </li>
                <li>
                  <label>Odds</label>
                  <input
                    name="odds"
                    placeholder="2.1"
                    type="string"
                    id="decimal"
                    onChange={(e) => changeInputs(e)}
                    value={inputs.odds}
                  ></input>
                </li>
                <li>
                  <label>Win Probability</label>
                  <input
                    name="winProbability"
                    placeholder="50"
                    type="string"
                    id="fractional"
                    onChange={(e) => changeInputs(e)}
                  ></input>
                </li>
              </ul>
            </form>
            <div className={kellyStyles.totals}>
              <div className={kellyStyles.output}>
                <label>Expected Value %</label>
                <span>{validOutput(outputs.evPercentage)}%</span>
              </div>
              <div className={kellyStyles.output}>
                <label>Wager %</label>
                <span>{outputs.wagerPercentage}%</span>
              </div>
              <div className={kellyStyles.output}>
                <label>Expected Value $</label>
                <span>${outputs.evDollar}</span>
              </div>
              <div className={kellyStyles.output}>
                <label>Wager $</label>
                <span>${outputs.wagerDollar}</span>
              </div>
            </div>
          </div>
        </section>
        <section className={calcStyles["calc-footer"]}>
          <h2>How to Use the Kelly Criterion Calculator</h2>
          <p>
            To utilize the Kelly Criterion calculator, input the odds and "fair"
            win probability of your bet, along with the desired fraction of the
            Kelly Criterion to apply. The calculator will determine the expected
            value of the bet and the optimal wager as a percentage of your
            bankroll. If you wish for the optimal wager amount to be in dollars
            and determine expected value of that wager in dollars as well, you
            have the option to enter your bankroll amount.
          </p>
          <p>
            You can determine “fair” win probability using the current market
            odds from the sharpest sportsbooks in the world. Enter the market
            into our{" "}
            <Link href="/betting-calculators/margin">Margin Calculator</Link> to
            determine the fair win probability. As an example, imagine the
            sharpest bookmaker in the world has the Toronto Raptors moneyline
            odds listed at 1.95 odds, with their oppenent having the same odds.
            In this case, both teams have identical moneyline odds, resulting in
            a "fair" win probability of 50% for the Raptors.
          </p>
          <h2>What is the Kelly Criterion?</h2>
          <p>
            The Kelly Criterion is a mathematical formula used in betting and
            investing to determine the optimal size of bets or investments. Its
            primary objective is to maximize the growth of capital over time
            while minimizing the risk of ruin. This is achieved by considering
            the expected value of each bet or investment and their associated
            risks.
          </p>
          <h2>Why Use Kelly Criterion?</h2>
          <p>
            Picture this: you've just stumbled upon an exceptional betting
            opportunity, and you're contemplating of wagering half of bankroll.
            While you should be inclined to wager more on promising bets, it's
            important to remember that even the best bets result in losses. You
            don't want to go broke in a few bets. Perserving your bankroll by
            properly sizing your bets will ensure your ability to weather
            unfavorable variance and the Kelly Criterion is the tool.
          </p>
          <p>
            What's the optimal bet size? Is it best to place a consistent $50
            bet for each wager, or would it be better to allocate a fixed
            percentage, such as 2.5% of your bankroll? Selecting any of these
            methods could work but it doesn't take into account the actual bet.
            A bet could have a high likehood of winning but this strategy
            doesn't factor it in. Rather than selecting an arbitrary flat value
            or percentage, the Kelly Criterion tailors the bet size for each bet
            by considering the odds and the bet's probability to win.
          </p>
          <p>
            Expected values of bets vary, and therefore, bet sizes should also
            vary to match them. Why opt for a bet a fixed rate, whether its flat
            or based on percentage, when a bet with an expected value of 3% is
            higher than one with an expected value of 2%? The higher expected
            value of a bet, the more advantageous it becomes to stake larger
            amounts, since potential returns increase. The Kelly Criterion
            follows this logic of scaling bet sizes proportionally to maximize
            profits.
          </p>
          <h2>Why Use Fractional Kelly Criterion?</h2>
          <p>
            While the Kelly Criterion is an invaluable tool for determining
            optimal wager sizes, it's essential to be cautious when considering
            its recommendations. The key factor to bear in mind is the Kelly
            multiplier, which you input into the calculator. Even the sharpest
            sportsbooks are susceptible to inaccuracies in their predictions,
            occasionally introducing errors into their calculations. These
            errors can potentially skew the "fair" odds used in Kelly Criterion
            calculations. Moreover, market odds are in a constant state of flux,
            and by the time you place a bet, the initially calculated "fair"
            odds may no longer be in your favor. The greatest risk lies in
            overestimating your edge. To mitigate this, it's advisable to adopt
            a more conservative approach, opting for a fraction in the range of
            0.2 to 0.3.
          </p>
        </section>
      </main>
    </div>
  );
}
