"use client";
import { useState } from "react";
import {
  convertOdds,
  oddsToProbability,
  probabilityToOdds,
} from "utils/calculator-utils";
import calcStyles from "styles/calculators.module.css";
import convertStyles from "styles/odds-converter.module.css";

export default function OddsConverter() {
  const [american, setAmerican] = useState("");
  const [decimal, setDecimal] = useState("");
  const [fractional, setFractional] = useState("");
  const [probability, setProbability] = useState("");

  const changeOdds = (e) => {
    const {name, value} = e.target;
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
          const fractionalOddsPattern = /^(\d+)\/(\d+)$/;
          setFractional(value);
          if (fractionalOddsPattern.test(value)) {
            const [numerator, denominator] = value.split("/");
            const decimalValue = parseInt(numerator) / parseInt(denominator);
            setAmerican(convertOdds("fractional-american", decimalValue));
            setDecimal(convertOdds("fractional-decimal", decimalValue));
            setProbability(oddsToProbability("fractional", decimalValue));
          } else {
            setDecimal("");
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
          Our Odds Converter will convert Decimal odds, American odds and
          Fractional odds into your chosen odds format.
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
          <p>
            Like a personal preference for internet browsers, most bettors have
            their favourite odds format, which is why we have created a handy
            Odds Converter Calculator. These preferences tend to follow cultural
            lines. <strong>Fractional</strong> odds dominate in the UK with
            their roots in betting on horse racing, but they are limited to
            familiar fractions which became problematic as betting has evolved
            and moved online.
          </p>
          <p>
            <br />
            <strong>Decimal odds</strong> provide a purer translation of odds
            with greater range - Pinnacle quote to three decimal places and have
            grown in popularity as betting has moved online. They also lend
            themselves to digital feeds such as APIs which are how information
            is shared across the internet.
          </p>
          <p>
            <br />
            Americans came up with their own way of measuring betting risk -
            <strong>American odds</strong> - based either on the return of $100
            (when implied probability is less than 50%) denoted with a +,
            whereas when implied probability is greater than 50% the odds are
            expressed in terms of what you have to bet to win $100 .
          </p>
          <p>
            <br />
            While it is valuable to understand what betting odds represent and
            convert between American odds, Decimal odds and Fractional odds in
            your head, our Odds Converter Calculator conveniently does it all
            for you.
          </p>
          <p>
            <br />
            Convert seamlessly between American, Decimal and Fractional odds and
            start learning the shortcuts for yourself.
          </p>
        </section>
      </main>
    </div>
  );
}
