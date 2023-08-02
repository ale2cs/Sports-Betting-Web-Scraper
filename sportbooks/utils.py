import math
from datetime import datetime, timezone, timedelta

def flatten(list_to_flatten):
    return [item for sub_list in list_to_flatten for item in sub_list]

def rnd_dec(number, decimals):
    # Returns a value rounded down to a specific number of decimal places.
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more")
    elif decimals == 0:
        return math.floor(number)

    factor = 10 ** decimals
    return math.floor(number * factor) / factor

def american_to_decimal(number):
    dec = 3
    if (number > 0):
        return rnd_dec(1 + (number / 100), dec)
    else:
        return rnd_dec(1 - (100 / number), dec)

def imp_prob(odds1, odds2):
    return (odds2 / (odds1 + odds2)), (odds1 / (odds1 + odds2))

def vig(odds1, odds2):
    return (1 / odds1) + (1 / odds2) - 1

def no_vig_odds(odds1, odds2): 
    prob1, prob2 = imp_prob(odds1, odds2)
    return (1 / prob1), (1 / prob2) 

def ev(win_prob, odds):
    return (win_prob * (odds - 1)) + win_prob - 1 

def pos_ev(odds1, odds2, odds3, odds4):
    prob1, prob2 = imp_prob(odds1, odds2)
    ev1 = ev(prob1, odds3)
    ev2 = ev(prob2, odds4)
    return ev1 if (ev1 > 0) else ev2

def kelly_criterion(win_prob, odds):
    return win_prob - ((1 - win_prob) / (odds - 1))

def wager(bankroll, odds1, odds2, odds3): 
    prob1, prob2 = imp_prob(odds1, odds2)
    multiplier = 0.20
    kelly = kelly_criterion(prob1, odds3)
    return multiplier * kelly * bankroll

def rem_time(time):
    return datetime.fromisoformat(time) - datetime.fromisoformat(datetime.now(timezone.utc).isoformat())

def over_max_hours(time, hours):
    return datetime.fromisoformat(time) > (datetime.fromisoformat((datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()))

def epoch_to_iso(time):
    return f"{datetime.utcfromtimestamp(time).isoformat()}Z"