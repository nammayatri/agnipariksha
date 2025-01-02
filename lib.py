from mobileNumberGenerator import generate_random_mobile_number
import requests



dashboard_token =  "<token>"
dashboard_url = "http://localhost:8018"
merchant = "favorit0-0000-0000-0000-00000favorit"
city = "Bangalore"

def getRideOtpBpp(rideId) :
    headers = {'token': dashboard_token, 'Content-Type': 'application/json;charset=utf-8'}
    response = requests.get(f"{dashboard_url}/api/dev/bpp/driver-offer/{merchant}/{city}/ride/{rideId}/info", headers= headers)
    if(response.status_code == 200):
        return response.json()['rideOtp']
    else :
        return '0000'
