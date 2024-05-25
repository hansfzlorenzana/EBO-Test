
import requests
import json


Polymarket_manual_entry = [
        ((16678291189211314787145083999015737376658799626183230671758641503291735614088,"Yes"),"Stefanik",""),
        ]
def get_all_keys(data):
    keys = set()
    if isinstance(data, dict):
        for key, value in data.items():
            keys.add(key)
            keys.update(get_all_keys(value))  # Recursively get keys from nested dictionaries
    elif isinstance(data, list):
        for item in data:
            keys.update(get_all_keys(item))  # Recursively get keys from nested dictionaries in the list
    return keys
pm_ids = set([])
for (cand_FULL_name, _, _) in Polymarket_manual_entry:
    if cand_FULL_name:
        (pm_id, _) = cand_FULL_name
        # We'll get mixed up if we're not on the same page about whether this is an int or a string
        assert isinstance(pm_id, int), "Polymarket ids should be integers, not strings"
        pm_ids.add(pm_id)
# end up with something like ?id=123&id=435
polymarket_id_query_fields = ['token_id=' + str(pm_id) for pm_id in pm_ids]
polymarket_query_string = '?' + '&'.join(polymarket_id_query_fields)
polymarket_url = 'http://clob.polymarket.com/price/' + polymarket_query_string
print(polymarket_url)
polymarket_raw = requests.get(polymarket_url, verify=False).content
# print(polymarket_raw) 
resp_data = json.loads(polymarket_raw)['data']
# Get all keys
all_keys = get_all_keys(resp_data)
print(all_keys)
# ids come back as integers so we make them strings
polymarket_contracts_by_id = {resp_entry['token_id']: resp_entry for resp_entry in resp_data}
print(polymarket_contracts_by_id)

# Just check that we got all of the ids we asked for:
found_ids = set(polymarket_contracts_by_id.keys())
print(found_ids)