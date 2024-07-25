from locust import HttpUser, task, between
import json
import datetime
import time
from mobileNumberGenerator  import generate_random_mobile_number

class CustomerApp(HttpUser):
    wait_time = between(1, 5)
    host = "<Host-Name-here>"
    status = "IDLE"
    @task
    def on_start(self):
        self.status = "IDLE"
        self.environment_vars = {
            "customer_merchant_id": "NAMMA_YATRI",
            "customer_chosen_vehicle_variant": "AUTO_RICKSHAW",
            "baseUrl_lts" : "<Host-Name-here>/dev/dobpp/ui",
            "baseUrl_app": "<Host-Name-here>/dev/app/v2",
            "origin-lat": 12.942247365419119,
            "origin-lon": 77.62198115675885,
            "dest-lat": 12.9325404,
            "dest-lon": 77.6287519,
        }
        self.customer_auth()
        self.customer_auth_verification()
        self.start_customer_app()

    def set_environment_variable(self, key, value):
        self.environment_vars[key] = value

    def get_environment_variable(self, key):
        return self.environment_vars.get(key, '')

    def customer_auth(self):
        mobileNumber = generate_random_mobile_number(['1','2','3'])
        self.set_environment_variable("customer_mobile_number", mobileNumber)
        payload = {
            "mobileNumber": mobileNumber,
            "mobileCountryCode": "+91",
            "merchantId": "NAMMA_YATRI"
        }
        headers = {'Content-Type': 'application/json;charset=utf-8'}
        response = self.client.post(f"{self.get_environment_variable('baseUrl_app')}/auth", json=payload, headers=headers)
        if response.status_code == 200:
            jsonData = response.json()
            self.set_environment_variable(f"customer_authId", jsonData["authId"])
        self.customer_auth_verification()
        time.sleep(0.5)

    def customer_auth_verification(self):
        mobileNumber = self.get_environment_variable("customer_mobile_number")
        auth_id = self.get_environment_variable(f"customer_authId")
        payload = {
            "otp": "7891",
            "deviceToken": "doDpYhFKfEoJgGTjTbJSDj:APA91bE8vTiYAVx89Q0vKCo0zRp7K2SyJukMjADCithsfhsd0jlNPyR18BUdav-ocA0gcMvkwp8XhE0dOkVvXou-DfSs7LHjOotRlTEX1suQQTya0wOWn7UUCTZAFip_GYMCavSDzpEE"
        }
        headers = {'Content-Type': 'application/json;charset=utf-8'}
        response = self.client.post(f"{self.get_environment_variable('baseUrl_app')}/auth/{auth_id}/verify", json=payload, headers=headers)
        if response.status_code == 200:
            jsonData = response.json()
            self.set_environment_variable(f"customer_token", jsonData["token"])
        time.sleep(0.5)



    def ride_search(self):
        current_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.set_environment_variable("current_time", current_time)
        payload = {
            "fareProductType": "ONE_WAY",
            "contents": {
                "startTime": current_time,
                "estimatedRentalDistance": 30000,
                "estimatedRentalDuration": 7200,
                "origin": {
                    "address": {
                        "area": "8th Block Koramangala",
                        "areaCode": "560047",
                        "building": "Juspay Buildings",
                        "city": "Bangalore",
                        "country": "India",
                        "door": "#444",
                        "street": "18th Main",
                        "state": "Karnataka"
                    },
                    "gps": {
                            "lat": self.get_environment_variable("origin-lat"),
                            "lon": self.get_environment_variable("origin-lon")
                        }
                },
                "destination": {
                    "address": {
                        "area": "6th Block Koramangala",
                        "areaCode": "560047",
                        "building": "Juspay Apartments",
                        "city": "Bangalore",
                        "country": "India",
                        "door": "#444",
                        "street": "18th Main",
                        "state": "Karnataka"
                    },
                    "gps": {
                            "lat": self.get_environment_variable("dest-lat"),
                            "lon": self.get_environment_variable("dest-lon")
                        }
                }
            }
        }
        mobileNumber = self.get_environment_variable("customer_mobile_number")
        headers = {'Content-Type': 'application/json;charset=utf-8', 'token': self.get_environment_variable(f"customer_token")}
        response = self.client.post(f"{self.get_environment_variable('baseUrl_app')}/rideSearch", json=payload, headers=headers)
        if response.status_code == 200:
            body = response.json()
            self.set_environment_variable("customer_searchId", body["searchId"])
            self.status = "SEARCHING"
        else:
            print("some Error in searching", response.json())
        time.sleep(0.5)


    def ride_search_estimates_or_quotes(self):
        search_id = self.get_environment_variable("customer_searchId")
        headers = {'Content-Type': 'application/json;charset=utf-8', 'token': self.get_environment_variable("customer_token")}
        response = self.client.get(f"{self.get_environment_variable('baseUrl_app')}/rideSearch/{search_id}/results", headers=headers)
        if response.status_code == 200:
            body = response.json()
            vehicle_variant = self.get_environment_variable("customer_chosen_vehicle_variant")
            retry = 5
            count = int(self.get_environment_variable(f"{search_id}") or 0)
            if count > retry:
                self.status = "IDLE"
            if len(body.get("estimates")) or len(body.get("quotes")):
                if body.get("estimates"):
                    estimate_id = next((estimate["id"] for estimate in body["estimates"] if estimate["vehicleVariant"] == vehicle_variant), None)
                    if estimate_id == None:
                        self.status = "IDLE"
                        return
                    self.set_environment_variable("customer_estimate_id", estimate_id)
                    self.status = "GOT_ESTIMATES"
                if body.get("quotes"):
                    quote_id = next((quote["onDemandCab"]["id"] for quote in body["quotes"] if quote["onDemandCab"]["vehicleVariant"] == vehicle_variant), None)
                    self.set_environment_variable("customer_quote_id", quote_id)

            else:
                count += 1
                self.set_environment_variable(f"{search_id}", str(count))
                time.sleep(5)
            time.sleep(0.5)

    def select_ride_estimate(self):
        estimate_id = self.get_environment_variable("customer_estimate_id")
        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "token": self.get_environment_variable("customer_token")
        }
        payload = { "autoAssignEnabledV2" : True, "autoAssignEnabled" : True }
        response = self.client.post(f"{self.get_environment_variable('baseUrl_app')}/estimate/{estimate_id}/select2", json=payload, headers=headers)
        if response.status_code == 200:
            self.status = "AWAITING_OTP"
        else:
            print("Select Ride Estimate", response.status_code, response.text)
            self.status = "IDLE"
        time.sleep(0.5)

    def customer_otp_for_latest_ride_booked(self):
        headers = {
            "token": self.get_environment_variable("customer_token")
        }
        response = self.client.get(f"{self.get_environment_variable('baseUrl_app')}/rideBooking/list?limit=1&onlyActive=true", headers=headers)

        if response.status_code == 200:
            body = response.json()
            retry = 5
            count = int(self.get_environment_variable("otp_count") or 1)
            if count > retry:
                self.status = "IDLE"
            if body.get("list"):
                confirmed_booking = next((booking for booking in body["list"] if booking["status"] == "CONFIRMED"), None)
                if confirmed_booking:
                    print("bookingData", confirmed_booking["bookingDetails"]["contents"])
                    rideOtp = confirmed_booking["bookingDetails"]["contents"]["otpCode"]
                    if rideOtp == None:
                        count += 1
                        self.set_environment_variable("otp_count", str(count))
                        return
                    self.set_environment_variable("ride_otp", rideOtp)
                    self.status = "AWAITING_PICKUP"

                trip_assigned_booking = next((booking for booking in body["list"] if booking["status"] == "TRIP_ASSIGNED"), None)
                if trip_assigned_booking:
                    rideOtp = trip_assigned_booking["rideList"][0]["rideOtp"]
                    rideId = trip_assigned_booking["rideList"][0]["id"]
                    bookingId = trip_assigned_booking["id"]
                    if rideOtp == None or rideId == None or bookingId == None:
                        count += 1
                        self.set_environment_variable("otp_count", str(count))
                        return
                    self.set_environment_variable("ride_otp", rideOtp)
                    self.set_environment_variable("customer_ride_id", rideId)
                    self.set_environment_variable("customer_bookingId", bookingId)
                    self.status = "AWAITING_PICKUP"

            else:
                count += 1
                time.sleep(4)
                self.set_environment_variable("otp_count", str(count))
        time.sleep(0.5)

    def start_customer_app(self):
        if self.status == "IDLE":
            self.ride_search()
        elif self.status == "SEARCHING":
            self.ride_search_estimates_or_quotes()
        elif self.status == "GOT_ESTIMATES":
            self.select_ride_estimate()
        elif self.status == "AWAITING_OTP":
            self.customer_otp_for_latest_ride_booked()
        elif self.status == "AWAITING_PICKUP":
            self.customer_otp_for_latest_ride_booked()

        self.start_customer_app()
