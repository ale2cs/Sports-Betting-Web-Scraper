import calcStyles from "styles/calculators.module.css";
import kellyStyles from "styles/kelly.module.css";

export default function KellyCriterion() {
  return (
    <div>
      <header className={calcStyles["calc-head"]}>
        <h1 className={calcStyles["calc-header"]}>
          Kelly Criterion Calculator
        </h1>
        <aside>
          The Kelly Criterion Calculator will calculate the expected value of
          your bet and tell you how much of your bank roll to wager.
        </aside>
      </header>
      <main className={calcStyles["main-container"]}>
        <section className={calcStyles["calc-content"]}>
          <form>
            <ul className={kellyStyles["calc-wager"]}>
              <li>
                <label>Kelly Multiplier</label>
                <input
                  name="multiplier"
                  placeholder="Enter Multiplier"
                  type="string"
                  id="american"
                ></input>
              </li>
              <li>
                <label>Bankroll</label>
                <input
                  name="multiplier"
                  placeholder="Enter Multiplier"
                  type="string"
                  id="american"
                ></input>
              </li>
              <li>
                <label>Odds</label>
                <input
                  name="odds"
                  placeholder="Enter Odds"
                  type="string"
                  id="decimal"
                ></input>
              </li>
              <li>
                <label>Win %</label>
                <input
                  name="win-percentage"
                  placeholder="Enter Win Percentage"
                  type="string"
                  id="fractional"
                ></input>
              </li>
            </ul>
          </form>
        </section>
        <section className={calcStyles["calc-footer"]}>
          <p>
            A Kelly Criterion sports betting calculator can be used to manage
            your sports betting bankroll and determine optimal bet sizing. For
            obvious reasons, if your sports betting bankroll is, say, $5,000,
            you should not stake it all on one bet, regardless of how great you
            think the bet is. This is just common sense! Even the best bets lose
            sometimes, and you don't want your risk of ruin to be too high. You
            don't want to go broke on one bet.
          </p>
          <p>
            <br />
            But what's the optimal bet size? Should you bet 5% of your bankroll
            or 2.5% on each wager? That's what a Kelly Criterion sports betting
            calculator tells you. It's a mathematical betting formula that
            calculates the amount you should stake when there is a discrepancy
            between the given odds and the “fair” odds.
          </p>
          <p>
            <br />
            Of course, you should only place wagers when the given odds are
            superior to the “fair” odds. You don't want to place a bet at +100
            odds when fair is +103. This would be an example of a negative
            expected value (e.g. unprofitable) sports bet, and the Kelly
            Criterion would tell you to stake $0.
          </p>
          <p>
            <br />
            To use a Kelly Criterion calculator, you need to enter the odds
            given by the sportsbook, the “fair” win probability of your bet, and
            the current size of your sports betting bankroll. The Kelly
            calculator will automatically determine your optimal bet size, and
            this mathematical formula was designed to help you maximize profit
            while minimizing risk of ruin. As a general rule of thumb, your
            total sports betting bankroll should be an amount of money that you
            are comfortable losing. Most sports bettors start with a bankroll of
            $5,000 to $25,000.
          </p>
          <p>
            <br />
            You can determine “fair” win probability using the current market
            odds from the sharpest sportsbook in the world - you know what it
            is! Simply enter the market into a no vig calculator to determine
            fair win probability. As an example, imagine the sharpest bookmaker
            in the world has the New York Mets moneyline odds listed at -104
            odds. Their opponent is also listed at -104 odds, so both teams have
            the same moneyline odds. Thus, the “fair” win probability for the
            Mets would be 50%.
          </p>
        </section>
      </main>
    </div>
  );
}
