#pip install requests
import requests

GEOCODING_API_URL = "https://geocoding-api.open-meteo.com/v1/search"
city_name = "tokyo"
params = {
    'name': city_name,
    'count': 1
}
response = requests.get(GEOCODING_API_URL, params=params)
if response.status_code == 200:
    data = response.json()
    if data.get('results'):
        lat = data['results'][0]['latitude']
        lon = data['results'][0]['longitude']
        print( lat, lon)
    else:
        print( None, None)
else:
    print( None, None)
