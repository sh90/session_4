#pip install requests
import requests

url = "https://imdb236.p.rapidapi.com/imdb/autocomplete"
headers = {
    'x-rapidapi-host': 'imdb236.p.rapidapi.com',
    'x-rapidapi-key': '766ea387a6msh84ff46479ed9b4bp18b495jsna547d73e1ef5'
}
params = {
    'query': 'matrix'
}

response = requests.get(url, headers=headers, params=params)

# Print the response content (for debugging purposes)
print(response.json())
