"use client";
import { useState } from "react";
import {
  americanToDecimal,
  americanToFractional,
  decimalToAmerican,
  decimalToFractional,
  fractionalToAmerican,
  fractionalToDecimal,
} from "utils/calculator-utils";
import calcStyles from "styles/calculators.module.css";
import convertStyles from "styles/odds-converter.module.css";

export default function OddsConverter() {
  const [american, setAmerican] = useState(110);
  const [decimal, setDecimal] = useState(2.1);
  const [fractional, setFractional] = useState(11 / 10);

  const changeAmerican = (event) => {
    let integer = parseInt(event.target.value);
    setAmerican(integer);
    setDecimal(americanToDecimal(integer));
    setFractional(americanToFractional(integer));
  };

  const changeDecimal = (event) => {
    let float = parseFloat(event.target.value);
    setDecimal(float);
    setAmerican(decimalToAmerican(float).toFixed());
    setFractional(decimalToFractional(float));
  };

  const changeFractional = (event) => {
    setFractional(event.target.value);
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
                    placeholder="+100"
                    type="string"
                    id="american"
                    onChange={(event) => changeAmerican(event)}
                    value={american}
                  ></input>
                </li>
                <li>
                  <label>Decimal</label>
                  <input
                    name="decimal"
                    placeholder="2.00"
                    type="string"
                    id="decimal"
                    onChange={(event) => changeDecimal(event)}
                    value={decimal}
                  ></input>
                </li>
                <li>
                  <label>Fractional</label>
                  <input
                    name="fractional"
                    placeholder="1/1"
                    type="string"
                    id="fractional"
                    onChange={(event) => changeFractional(event)}
                    value={fractional}
                  ></input>
                </li>
                <li>
                  <label>Implied Probability</label>
                  <input
                    name="implied-probability"
                    placeholder="47.6%"
                    type="string"
                    id="implied-probability"
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
