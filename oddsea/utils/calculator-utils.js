export const vig = (odds, odds2) => {
    return (
        ((1 / odds) + (1 / odds2) - 1) * 100
    );
}

export const impliedProbability = (odds, odds2) => {
    return (
        [(odds2 / (odds + odds2)), (odds / (odds + odds2))]
    );
}

export const noVigOdds = (odds, odds2) => {
    let [prob, prob2] = impliedProbability(odds, odds2);
    return (
        [(1 / prob).toFixed(2), (1 / prob2).toFixed(2)]
    );
}

export const americanToDecimal = (odds) => {
    const dec = 3;
    if (odds > 0) {
        return (1 + (odds / 100)).toFixed(dec);
    }
    return (1 - (100 / odds)).toFixed(dec); 
}

export const americanToFractional = (odds) => {
    if (odds > 0) {
        return odds / 100;
    }
    return -100 / odds;
}

export const fractionalToDecimal = (odds) => {
    const dec = 3;
    return (odds + 1).toFixed(dec);
}

export const fractionalToAmerican = (odds) => {
    if (odds > 1) {
        return (odds * 100);
    }
    return -100 / odds;
}

export const decimalToFractional = (odds) => {
    return odds - 1;
}

export const decimalToAmerican = (odds) => {
    if (odds > 2) {
        return (odds - 1) * 100;
    }
    return -100 / (odds - 1);
}

export const ev = (winProbability, odds) => {
    return (winProbability * (odds - 1)) + winProbability - 1;
}

export const kellyCriterion = (winProbability, odds) => {
    return winProbability - ((1 - winProbability) / (odds - 1))
}