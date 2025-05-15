import requests

def get_data(videos=[]):
    # Replace with your OpenRouter API key
    API_KEY = open("key.txt").readline()

    API_URL = 'https://openrouter.ai/api/v1/chat/completions'

    # Define the headers for the API request
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    # Define the request payload (data)
    data = {
        "model": "deepseek/deepseek-chat:free",
        "messages": [{"role": "user", "content": "What is the meaning of life?"}]
    }

    # Send the POST request to the DeepSeek API
    response = requests.post(API_URL, json=data, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        return (dict(dict(response.json())['choices'][0]['message'])['content'])
    # else:
    #     print("Failed to fetch data from API. Status Code:", response.status_code)