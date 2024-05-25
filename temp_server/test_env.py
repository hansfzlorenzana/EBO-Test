import gzip
from datetime import timedelta
from pprint import pprint, pformat
import imp
import sys
import shutil
import logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
import re
import requests
import json


PredictIt_manual_entry = [
        ("Stefanik","Stefanik",""),
        ]
my_PredictIt_URL = "https://www.predictit.org/api/marketdata/markets/8069" 

USE_CACHED_RESPONSES = False
SET_CACHED_RESPONSES = False

def scrape_predictit():
    scrape_failed = False

    try:

        headers = {
            "Cookie": "bfsd=ts=$(date +%s)000|st=p; betexPtk=betexCurrency%3DUSD%7EbetexTimeZone%3DAmerica%2FNew_York%7EbetexRegion%3DGBR%7EbetexLocale%3Den"
        }
        response = requests.get(my_PredictIt_URL, headers=headers)
        PredictIt_WINNER_raw = response.content

        PredictIt_WINNER_raw = unicode(PredictIt_WINNER_raw.decode('utf-8'))

        parsable_PredictIt_WINNER_raw = PredictIt_WINNER_raw.replace('"', '')
        parsable_PredictIt_WINNER_raw = ''.join(parsable_PredictIt_WINNER_raw.split())
        logging.info("PredictIt scraped")

        PredictIt_volume_URL = str(my_PredictIt_URL) + "/Contracts/Stats"
        PredictIt_volume_URL = PredictIt_volume_URL.replace("marketdata/markets","Market")
        def getTotalOpenInterest(url):
            resp = requests.get(url)
            json_data = json.loads(resp.content)
            costs = []
            for foo in json_data:
                costs.append(foo['openInterest'])
            total = sum(costs)
            return total
        def getTotalVolume(url):
            resp = requests.get(url)
            json_data = json.loads(resp.content)
            costs = []
            for foo in json_data:
                costs.append(foo['totalSharesTraded'])
            total = sum(costs)
            return total
        predictit_open_interest = getTotalOpenInterest(PredictIt_volume_URL)
        predictit_volume = getTotalVolume(PredictIt_volume_URL)
        #adjusting for peculiarities of Pred volume reporting
        predictit_volume = predictit_volume # / (len(PredictIt_manual_entry) / 2)
        predictit_open_interest = predictit_open_interest
    except Exception:
        warning_message = "Error scraping PredictIt (may try to recover with other markets)"

        scrape_failed = True

        parsable_PredictIt_WINNER_raw = ''
        predictit_volume = 0

    return scrape_failed, parsable_PredictIt_WINNER_raw, predictit_volume, predictit_open_interest

def parse_predictit_volume(predictit_volume):
    return predictit_volume

scrape, poly, vol, oi = scrape_predictit()

print "Volume"
print vol
print oi

# p_vol = parse_predictit_volume(vol)

# print(p_vol)

