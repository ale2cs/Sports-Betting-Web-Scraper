from datetime import datetime, timezone, timedelta

def epoch_to_iso(time):
    return f"{datetime.utcfromtimestamp(time).isoformat()}Z"


def over_max_hours(time, hours):
    return datetime.fromisoformat(time) > (datetime.fromisoformat((datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()))


def rem_time(time):
    return datetime.fromisoformat(time) - datetime.fromisoformat(datetime.now(timezone.utc).isoformat())
