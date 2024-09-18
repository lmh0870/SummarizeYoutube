import requests

url = "https://api.laftel.net/api/search/v1/discover/"
params = {"sort": "rank", "years": "2010년", "offset": 0, "size": 10}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"에러 발생: {response.status_code}")
