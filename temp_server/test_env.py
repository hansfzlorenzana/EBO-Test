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


Polymarket_new_manual_entry = [
        ((240613,"Democratic"),"DEM",""),
        ((240613,"Republican"),"REP",""),]
my_Polymarket_URL = "https://polymarket.com/event/which-party-will-win-the-2024-united-states-presidential-election"
USE_CACHED_RESPONSES = False
SET_CACHED_RESPONSES = False

def scrape_polymarket_new():
    scrape_failed = False

    # Scraping Polymarket (Direct, Clob API and Gamma API)
    polymarket_contracts_by_id = {}
    try:

        # Extract PRICES using Polymarket Clob API
        def get_json(polymarket_clob_url):
            clob_api_raw = requests.get(polymarket_clob_url, verify=False,timeout=5).content
            resp_data = json.loads(clob_api_raw)
            return resp_data
        
        pm_ids = set([])
        for (cand_FULL_name, _, _) in Polymarket_new_manual_entry:
            if cand_FULL_name:
                (pm_id, _) = cand_FULL_name
                # We'll get mixed up if we're not on the same page about whether this is an int or a string
                assert isinstance(pm_id, int), "Polymarket ids should be integers, not strings"
                pm_ids.add(pm_id)
        polymarket_ids = [str(pm_id) for pm_id in pm_ids]
        polymarket_url = my_Polymarket_URL
        if USE_CACHED_RESPONSES:
            polymarket_raw = open('cached/polymarket_raw', 'r').read()
        else:
            polymarket_raw = requests.get(polymarket_url, verify=False)
            if SET_CACHED_RESPONSES:
                open('cached/polymarket_raw', 'w').write(polymarket_raw)
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
                        no_token_id = market['clobTokenIds'][1]

                        # Extract BID & ASK PRICES using Polymarket Clob API
                        price_url_base = 'https://clob.polymarket.com/price'
                        # First outcome
                        yes_bid_query_fields = '?side=buy&token_id={}'.format(str(yes_token_id))
                        yes_ask_query_fields = '?side=sell&token_id={}'.format(str(yes_token_id))
                        yes_bid_price = get_json(price_url_base + yes_bid_query_fields)
                        yes_ask_price = get_json(price_url_base + yes_ask_query_fields)

                        # Second outcome
                        no_bid_query_fields = '?side=buy&token_id={}'.format(str(no_token_id))
                        no_ask_query_fields = '?side=sell&token_id={}'.format(str(no_token_id))
                        no_bid_price = get_json(price_url_base + no_bid_query_fields)
                        no_ask_price = get_json(price_url_base + no_ask_query_fields)

                        market['outcomesPrice'] = [{'outcome': outcome, 'bid': None, 'ask': None} for outcome in market['outcomes']]                        
                        # Add 'bid' and 'ask' fields to the market dictionary
                        market['outcomesPrice'][0]['bid'] = yes_bid_price
                        market['outcomesPrice'][0]['ask'] = yes_ask_price
                        market['outcomesPrice'][1]['bid'] = no_bid_price
                        market['outcomesPrice'][1]['ask'] = no_ask_price
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

        # Just check that we got all of the ids we asked for:
        found_ids = set(polymarket_contracts_by_id.keys())
        if pm_ids - found_ids != set(): # Not every expected ID was found
            logging.warning("Polymarket API did not return these expected ids: " + ', '.join(map(str, (pm_ids - found_ids))))
        if pm_ids - found_ids == pm_ids: # Not *any* expected ID was found
            # NOTE: further down the process, we have a warning email for any markets with zero candidate data found
            logging.warning("Polymarket API did not return any expected ids. (will try to recover with other markets)")

    except Exception as e:
        warning_message = "Error scraping Polymarket (may try to recover with other markets)"

        scrape_failed = True

        logging.warning(warning_message)

        polymarket_contracts_by_id = {}
        polymarket_volume = 0

    return scrape_failed, polymarket_contracts_by_id, polymarket_volume

def parse_polymarket_new_odds(polymarket_contracts_by_id, cand_FULL_name):
    # In the case of Polymarket Clob API, we will denote skipping a candidate with an empty string or a None
    pm_id, pm_outcome = cand_FULL_name
    if pm_id in polymarket_contracts_by_id and pm_outcome in polymarket_contracts_by_id[pm_id]['outcomes']:
        outcome_index = polymarket_contracts_by_id[pm_id]['outcomes'].index(pm_outcome)
        print outcome_index

        # TODO - handle odd cases like low liquidity like the other markets?
        Candidate_ask = float(polymarket_contracts_by_id[pm_id]['outcomesPrice'][outcome_index]['ask']['price'])
        Candidate_bid = float(polymarket_contracts_by_id[pm_id]['outcomesPrice'][outcome_index]['bid']['price'])
        Candidate_odds = (Candidate_bid+Candidate_ask)/2

        return {
            'Candidate_found': True,
            'Candidate_bid': Candidate_bid,
            'Candidate_ask': Candidate_ask,
            'Candidate_odds': Candidate_odds,
        }
    else:
        return {
            'Candidate_found': False,
        }

scrape, poly, vol = scrape_polymarket_new()

cand_FULL_name = (240613,"Republican")

parse_polymarket_new_odds(poly, cand_FULL_name)