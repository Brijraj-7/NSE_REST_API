import requests

auth_url = "http://localhost:8000/api/token/"

credentials = {
    "username": "brij",
    "password": "brij2510"
}

response = requests.post(auth_url, json=credentials)

if response.status_code == 200:
    access_token = response.json().get("access", None)
    
    if access_token is not None:
        print("Access Token:", access_token)
    else:
        print("Access token not found in the response.")
else:
    print("Failed to authenticate:")
    print("Status Code:", response.status_code)
    print("Response:", response.json())
