import requests

def getRideOtpBpp(rideId, bppDashboardHost, bppDashboardToken, shortMerchantId, city) :
    headers = {'token': bppDashboardToken, 'Content-Type': 'application/json;charset=utf-8'}
    response = requests.get(f"{bppDashboardHost}/bpp/driver-offer/{shortMerchantId}/{city}/ride/{rideId}/info", headers= headers)
    if(response.status_code == 200):
        return response.json()['rideOtp']
    else :
        print("Error: Unable to fetch otp")
        return '0000'
