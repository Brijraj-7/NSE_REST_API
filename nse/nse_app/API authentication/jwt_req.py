import requests
auth_url = "http://localhost:8000/api/token/"

credentials = {
    "username": "brij",
    "password": "brij2510"
}

response = requests.post(auth_url, json=credentials)
access_token = response.json().get("access", None)

if access_token:
    print("Access token obtained successfully")
else:
    print("Failed to obtain access token.")
    exit()

api_url = "http://localhost:8000/api/indexes/1/?date=2024-03-15"
headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(api_url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print("Data:", data)
else:
    print("Failed to access the API endpoint.")
    print("Status Code:", response.status_code)
    print("Response:", response.json())
