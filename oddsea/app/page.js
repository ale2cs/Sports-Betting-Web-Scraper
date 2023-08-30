import Image from "next/image";
import PositiveLines from "@/components/positive-lines";
import styles from "styles/home.module.css";

export default function Home() {
  return (
    <main>
      <h1 className={styles.title}>Current Positive EV Bets</h1>
      <PositiveLines />
    </main>
  );
}
