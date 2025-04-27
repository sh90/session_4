import openai
import requests

# --- Configuration ---
import data_info

openai.api_key = data_info.open_ai_key

# API Key for RapidAPI (IMDB API)
RAPIDAPI_KEY = '766ea387a6msh84ff46479ed9b4bp18b495jsna547d73e1ef5'
IMDB_API_URL = "https://imdb236.p.rapidapi.com/imdb/autocomplete"


# --- External Tool Function: IMDB API Integration ---
AVIATIONSTACK_API_KEY = "56420807c490bd835b6e922d2b983fbb"
AVIATIONSTACK_URL = "http://api.aviationstack.com/v1/flights"

def call_flight_status_api(flight_number):
    params = {
        'access_key': AVIATIONSTACK_API_KEY,
        'flight_iata': flight_number
    }
    response = requests.get(AVIATIONSTACK_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get('data'):
            flight_info = data['data'][0]
            status = flight_info['flight_status']
            departure = flight_info['departure']['airport']
            arrival = flight_info['arrival']['airport']
            return f"Flight {flight_number} is currently {status}. Departure: {departure}, Arrival: {arrival}."
        else:
            return "Sorry, couldn't find information for that flight."
    else:
        return "Sorry, couldn't retrieve flight data."


def call_imdb_api(movie_title):
    headers = {
        'x-rapidapi-host': 'imdb236.p.rapidapi.com',
        'x-rapidapi-key': RAPIDAPI_KEY
    }
    params = {'query': movie_title}

    response = requests.get(IMDB_API_URL, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return "Sorry, couldn't retrieve movie information."


# --- Super Agent Logic (Updated) ---
def call_exchange_api(base_currency, target_currency):
    EXCHANGE_API_URL = "https://open.er-api.com/v6/latest/"
    response = requests.get(EXCHANGE_API_URL + base_currency.upper())
    if response.status_code == 200:
        data = response.json()
        if data.get('result') == 'success':
            rate = data['rates'].get(target_currency.upper())
            if rate:
                return f"1 {base_currency.upper()} = {rate} {target_currency.upper()}."
            else:
                return f"Sorry, couldn't find exchange rate for {target_currency}."
        else:
            return "Sorry, couldn't retrieve exchange rates."
    else:
        return "Sorry, couldn't access the exchange rate service."

def gpt4o_mini_super_agent(user_input):
    # Step 1: Decide what tool to use
    tool_selection_prompt = f"""You are a multi-tool assistant who can use external APIs:

- Weather API (for weather questions)
- Movie API (for movie questions)
- Currency Exchange API (for currency conversion)
- Flight Tracker API (for flight status)

When the user asks:
- About the weather -> "CALL_WEATHER_API: <city-name>"
- About a movie -> "CALL_MOVIE_API: <movie-title>"
- About currency -> "CALL_EXCHANGE_API: <base-currency> to <target-currency>"
- About a flight -> "CALL_FLIGHT_API: <flight-number>"

Otherwise, answer normally.

User input: "{user_input}"
"""

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": tool_selection_prompt}],
        temperature=0.1
    )

    assistant_reply = response.choices[0].message.content
    print(f"[Assistant Thought] {assistant_reply}")

    # Step 2: Handle tool call
    if assistant_reply.startswith("CALL_WEATHER_API:"):
        city_name = assistant_reply.replace("CALL_WEATHER_API:", "").strip()
        lat, lon = get_lat_lon(city_name)
        if lat is None or lon is None:
            return f"Sorry, I couldn't find the location for {city_name}."
        api_result = call_open_meteo_api(lat, lon)
        final_prompt = f"The weather in {city_name} is: {api_result}. Please create a friendly response."

    elif assistant_reply.startswith("CALL_MOVIE_API:"):
        movie_title = assistant_reply.replace("CALL_MOVIE_API:", "").strip()
        api_result = call_imdb_api(movie_title)  # Call the new IMDB API
        final_prompt = f"The movie information about {movie_title} is: {api_result}. Please create a friendly response."

    elif assistant_reply.startswith("CALL_EXCHANGE_API:"):
        parts = assistant_reply.replace("CALL_EXCHANGE_API:", "").strip().split(" to ")
        if len(parts) == 2:
            base_currency = parts[0]
            target_currency = parts[1]
            api_result = call_exchange_api(base_currency, target_currency)
            final_prompt = f"The exchange rate information is: {api_result}. Please create a friendly response."
        else:
            return "Sorry, I couldn't understand the currency conversion request."

    elif assistant_reply.startswith("CALL_FLIGHT_API:"):
        flight_number = assistant_reply.replace("CALL_FLIGHT_API:", "").strip()
        api_result = call_flight_status_api(flight_number)
        final_prompt = f"The flight status information is: {api_result}. Please create a friendly response."

    else:
        # No tool call needed, just reply normally
        return assistant_reply

    # Step 3: Final polish from GPT
    final_response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": final_prompt}],
        temperature=0.1
    )

    final_answer = final_response.choices[0].message.content
    return final_answer


# --- Main ---

if __name__ == "__main__":
    print("🤖 Ask me about weather, movies, currencies, or flights!")
    while True:
        user_question = input("\nYou: ")
        if user_question.lower() in ['exit', 'quit']:
            break
        answer = gpt4o_mini_super_agent(user_question)
        print("\n[Answer]")
        print(answer)
