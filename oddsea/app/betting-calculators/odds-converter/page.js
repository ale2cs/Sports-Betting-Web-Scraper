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
    <main className={calcStyles["main-container"]}>
      <div className={calcStyles["calc-head"]}>
        <h2 className={calcStyles["calc-header"]}>Odds Converter Calculator</h2>
        <p>
          Our Odds Converter will convert Decimal odds, American odds and
          Fractional odds into your chosen odds format.
        </p>
      </div>
      <section className={convertStyles["converter-calc"]}>
        <div className={convertStyles["calc-content"]}>
          <form>
            <ul className={convertStyles["calc-conversion"]}>
              <li>
                <label className={convertStyles}>American</label>
                <input
                  name="american"
                  className={convertStyles.odds}
                  placeholder="+100"
                  type="string"
                  id="american"
                  onChange={(event) => changeAmerican(event)}
                  value={american}
                ></input>
              </li>
              <li>
                <label className={convertStyles}>Decimal</label>
                <input
                  name="decimal"
                  className={convertStyles.odds}
                  placeholder="2.00"
                  type="string"
                  id="decimal"
                  onChange={(event) => changeDecimal(event)}
                  value={decimal}
                ></input>
              </li>
              <li>
                <label className={convertStyles}>Fractional</label>
                <input
                  name="fractional"
                  className={convertStyles.odds}
                  placeholder="1/1"
                  type="string"
                  id="fractional"
                  onChange={(event) => changeFractional(event)}
                  value={fractional}
                ></input>
              </li>
            </ul>
          </form>
        </div>
        <div className={convertStyles["calc-footer"]}>
          <p>
            <br />
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
        </div>
      </section>
    </main>
  );
}
