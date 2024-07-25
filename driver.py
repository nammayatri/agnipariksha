from locust import HttpUser, task, between
import json
import datetime
import time
from lib import getRideOtpBpp
from addDriverVehicle import add_vehicle
from mobileNumberGenerator  import generate_random_mobile_number



class DriverApp(HttpUser):

    wait_time = between(1, 5)
    host = "<Host-Url-Here>"
    status = "IDLE"
    @task
    def on_start(self):
        self.status = "IDLE"
        self.environment_vars = {
            "driver_merchant_id": "7f7896dd-787e-4a0b-8675-e9e6fe93bb8f",
            "baseURL_namma_P" : "<Host-Url-Here>/dev/dobpp/ui",
            "baseUrl_lts" : "<Host-Url-Here>/dev/dobpp/ui",
            "origin-lat": 12.942247365419119,
            "origin-lon": 77.62198115675885,
            "dest-lat": 12.9325404,
            "dest-lon": 77.6287519,
        }
        self.auth()
        self.auth_verification()
        self.get_profile()
        self.startDriverApp()



    def set_environment_variable(self, key, value):
        self.environment_vars[key] = value

    def get_environment_variable(self, key):
        return self.environment_vars.get(key, '')

    def auth(self):
        mobileNumber = generate_random_mobile_number(['7','8','9'])
        self.set_environment_variable("mobile_number", mobileNumber)
        payload = {
            "mobileNumber": mobileNumber,
            "mobileCountryCode": "+91",
            "merchantId": self.get_environment_variable("driver_merchant_id")
        }
        headers = {'Content-Type': 'application/json;charset=utf-8'}
        response = self.client.post(f"{self.get_environment_variable('baseURL_namma_P')}/auth", json=payload, headers=headers)
        if response.status_code == 200:
            jsonData = response.json()
            self.set_environment_variable("driver_authId", jsonData["authId"])
        time.sleep(0.5)


    def auth_verification(self):
        auth_id = self.get_environment_variable("driver_authId")
        payload = {
            "otp": "7891",
            "deviceToken": "doDpYhFKfEoJgGTjTbJSDj:APA91bE8vTiYAVx89Q0vKCo0zRp7K2SyJukMjADCithsfhsd0jlNPyR18BUdav-ocA0gcMvkwp8XhE0dOkVvXou-DfSs7LHjOotRlTEX1suQQTya0wOWn7UUCTZAFip_GYMCavSDzpEE"
        }
        headers = {'Content-Type': 'application/json;charset=utf-8'}
        response = self.client.post(f"{self.get_environment_variable('baseURL_namma_P')}/auth/{auth_id}/verify", json=payload, headers=headers)
        if response.status_code == 200:
            jsonData = response.json()
            add_vehicle(jsonData["person"]["id"])
            self.set_environment_variable("driver_token", jsonData["token"])
        time.sleep(0.5)

    def set_online_offline(self):
        headers = {'Accept': 'application/json;charset=utf-8', 'token': self.get_environment_variable("driver_token")}
        response = self.client.post(f"{self.get_environment_variable('baseURL_namma_P')}/driver/setActivity?active=true&mode=\"ONLINE\"", headers=headers)
        time.sleep(0.5)

    def get_profile(self):
        headers = {'token': self.get_environment_variable("driver_token")}
        response = self.client.get(f"{self.get_environment_variable('baseURL_namma_P')}/driver/profile", headers=headers)
        if response.status_code == 200:
            body = response.json()
            self.set_environment_variable("mId", body["organization"]["id"])
            self.set_environment_variable("vt", body["linkedVehicle"]["variant"])
            self.set_environment_variable("driver_id", body["id"])
            self.set_environment_variable("dm", body["mode"])
        time.sleep(0.5)

    def set_driver_location(self):
        headers = {
            'Content-Type': 'application/json;charset=utf-8',
            'Accept': 'application/json;charset=utf-8',
            'vt': self.get_environment_variable("vt"),
            'mId': self.get_environment_variable("mId"),
            'dm': self.get_environment_variable("dm"),
            'token': self.get_environment_variable("driver_token")
        }
        current_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.set_environment_variable("current_time", current_time)

        payload = [
            {
                "pt": {
                    "lat": self.get_environment_variable("origin-lat"),
                    "lon": self.get_environment_variable("origin-lon")
                },
                "ts": self.get_environment_variable("current_time"),
                "acc": 1,
                "v": 5
            } for _ in range(10)
        ]
        response = self.client.post(f"{self.get_environment_variable('baseUrl_lts')}/driver/location", json=payload, headers=headers)
        time.sleep(2)

    def nearby_ride_request(self):
        headers = {
            "Accept": "application/json;charset=utf-8",
            "token": self.get_environment_variable("driver_token")
        }
        response = self.client.get(f"{self.get_environment_variable('baseURL_namma_P')}/driver/nearbyRideRequest", headers=headers)
        if response.status_code == 200:
            body = response.json()
            if body.get("searchRequestsForDriver") and (len(body["searchRequestsForDriver"]) != 0):
                searchRequestId = body["searchRequestsForDriver"][0]["searchRequestId"]
                if(searchRequestId ==None):
                    return
                self.set_environment_variable("driver_search_request_id", searchRequestId)
                self.status = "QUOTE_OFFERED"

        elif response.status_code == 400:
            print("No nearby ride request 400 error")
            self.status = "IDLE"
        elif response.status_code == 401:
            print("No nearby ride request 401 error")
            self.auth()
            self.auth_verification()
            self.status = "IDLE"
        else:
            print(f"No nearby ride request {response.status_code} error")
            self.status = "IDLE"
        time.sleep(0.5)

    def quote_customer_for_ride(self):
        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Accept": "application/json;charset=utf-8",
            "token": self.get_environment_variable("driver_token")
        }
        srid = self.get_environment_variable("driver_search_request_id")
        payload = {
            "searchRequestId": srid,
            "response": "Accept"
        }
        response = self.client.post(f"{self.get_environment_variable('baseURL_namma_P')}/driver/searchRequest/quote/respond", json=payload, headers=headers)

        if response.status_code == 200:
            self.status = "REACHING_PICKUP"
        elif response.status_code == 400:
            print("quote offer 400 error", response.json(), srid)
            self.status = "IDLE"
        elif response.status_code == 401:
            print("quote offer 401 error", response.json(), srid)
            self.status = "IDLE"
        else:
            print(f"quote offer {response.status_code} error", response.json(), srid)
            self.status = "IDLE"
        time.sleep(0.5)

    def driver_ride_id_of_newly_booked_ride(self):
        headers = {
            "token": self.get_environment_variable("driver_token")
        }
        response = self.client.get(f"{self.get_environment_variable('baseURL_namma_P')}/driver/ride/list?limit=1", headers=headers)

        if response.status_code == 200:
            body = response.json()
            new_ride = next((ride for ride in body["list"] if ride["status"] == "NEW"), None)
            if new_ride!=None and new_ride != "" :
                self.set_environment_variable("driver_ride_id", new_ride["id"])
        time.sleep(0.5)


    def driver_start_ride_by_entering_otp(self):
        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "token": self.get_environment_variable("driver_token")
        }
        payload = {
            "rideOtp": getRideOtpBpp(self.get_environment_variable("driver_ride_id")),
            "point": {
                "lat": self.get_environment_variable("origin-lat"),
                "lon": self.get_environment_variable("origin-lon")
            },
            "odometer": None
        }
        ride_id = self.get_environment_variable("driver_ride_id")
        retry = 5
        count = int(self.get_environment_variable("rstart_count") or 0)
        if ride_id == None or ride_id == "":
            count += 1
            self.set_environment_variable("rstart_count", count)
            return
        response = self.client.post(f"{self.get_environment_variable('baseURL_namma_P')}/driver/ride/{ride_id}/start", json=payload, headers=headers)
        if(count>retry):
            self.status = "REACHING_PICKUP"
        elif response.status_code == 200:
            self.status = "ON_RIDE"
        else:
            count += 1
            self.set_environment_variable("rstart_count", count)
            print(f"Start Ride - Failed with status code {response.status_code}", response.json(), ride_id)
        time.sleep(0.5)

    def driver_ride_completion(self):
        headers = {
            "token": self.get_environment_variable("driver_token")
        }
        payload = {
            "point": {
                "lat": self.get_environment_variable("dest-lat"),
                "lon": self.get_environment_variable("dest-lon")
            }
        }
        ride_id = self.get_environment_variable("driver_ride_id")
        response = self.client.post(f"{self.get_environment_variable('baseURL_namma_P')}/driver/ride/{ride_id}/end", json=payload, headers=headers)
        retry = 5
        count = int(self.get_environment_variable("rend_count") or 0)
        if(count>retry):
            self.status = "IDLE"
        elif response.status_code == 200:
            self.status = "IDLE"
        else:
            count += 1
            self.set_environment_variable("rend_count", count)
            print(f"Ride Completion - Failed with status code {response.status_code}", response.json())

        time.sleep(0.5)


    def startDriverApp(self):
        if(self.status == "IDLE"):
            self.set_online_offline()
            self.set_driver_location()
            self.nearby_ride_request()
        elif(self.status == "QUOTE_OFFERED"):
            self.quote_customer_for_ride()
        elif(self.status == "REACHING_PICKUP"):
            self.driver_ride_id_of_newly_booked_ride()
            self.driver_start_ride_by_entering_otp()
        elif(self.status == "ON_RIDE"):
            self.driver_ride_completion()
        self.startDriverApp()
