"use client";
import { useState } from "react";
import {
  convertOdds,
  oddsToProbability,
  probabilityToOdds,
  validInput,
} from "utils/calculator-utils";
import calcStyles from "styles/calculators.module.css";
import convertStyles from "styles/odds-converter.module.css";

export default function OddsConverter() {
  const [american, setAmerican] = useState("");
  const [decimal, setDecimal] = useState("");
  const [fractional, setFractional] = useState("");
  const [probability, setProbability] = useState("");

  const changeOdds = (e) => {
    const { name, value } = e.target;
    const num = parseFloat(value);
    if (value == "") {
      setAmerican("");
      setDecimal("");
      setFractional("");
      setProbability("");
    } else {
      switch (name) {
        case "american":
          setAmerican(value);
          setDecimal(convertOdds("american-decimal", num));
          setFractional(convertOdds("american-fractional", num));
          setProbability(oddsToProbability("american", num));
          break;
        case "decimal":
          setDecimal(value);
          setAmerican(convertOdds("decimal-american", num));
          setFractional(convertOdds("decimal-fractional", num));
          setProbability(oddsToProbability("decimal", num));
          break;
        case "fractional":
          setFractional(value);
          const fractionalOddsPattern = /^(\d+)\/(\d+)$/;
          if (fractionalOddsPattern.test(value)) {
            setAmerican(convertOdds("fractional-american", value));
            setDecimal(convertOdds("fractional-decimal", value));
            setProbability(oddsToProbability("fractional", value));
          } else {
            setAmerican("");
            setDecimal("");
            setProbability("");
          }
          break;
        case "impliedProbability":
          setProbability(value);
          setAmerican(probabilityToOdds("american", value));
          setDecimal(probabilityToOdds("decimal", value));
          setFractional(probabilityToOdds("fractional", value));
          break;
      }
    }
  };

  return (
    <div>
      <header className={calcStyles["calc-head"]}>
        <h1 className={calcStyles["calc-header"]}>Odds Converter Calculator</h1>
        <aside>
          The Odds Converter will convert odds between three most used odds
          formats in the world and calculate its implied probability.
        </aside>
      </header>
      <main className={calcStyles["main-container"]}>
        <section className={calcStyles["calc-content"]}>
          <div className={convertStyles.converters}>
            <form>
              <ul className={convertStyles["calc-conversion"]}>
                <li>
                  <label>American</label>
                  <input
                    name="american"
                    placeholder="+110"
                    type="string"
                    id="american"
                    onInput={(e) => changeOdds(e)}
                    value={american}
                  ></input>
                </li>
                <li>
                  <label>Decimal</label>
                  <input
                    name="decimal"
                    placeholder="2.100"
                    type="string"
                    id="decimal"
                    onInput={(e) => changeOdds(e)}
                    value={decimal}
                  ></input>
                </li>
                <li>
                  <label>Fractional</label>
                  <input
                    name="fractional"
                    placeholder="11/10"
                    type="string"
                    id="fractional"
                    onChange={(e) => changeOdds(e)}
                    value={fractional}
                  ></input>
                </li>
                <li>
                  <label>Implied Probability</label>
                  <input
                    name="impliedProbability"
                    placeholder="47.62%"
                    type="string"
                    id="impliedProbability"
                    onChange={(e) => changeOdds(e)}
                    value={probability}
                  ></input>
                </li>
              </ul>
            </form>
          </div>
        </section>
        <section className={calcStyles["calc-footer"]}>
          <h2>How to Use the Odds Converter Calculator?</h2>
          <p>
            Enter in the proper format into any of the input boxes and it will
            calculate away! The calculator can also handle inputing the
            probability of a bet winning and convert it into its odd form.
          </p>
          <p>
            <strong>American odds</strong> are based either on the return of
            $100 (when implied probability is less than 50%) denoted with a +,
            whereas when implied probability is greater than 50% the odds are
            expressed in terms of the amount to bet to win $100. For example
            betting $100 on +120 odds, would profit you $120, while betting $100
            on -120 odds would profit you $83.33.
          </p>
          <p>
            <strong>Decimal odds</strong> represent the return of the amount
            wagered multiplied by the odds. For example betting $100 on 2.1 odds
            will return $210 dollars, resulting in a $110 profit.
          </p>
          <p>
            <strong>Fractional odds</strong> express the odds as a ratio in the
            form of a fraction, where numerator represents the potential profit,
            and the denominator represents the amount to state. For instance,
            betting $100 on 1/2 odds will yield a total return of $150,
            resulting in a profit of $50.
          </p>
          <h2>Why are there Different Odds Formats?</h2>
          <p>
            Odds formats are like different lanagues spoken aroud the world.
            Just as people from different regions use various langauges to
            communicate, sports bettors from different areas use distinct odds
            formats. Often, a bettor's preference for an odds format is due to
            what is commonly offered in their region. Fractional odds are
            predominantly used in the United Kingdom, american odds in North
            America, and decimal odds in places in Europe and Australasia.
          </p>
          <p>
            Sportsbooks may only offer one type of odds format making it
            valuable to understand what betting odds represent. Converting
            between American odds, Decimal odds and Fractional odds in your head
            can be difficult so you can use the Odds Converter Calculator as
            tool to help you out. 
          </p>
        </section>
      </main>
    </div>
  );
}
