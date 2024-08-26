import requests

def handler(event, context):
    response = requests.get("https://api.ipify.org?format=json")
    ip = response.json()

    return ip
