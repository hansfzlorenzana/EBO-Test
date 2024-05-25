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

my_Polymarket_URL = "https://polymarket.com/event/republican-vp-nominee"

Polymarket_new_manual_entry = [
        ((253992,"Yes"),"TimScott",""),
        ((254112,"Yes"),"Vance",""),
        ]

# Extract PRICES using Polymarket Clob API
def get_json(polymarket_clob_url):
    clob_api_raw = requests.get(polymarket_clob_url, verify=False,timeout=5).content
    resp_data = json.loads(clob_api_raw)
    return resp_data

polymarket_contracts_by_id = {}

pm_ids = set([])
for (cand_FULL_name, _, _) in Polymarket_new_manual_entry:
    if cand_FULL_name:
        (pm_id, _) = cand_FULL_name
        # We'll get mixed up if we're not on the same page about whether this is an int or a string
        assert isinstance(pm_id, int), "Polymarket ids should be integers, not strings"
        pm_ids.add(pm_id)
polymarket_ids = [str(pm_id) for pm_id in pm_ids]
polymarket_url = my_Polymarket_URL
polymarket_raw = requests.get(polymarket_url, verify=False)

html_content = polymarket_raw.text

# Find the script tag with id="__NEXT_DATA__" using regex
script_tag_match = re.search(r'<script\s+id="__NEXT_DATA__"\s+type="application/json"\s+crossorigin="anonymous">(.+?)</script>', html_content)

if script_tag_match:
    # Extract JSON data from the matched script tag
    json_data = json.loads(script_tag_match.group(1))

    event_id = json_data['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']['id']
    # Extract VOLUME using direct scrape
    polymarket_volume_direct = json_data['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']['volume']

    # Extract content for each ID in the list
    for id_to_extract in pm_ids:
        for market in json_data['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']['markets']:
            if market['id'] == str(id_to_extract):
                yes_token_id = market['clobTokenIds'][0]

                # Extract BID & ASK PRICES using Polymarket Clob API
                price_url_base = 'https://clob.polymarket.com/price'
                bid_query_fields = '?side=buy&token_id={}'.format(str(yes_token_id))
                ask_query_fields = '?side=sell&token_id={}'.format(str(yes_token_id))
                bid_price = get_json(price_url_base + bid_query_fields)
                ask_price = get_json(price_url_base + ask_query_fields)

                # Add 'bid' and 'ask' fields to the market dictionary
                market['bid'] = bid_price
                market['ask'] = ask_price
                polymarket_contracts_by_id[id_to_extract] = market
                break

# Extract VOLUME using gamma-api.polymarket.com
gamma_response = requests.get("https://gamma-api.polymarket.com/events/" + event_id, verify=False)
if gamma_response.status_code == 200:
    gamma_api_data = gamma_response.content
    try:
        gamma_api_data = json.loads(gamma_api_data)
        polymarket_volume_gamma = gamma_api_data.get('volume', 0)  # Default to 0 if 'volume' key is not present
        polymarket_volume = polymarket_volume_gamma
    except ValueError:
        polymarket_volume = polymarket_volume_direct
else:
    # Use polymarket_volume_direct as fallback if the response is not successful
    polymarket_volume = polymarket_volume_direct

Candidate_ask = float(polymarket_contracts_by_id[pm_id]['ask']['price'])
Candidate_bid = float(polymarket_contracts_by_id[pm_id]['bid']['price'])
Candidate_odds = (Candidate_bid+Candidate_ask)/2

print Candidate_ask
print Candidate_bid
print Candidate_odds