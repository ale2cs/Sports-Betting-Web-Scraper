"use client";
import React, { useState } from 'react';
import Link from "next/link";
import styles from "styles/navbar.module.css"

export default function Navbar() {
    const [isActive, setIsActive] = useState(false);

    const handleClick = () => {
      setIsActive(!isActive);
    }
    return (
        <div className={styles.navbar}>
            <Link href="/">Home</Link>
            <div className={styles['calculators-dropdown']}>
                <span className={styles['navbar-item']}>Calculators</span>
                <div className={styles['calculators-menu']}>
                    <Link href="/betting-calculators/kelly-criterion">Kelly Criterion</Link>
                    <Link href="/betting-calculators/margin">Margin</Link>
                    <Link href="/betting-calculators/odds-converter">Odds Converter</Link>
                </div>
            </div>
        </div>
    );
}