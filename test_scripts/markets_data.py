import requests
import json
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

polymarket_url = 'http://clob.polymarket.com/marketscondition_id=0x426cf619bab4d089ae92b1cf4ab28a3c86332b53b509e9aeb8b3753afdb168f1'

polymarket_raw = requests.get(polymarket_url, verify=False).content
resp_data = json.loads(polymarket_raw)
print(resp_data)