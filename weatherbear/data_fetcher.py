from weatherbear import user
import requests
from requests.exceptions import HTTPError, Timeout, RequestException

BASE_URL = "https://api.weather.gov"
USER_AGENT = "WeatherBearApp"

class Data_Fetcher:
    def __init__(self, location):
        self.location = location

    def get_forecast(self):
        '''
        This function will use the NWS API to grab the following products
        Text Forecast Discussion for the region - check
        Forecasted High and Low Temperatures - 
        Forecasted Feels-Like Temperatures
        Forecasted Precipitation Amounts and General Timing (Whatever I can find from the API)
        Any Watches/Warnings in the area for the specific time
        '''
        # Get inital data
        coords = self.get_latlon()
        forecast_office = self.get_forecast_office(coords[0], coords[1])

        # Get Text Forecast Discussion
        url = f"{BASE_URL}/products/types/AFD/locations/{forecast_office}/latest"
        data = self.make_request(url, USER_AGENT)
        forecast_discussion = data['productText']
        forecast_discussion_time = data['issuanceTime']
        


    def get_latlon(self):
        url = f"https://nominatim.openstreetmap.org/search?q={self.location}&format=json&limit=1"
        try:
            response = requests.get(url, headers={"User-Agent": "WeatherBearApp/1.0"})
            response.raise_for_status
            data = response.json()
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
            else:
                raise ValueError("Could not find location - try a zip code or different town")
        except(HTTPError, Timeout, RequestException) as e:
            print(f"Error fetching lat/lon: {e}")
            return None
        
    def get_forecast_office(self, lat, lon):
        
        url = f"{BASE_URL}/points/{lat},{lon}"
        data = self.make_request(url, USER_AGENT)
        
        if data:
            office = data['properties']['forecastOffice']
            #gridX = data['properties']['gridX']
            #gridY = data['properties']['gridY']
            #forecast_url = data['properties']['forecast']
            office = office[-3:]
            return office
        else:
            print("Failed to Retrieve Data")

        
    def make_request(self, endpoint, user_agent):
        headers = {"User-Agent": user_agent}
        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()

        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err} - Status code: {response.status_code}")
        except Timeout as timeout_err:
            print(f"Request timed out: {timeout_err}")
        except RequestException as req_err:
            print(f"Request error: {req_err}")
        
        return None