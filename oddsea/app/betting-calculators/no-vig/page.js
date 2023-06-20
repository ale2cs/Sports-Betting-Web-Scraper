"use client";
import { useState } from 'react';
import styles from 'app/page.module.css';
import {vig, impliedProbability, noVigOdds} from 'app/utils/calculator-utils';

export default function NoVig() { 
    const [odds, setOdds] = useState(2);
    const [odds2, setOdds2] = useState(1.9);
    
    const changeOdds = (event) => {
        setOdds(parseFloat(event.target.value));
    }
    const changeOdds2 = (event) => {
        setOdds2(parseFloat(event.target.value));
    }

    return (
        <main className={styles.main}>
            <div>
                <h1>This is the no-vig calcualtor page!</h1>
                <input name="odds" placeholder="2.00" type="string" id="odds" onChange={event => changeOdds(event)}></input>
                <input name="odds2" placeholder="1.90" type="string" id="odds2" onChange={event => changeOdds2(event)}></input>
                <h2>{odds} {odds2}</h2>
                <h2>{typeof(odds)} {typeof(odds2)}</h2>
                <h2>{odds + odds2}</h2>
                <h2>{vig(odds, odds2)}</h2>
                <h2>{impliedProbability(odds, odds2).join(', ')}</h2>
                <h2>{noVigOdds(odds, odds2).join(', ')}</h2>
            </div>
        </main>
    );
}