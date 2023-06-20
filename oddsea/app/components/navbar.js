"use client";
import React, { useState } from 'react';
import Link from "next/link";

export default function Navbar() {
    const [isActive, setIsActive] = useState(false);

    const handleClick = () => {
      setIsActive(!isActive);
    }
    return (
        <div class="navbar">
            <Link href="/" class="navbar-item">Home</Link>
            <div class="calculators-dropdown">
                <span class="navbar-item">Calculators</span>
                <div class="calculators-menu">
                    <Link href="/betting-calculators/no-vig">No-Vig</Link>
                    <Link href="/betting-calculators/kelly-criterion">Kelly Criterion</Link>
                    <Link href="/betting-calculators/odds-converter">Odds Converter</Link>
                </div>
            </div>
        </div>
    );
}