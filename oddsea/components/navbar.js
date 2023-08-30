import Link from "next/link";
import styles from "styles/navbar.module.css";

export default function Navbar() {
  return (
    <header className={styles["main-header"]}>
      <nav>
        <ul className={styles.options}>
          <li className={styles.option}>
            <Link className={styles.link} href="/">
              Home
            </Link>
          </li>
          <li className={styles.option}>
            <div className={styles.dropdown}>
              <button aria-haspopup="menu">
                Calculators
                <span className={styles.arrow}></span>
              </button>
              <ul className={styles["dropdown-menu"]}>
                <li>
                  <Link
                    className={styles.link}
                    href="/betting-calculators/kelly-criterion"
                  >
                    Kelly Criterion
                  </Link>
                </li>
                <li>
                  <Link
                    className={styles.link}
                    href="/betting-calculators/margin"
                  >
                    Margin
                  </Link>
                </li>
                <li>
                  <Link
                    className={styles.link}
                    href="/betting-calculators/odds-converter"
                  >
                    Odds Converter
                  </Link>
                </li>
              </ul>
            </div>
          </li>
          <li className={styles.option}>
            <Link className={styles.link} href="/about">About</Link>
          </li>
          <li className={styles.option}>
            <Link className={styles.link} href="/contact">Contact</Link>
          </li>
        </ul>
      </nav>
    </header>
  );
}
