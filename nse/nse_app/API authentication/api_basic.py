import requests
from requests.auth import HTTPBasicAuth

def main():
    url = 'http://localhost:8000/api/indexes/2/?date=2024-02-19'
    username = 'brij'
    password = 'brij2510'
    
    response = requests.get(url, auth=HTTPBasicAuth(username, password))
    
    if response.status_code == 200:
        print("Request successful:")
        print(response.json())
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.text)  # Print response content for error cases

if __name__ == "__main__":
    main()