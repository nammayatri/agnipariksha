import requests
import random
import string


merchantId = 'NAMMA_YATRI_PARTNER'
# driverId = 'favorit-suv-000000000000000000000000'
token = "<dashboard-token>"


def generate_random_registration_number():
    letters1 = ''.join(random.choices(string.ascii_uppercase, k=2))
    digits = ''.join(random.choices(string.digits, k=2))
    letters2 = ''.join(random.choices(string.ascii_uppercase, k=2))
    digits2 = ''.join(random.choices(string.digits, k=4))
    return f"{letters1}{digits}{letters2}{digits2}"

def enable_driver(driverId):
    print("Driver ID is: ", driverId)
    print("token is: ", token)
    print("merchantId is: ", merchantId)
    url = f"https://dashboard.integ.moving.tech/api/dev/bpp/driver-offer/{merchantId}/Kochi/driver/{driverId}/enable"
    headers = {
        "token": token,
        "Content-Type": "application/json",
        "Authorization": "Bearer token"
    }
    response = requests.post(url, headers=headers)
    print("response hai: ", response.status_code)
    print(response.json())

def add_vehicle(driverId):
    url = f"https://dashboard.integ.moving.tech/api/dev/bpp/driver-offer/{merchantId}/std:0484/driver/{driverId}/addVehicle"
    headers = {
        "token": token,
        "Content-Type": "application/json",
        "Authorization": "Bearer token"
    }
    data = {
        "variant": "AUTO_RICKSHAW",
        "registrationNo": generate_random_registration_number(),
        "vehicleClass": "3WT",
        "capacity": 3,
        "colour": "Green",
        "energyType": "Petrol",
        "model": "Bajaj",
        "make": "PAYTM",
        "driverName": "Text"
    }

    response = requests.post(url, headers=headers, json=data)
    print(response.status_code)
    print(response.json())
    enable_driver(driverId)
