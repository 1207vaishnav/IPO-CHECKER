import requests


url = "https://in.mpms.mufg.com/Initial_Offer/IPO.aspx/SearchOnPan"


pan = input("Enter PAN to test: ").strip().upper()


payload = {
    "clientid": "11923",
    "PAN": pan,
    "IFSC": "",
    "CHKVAL": "1",
    "token": "REPLACE_WITH_FRESH_TOKEN",
}


headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "content-type": "application/json; charset=UTF-8",
    "origin": "https://in.mpms.mufg.com",
    "referer": "https://in.mpms.mufg.com/Initial_Offer/public-issues.html",
    "x-requested-with": "XMLHttpRequest",
}


response = requests.post(
    url,
    headers=headers,
    json=payload,
    timeout=20,
)


print("\nHTTP STATUS:")
print(response.status_code)

print("\nRESPONSE:")
print(response.text)