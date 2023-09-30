const Fraction = require("fraction.js"); // Import Fraction.js

export const vig = (odds, odds2) => {
  return (1 / odds + 1 / odds2 - 1) * 100;
};

export const impliedProbability = (odds, odds2) => {
  return [odds2 / (odds + odds2), odds / (odds + odds2)];
};

export const noVigOdds = (odds, odds2) => {
  let [prob, prob2] = impliedProbability(odds, odds2);
  return [(1 / prob).toFixed(2), (1 / prob2).toFixed(2)];
};

export const convertOdds = (conversion, odds) => {
  let convertedOdds = null;
  const roundAmerican = 2;
  const roundDecimal = 3;
  const fractionalOddsPattern = /^(\d+)\/(\d+)$/;
  switch (conversion) {
    case "american-decimal":
      if (odds > 0) {
        convertedOdds = (1 + odds / 100).toFixed(roundDecimal);
      } else {
        convertedOdds = (1 - 100 / odds).toFixed(roundDecimal);
      }
      break;
    case "american-fractional":
      if (odds > 0) {
        convertedOdds = Fraction(odds / 100).toFraction();
        if (odds % 100 == 0) {
          convertedOdds = `${convertedOdds}/1`;
        }
      } else {
        convertedOdds = Fraction(-100 / odds).toFraction();
      }
      break;
    case "decimal-american":
      if (odds >= 2) {
        convertedOdds = `+${((odds - 1) * 100).toFixed(roundAmerican)}`;
      } else {
        convertedOdds = (-100 / (odds - 1)).toFixed(roundAmerican);
      }
      break;
    case "decimal-fractional":
      convertedOdds = Fraction(odds - 1)
        .simplify([0.001])
        .toFraction();
      if (odds % 1 == 0) {
        convertedOdds = `${convertedOdds}/1`;
      }
      break;
    case "fractional-decimal":
      if (fractionalOddsPattern.test(odds)) {
        const [numerator, denominator] = odds.split("/");
        const decimalValue = parseInt(numerator) / parseInt(denominator);
        convertedOdds = (decimalValue + 1).toFixed(roundDecimal);
      } else {
        convertedOdds = odds;
      }
      break;
    case "fractional-american":
      if (fractionalOddsPattern.test(odds)) {
        const [numerator, denominator] = odds.split("/");
        const decimalValue = parseInt(numerator) / parseInt(denominator);
        if (decimalValue >= 1) {
          convertedOdds = `+${(decimalValue * 100).toFixed(roundAmerican)}`;
        } else {
          convertedOdds = (-100 / decimalValue).toFixed(roundAmerican);
        }
      } else {
        convertedOdds = odds;
      }
      break;
  }
  return convertedOdds;
};

export const oddsToProbability = (format, odds) => {
  let probability = null;
  const round = 2;
  switch (format) {
    case "american":
      if (odds > 0) {
        probability = (100 / (odds + 100)) * 100;
      } else {
        probability = (Math.abs(odds) / (Math.abs(odds) + 100)) * 100;
      }
      break;
    case "decimal":
      probability = (1 / odds) * 100;
      break;
    case "fractional":
      probability = (1 / (odds + 1)) * 100;
      break;
  }
  return probability.toFixed(round);
};

export const probabilityToOdds = (format, probability) => {
  let odds = null;
  const roundAmerican = 2;
  const roundDecimal = 3;
  switch (format) {
    case "american":
      if (probability > 50) {
        odds = (-probability / (1 - probability / 100)).toFixed(roundAmerican);
      } else {
        odds = `+${(100 / (probability / 100) - 100).toFixed(roundDecimal)}`;
      }
      break;
    case "decimal":
      odds = (1 / (probability / 100)).toFixed(roundDecimal);
      break;
    case "fractional":
      odds = Fraction(1 / (probability / 100) - 1)
        .simplify([0.001])
        .toFraction();
      break;
  }
  return odds;
};

export const ev = (winProbability, odds) => {
  return winProbability * (odds - 1) + winProbability - 1;
};

export const kellyCriterion = (winProbability, odds) => {
  return winProbability - (1 - winProbability) / (odds - 1);
};

export const validInput = (input) => {
  const fractionalOddsPattern = /^(\d+)\/(\d+)$/;
  if (fractionalOddsPattern.test(input)) {
    // fractional
    return true;
  } else if (!isNaN(input) && isFinite(input) && input != "") {
    // american and decimal
    return true;
  }
  return false;
};

export const validOutput = (number) => {
  let display;
  const fractionalOddsPattern = /^(\d+)\/(\d+)$/;
  if (fractionalOddsPattern.test(number)) {
    // fraction
    display = number;
  } else if (!isNaN(number) && isFinite(number)) {
    // american and decimal
    display = number;
  } else {
    display = "0.00";
  }
  return display;
};
