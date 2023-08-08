import Image from "next/image";
import Markets from "@/components/markets";
import Lines from "@/components/lines";
import PositiveLines from "@/components/positive-lines";

export default function Home() {
  return (
    <main>
      <h1>This is the home page!</h1>
      <PositiveLines /> 
    </main>
  );
}
