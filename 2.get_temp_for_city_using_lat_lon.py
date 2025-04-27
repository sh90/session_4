#pip install requests
#Objective: Learn how to call external APIs to get real time information
import requests

lat=35.6895
lon=139.691
url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
print(url)
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    weather = data['current_weather']
    print(f"The temperature is {weather['temperature']}°C with a wind speed of {weather['windspeed']} km/h.")
else:
    print("Sorry, couldn't retrieve the weather.")
