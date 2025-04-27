import openai
import requests
import data_info
# Configure OpenAI API Key
openai.api_key = data_info.open_ai_key

# Exchange Rates API (no key needed for open.er-api.com)
EXCHANGE_API_URL = "https://open.er-api.com/v6/latest/"


def call_exchange_api(base_currency, target_currency):
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


def gpt4o_mini_currency_agent(user_input):
    prompt = f"""You are an assistant with access to a currency exchange API.

    If the user asks about exchanging currency, respond exactly:
    "CALL_EXCHANGE_API: <base-currency-code> to <target-currency-code>"
    
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

    if assistant_reply.startswith("CALL_EXCHANGE_API:"):
        parts = assistant_reply.replace("CALL_EXCHANGE_API:", "").strip().split(" to ")
        if len(parts) == 2:
            base_currency = parts[0]
            target_currency = parts[1]
            api_result = call_exchange_api(base_currency, target_currency)
            final_prompt = f"The exchange rate is: {api_result}. Please compose a friendly detailed response."
        else:
            return "Sorry, I couldn't understand the currency pair."
    else:
        return assistant_reply

    final_response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": final_prompt}],
        temperature=0.1
    )

    return final_response.choices[0].message.content



# Example usage

user_question = input("Ask me about currency exchange rates: ")
answer = gpt4o_mini_currency_agent(user_question)
print("\n[Final Answer]")
print(answer)
