import requests

def main():
    url = 'http://localhost:8000/api/indexes/1/?date=2024-03-15'
    token='ce6a9dd7831999f60020d9fd070cd80efe6e14f9'

    headers = {
    'Authorization': f'token {token}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("Request successful:")
        print(response.json())
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.text)  # Print response content for error cases

if __name__ == "__main__":
    main()
