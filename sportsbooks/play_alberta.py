import requests
import jmespath


def get_play_alberta():
    bet_type_dict = {"MONEY_LINE": "moneyline" ,"FIXED_SPREAD": "spread", "FIXED_TOTAL": "total"}
    period_dict = {"Match": 0}

    url = "https://www.online.paglcprdabp.abpa.io/metal/v3/sportsbookdata/delta/events/usview/from/3050599992"
        