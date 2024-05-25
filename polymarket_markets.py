import requests
import json

# Polymarket API URL. Documentation: https://docs.polymarket.com/#introduction
url = "https://gamma-api.polymarket.com/query"

# GraphQL query to get all markets
query = """
{
  markets(where:"active = true and closed = false", offset: {offset_value})
    id
  }
}
"""

# Prepare the request payload
payload = json.dumps({"query": query})
headers = {
  'Content-Type': 'application/json'
}

# Send the request
response = requests.request("POST", url, headers=headers, data=payload)

# Print the response
print(response.text)
