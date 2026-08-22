import requests

RT_URL = "https://api.data.gov.my/gtfs-realtime/vehicle-position/prasarana?category=rapid-bus-kl"
STATIC_URL = "https://api.data.gov.my/gtfs-static/prasarana?category=rapid-bus-kl"

rt_response = requests.get(RT_URL)
static_response = requests.get(STATIC_URL)

print("Realtime status:", rt_response.status_code)
print("Realtime type:", rt_response.headers.get("Content-Type"))

print("Static status:", static_response.status_code)
print("Static type:", static_response.headers.get("Content-Type"))