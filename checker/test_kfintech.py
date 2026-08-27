import requests


url = "https://0uz601ms56.execute-api.ap-south-1.amazonaws.com/prod/api/query"


pan = input("Enter PAN to test: ").strip().upper()


headers = {
    "accept": "application/json, text/plain, */*",
    "client_id": "29849673370",
    "reqparam": pan,
}


params = {
    "type": "pan"
}


response = requests.get(
    url,
    headers=headers,
    params=params,
    timeout=20
)


print("\nHTTP STATUS:")
print(response.status_code)


print("\nRESPONSE:")
print(response.text)