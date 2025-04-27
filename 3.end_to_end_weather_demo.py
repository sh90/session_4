# pip install openai requests
import openai
import requests

# Configure OpenAI API key
import data_info

openai.api_key = data_info.open_ai_key

# Geocoding API to convert city -> lat/lon (no API key needed)
GEOCODING_API_URL = "https://geocoding-api.open-meteo.com/v1/search"

def get_lat_lon(city_name):
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
            return lat, lon
        else:
            return None, None
    else:
        return None, None


def call_open_meteo_api(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = data['current_weather']
        return f"The temperature is {weather['temperature']}°C with windspeed {weather['windspeed']} km/h. Weather code: {weather['weathercode']}."
    else:
        return "Sorry, couldn't retrieve the weather data."


def gpt4o_mini_agent(user_input):
    # First, let GPT decide what to do
    prompt = f"""You are an intelligent assistant with access to a weather API.

    If the user asks anything about the weather in a city, respond with: 
    "CALL_WEATHER_API: <city-name>"
    
    Otherwise, answer normally.
    
    User input: "{user_input}"
    """


    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    assistant_reply =  response.choices[0].message.content

    print(f"[Assistant Thought] {assistant_reply}")

    # If GPT indicates to call the API
    if assistant_reply.startswith("CALL_WEATHER_API:"):
        city_name = assistant_reply.replace("CALL_WEATHER_API:", "").strip()

        # Step 1: Get latitude and longitude
        lat, lon = get_lat_lon(city_name)
        if lat is None or lon is None:
            return f"Sorry, I couldn't find the location for {city_name}."

        # Step 2: Get weather data
        api_result = call_open_meteo_api(lat, lon)
        print(api_result)

        # Step 3: Let GPT format the final answer nicely
        final_prompt = f"The weather information for {city_name} is: {api_result}. Please compose a friendly response to the user."

        final_response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": final_prompt}],
            temperature=0.1
        )

        final_answer = final_response.choices[0].message.content

        return final_answer
    else:
        return assistant_reply

# Example usage
user_input = input("Ask me something: ")
prompt = f"""You are an intelligent assistant with access to a weather API.

    If the user asks anything about the weather in a city, respond with: 
    "CALL_WEATHER_API: <city-name>"

    Otherwise, answer normally.

    User input: "{user_input}"
    """

prompt_tweak = f"""You are an intelligent assistant with access to a weather API.

    If the user asks anything about the weather in a city, respond with: 
    "CALL_WEATHER_API: <city-name>"
    If you feel there is error in city name try to correct it and then format your response. If it can't be corrected 
    then return the origin city name which user has entered.
    Otherwise, answer normally.

    User input: "{user_input}"
    """
# we will experiment with prompt and prompt_tweak

response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.1
)

assistant_reply = response.choices[0].message.content

print(f"[Assistant Thought] {assistant_reply}")

# If GPT indicates to call the API
if assistant_reply.startswith("CALL_WEATHER_API:"):
    city_name = assistant_reply.replace("CALL_WEATHER_API:", "").strip()

    # Step 1: Get latitude and longitude
    lat, lon = get_lat_lon(city_name)
    if lat is None or lon is None:
        print( f"Sorry, I couldn't find the location for {city_name}.")

    # Step 2: Get weather data
    api_result = call_open_meteo_api(lat, lon)
    print(api_result)

    # Step 3: Let GPT format the final answer nicely
    final_prompt = f"The weather information for {city_name} is: {api_result}. Please compose a friendly response to the user."

    final_response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": final_prompt}],
        temperature=0.1
    )

    final_answer = final_response.choices[0].message.content
    print("-----------Final Response is------------")
    print(final_answer)
else:
    print("-----------Final Response is------------")
    print(assistant_reply)

