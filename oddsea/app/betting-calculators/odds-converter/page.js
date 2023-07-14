"use client";
import { useState } from 'react';
import styles from 'app/page.module.css'
import { americanToDecimal, americanToFractional, decimalToAmerican,
         decimalToFractional, fractionalToAmerican, fractionalToDecimal,
} from '/app/utils/calculator-utils';

export default function OddsConverter() {
    const [american, setAmerican] = useState(110);
    const [decimal, setDecimal] = useState(2.1);
    const [fractional, setFractional] = useState(11 / 10);

    const changeAmerican = (event) => {
        let integer = parseInt(event.target.value);
        setAmerican(integer); 
        setDecimal(americanToDecimal(integer));
        setFractional(americanToFractional(integer));
    }

    const changeDecimal= (event) => {
        let float = parseFloat(event.target.value);
        setDecimal(float);
        setAmerican(decimalToAmerican(float).toFixed());
        setFractional(decimalToFractional(float));
    }

    const changeFractional= (event) => {
        setFractional(event.target.value);
    }
    return (
         <main className={styles.main}>
            <div>
                <h1>This is the odds-converter calculator page!</h1>
                <h2>American</h2>
                <input name="american" placeholder="+100" type="string" id="american" onChange={event => changeAmerican(event)} value={american}></input>
                <h2>Decimal</h2>
                <input name="decimal" placeholder="2.00" type="string" id="decimal" onChange={event => changeDecimal(event)} value={decimal}></input>
                <h2>Fractional</h2>
                <input name="fractional" placeholder="1/1" type="string" id="fractional" onChange={event => changeFractional(event)} value={fractional}></input>
            </div>
         </main>
    );
}