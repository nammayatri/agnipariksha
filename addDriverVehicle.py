import requests
import random
import string
import os


def generate_random_registration_number():
    letters1 = ''.join(random.choices(string.ascii_uppercase, k=2))
    digits = ''.join(random.choices(string.digits, k=2))
    letters2 = ''.join(random.choices(string.ascii_uppercase, k=2))
    digits2 = ''.join(random.choices(string.digits, k=4))
    return f"{letters1}{digits}{letters2}{digits2}"

def enable_driver(driverId, bppDashboardHost, bppDashboardToken, shortMerchantId, city):
    url = f"{bppDashboardHost}/bpp/driver-offer/{shortMerchantId}/{city}/driver/{driverId}/enable"
    headers = {
        "token": bppDashboardToken,
        "Content-Type": "application/json",
        "Authorization": "Bearer token"
    }
    response = requests.post(url, headers=headers)
    print(response.status_code)
    print(response.text)

def add_vehicle(driverId, bppDashboardHost, bppDashboardToken, shortMerchantId, city):
    url = f"{bppDashboardHost}/bpp/driver-offer/{shortMerchantId}/{city}/driver/{driverId}/addVehicle"
    headers = {
        "token": bppDashboardToken,
        "Content-Type": "application/json",
        "Authorization": "Bearer token"
    }
    DRIVER_VEHICLE_VARIANT = os.getenv('DRIVER_VEHICLE_VARIANT'); DRIVER_VEHICLE_VARIANT = DRIVER_VEHICLE_VARIANT if DRIVER_VEHICLE_VARIANT else "<driver-vehicle-variant-here>"
    DRIVER_VEHICLE_CLASS = os.getenv('DRIVER_VEHICLE_CLASS'); DRIVER_VEHICLE_CLASS = DRIVER_VEHICLE_CLASS if DRIVER_VEHICLE_CLASS else "<driver-vehicle-class-here>"
    DRIVER_VEHICLE_CAPACITY = os.getenv('DRIVER_VEHICLE_CAPACITY'); DRIVER_VEHICLE_CAPACITY = DRIVER_VEHICLE_CAPACITY if DRIVER_VEHICLE_CAPACITY else "<driver-vehicle-capacity-here>"
    data = {
        "variant": DRIVER_VEHICLE_VARIANT,
        "registrationNo": generate_random_registration_number(),
        "vehicleClass": DRIVER_VEHICLE_CLASS,
        "capacity": int(DRIVER_VEHICLE_CAPACITY),
        "colour": "Green",
        "energyType": "Petrol",
        "model": "Bajaj",
        "make": "PAYTM",
        "driverName": "Text"
    }

    response = requests.post(url, headers=headers, json=data)
    print(response.status_code)
    print(response.text)
    enable_driver(driverId, bppDashboardHost, bppDashboardToken, shortMerchantId, city)
