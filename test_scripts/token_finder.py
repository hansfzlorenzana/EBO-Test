import requests
import json
import warnings
import time

# Ignore all warnings
warnings.filterwarnings("ignore")

# Starting polymarket_url with the initial next_cursor value
polymarket_url = 'http://clob.polymarket.com/markets?next_cursor=MTAx'
candidate_name = "Carson"
find_this = f"{candidate_name}"

while True:
    # Fetch data
    polymarket_raw = requests.get(polymarket_url, verify=False).content
    resp_data = json.loads(polymarket_raw)
    
    # Check if candidate name is present in any question
    for entry in resp_data['data']:
        question = entry.get('question')
        condition_id = entry.get('condition_id')
        token_id = entry.get('tokens')
        if find_this in question:
            print("Condition ID:", condition_id)
            print("Question:", question)
            print(token_id)
            break  # Exit the loop if candidate is found
    else:
        # If candidate is not found, try the next page
        next_cursor = resp_data.get('next_cursor')
        print(next_cursor)
        if next_cursor:
            polymarket_url = f'http://clob.polymarket.com/markets?next_cursor={next_cursor}'
            time.sleep(5)
        else:
            print("No more data to fetch.")
            break  # Exit the loop if there's no more data to fetch
