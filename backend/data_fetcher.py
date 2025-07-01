import requests
import math
from requests.exceptions import HTTPError, Timeout, RequestException

BASE_URL = "https://api.weather.gov"
''' The base url for all nws api interactions'''
USER_AGENT = "WeatherBearApp"
''' Username for interacting with NWS and openstreetmap API'''

class Data_Fetcher:
    '''
    Data_Fetcher Class. It handles all of the interactions with the NWS api and pulling data. Contains several
    methods but the main method is get_forecast(), it returns all of the data that is needed to generate emails 
    and interact with the LLM
    '''
    def __init__(self, location, units):
        '''
        Data_Fetcher object initialization method (constructor)

        @param location users zipcode, city, address, etc... 
        @param units used to specify units when pulling from nws
        '''
        self.location = location
        self.units = units 

    def get_forecast(self):
        '''
        Main function of this class. This function will use the NWS API to grab the following products
        Text Forecast Discussion for the region
        Active Alerts (Warnings and Watches)
        Observations from the closest station to the users location
        Hourly forecast dictionary including several variables (temp, dewpt, relative humidity, cloud level, etc...)

        @return forecast_discussion string containing the most recent forecast discussion
        @return organized_alerts list of dictionarys (1 dict for every alert) containing info on active alerts in the area
        @return daily_forecasts list of dictionarys (1 dict for every forecast period) containing the basic daily forecast information 
        @return obs_data dictionary containing information on the observations from the closest station. 
        @return hourly_forecast dictionary containing a list of periods with hourly forecast data (temp, dewpt, relative humidty, etc..)
        '''
        # Get inital data
        coords = self.get_latlon()
        if coords is None:
            print("Failed to get coords")
            return
        
        forecast_office, gridX, gridY, zone_url, obs_station = self.get_forecast_office(coords[0], coords[1])

        # Get Text Forecast Discussion - May consider trimming this string at the start, save tokens passing into LLM $$$
        text_url = f"{BASE_URL}/products/types/AFD/locations/{forecast_office}/latest"
        text_data = self.make_request(text_url, USER_AGENT)
        forecast_discussion = text_data['productText']
        forecast_discussion_time = text_data['issuanceTime']

        # Get Watches / Warnings
        zone_id = zone_url[-6:]
        watch_url = f"{BASE_URL}/alerts/active/zone/{zone_id}"
        watch_data = self.make_request(watch_url, USER_AGENT)
        alert_data = watch_data['features']

        ## get all import info out of json
        organized_alerts = []
        for alert in alert_data:
            prop = alert['properties']
            params = prop.get('parameters', {})

            # Grab most everything because not sure what we will need just yet
            organized_alert = {
                'event': prop.get('event'),
                'sender_name': prop.get('senderName'),
                'area': prop.get('areaDesc').split('; '),
                'severity': prop.get('severity'),
                'certainty': prop.get('certainty'),
                'urgency': prop.get('urgency'),
                'status': prop.get('status'),
                'message_type': prop.get('messageType'),
                'onset': prop.get('onset'),
                'ends': prop.get('ends'),
                'effective': prop.get('effective'),
                'expires': prop.get('expires'),
                'headline': prop.get('headline'),
                'description': prop.get('description'),
                'instruction': prop.get('instruction'),
                'response': prop.get('response'),
                'web': prop.get('web'),
                'vtec': params.get('VTEC', [None])[0], 
            }

            
            organized_alerts.append(organized_alert)
        # Only care about alerts affecting our zone irl
        organized_alerts = [a for a in organized_alerts if zone_id in alert['properties']['geocode']['UGC']]

        # Get Forecasts
        url = f"{BASE_URL}/gridpoints/{forecast_office}/{gridX},{gridY}/forecast"
        url = self.check_units(url)        
        forecast_data = self.make_request(url, USER_AGENT)
        daily_forecasts = []

        # Extract info
        for period in forecast_data['properties']['periods']:
            forecast = {
                'name': period['name'],
                'start_time': period['startTime'],
                'end_time': period['endTime'],
                'is_daytime': period['isDaytime'],
                'temperature': period['temperature'],
                'temperature_unit': period['temperatureUnit'],
                'precipitation_chance': period['probabilityOfPrecipitation']['value'],
                'wind_speed': period['windSpeed'],
                'wind_direction': period['windDirection'],
                'short_forecast': period['shortForecast'],
                'detailed_forecast': period['detailedForecast'],
                'icon': period['icon']
            }
            daily_forecasts.append(forecast)

        # Get hourly forecasts
        url = f"{BASE_URL}/gridpoints/{forecast_office}/{gridX},{gridY}/forecast/hourly"
        url = self.check_units(url)
        hourly_forecast = self.make_request(url, USER_AGENT)

        # Get closest observations
        obs_id = obs_station['properties']['stationIdentifier']
        url = f"{BASE_URL}/stations/{obs_id}/observations/latest"
        obs_data = self.make_request(url, USER_AGENT)

        return forecast_discussion, organized_alerts, daily_forecasts, obs_data, hourly_forecast
        

    def get_latlon(self):
        '''
        Use the open street map api to get a users lat/lon based on an inputted city/zipcode

        @return the station lat lon in a tuple --> data[0] = 'lat' data[1] = 'lon'
        '''
        url = f"https://nominatim.openstreetmap.org/search?q={self.location}&format=json&limit=1"

        try:
            # send a request to api
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
        '''
        Makes a request to the NWS api and gathers the closest forecast office, the stations grid points,
        the closest obs station, and the warning zone info

        @param lat latitude of user
        @param lon longitude of user
        @return office the forecast office
        @return gridX stations x grid point
        @return gridY stations y grid point
        @return zone_url the warning zone
        @return closest_station the closest observation station
        '''
        url = f"{BASE_URL}/points/{lat},{lon}"
        data = self.make_request(url, USER_AGENT)
       
        # pull important station information
        if data:
            office = data['properties']['forecastOffice']
            gridX = data['properties']['gridX']
            gridY = data['properties']['gridY']
            zone_url = data['properties']['forecastZone']
            obs_stations = self.make_request(data['properties']['observationStations'], USER_AGENT)
            office = office[-3:]
            
            closest_station = None
            min_dist = math.inf
            # find which obs station is closest to provided user location
            for station in obs_stations['features']:
                station_coords = station['geometry']['coordinates']
                dist = self.haversine(lon, lat, station_coords[0], station_coords[1])
                if dist < min_dist:
                    min_dist = dist
                    closest_station = station

            return office, gridX, gridY, zone_url, closest_station
        else:
            print("Failed to Retrieve Data")

        
    def make_request(self, endpoint, user_agent):
        '''
        Helper function that makes api requests to NWS API

        @param endpoint the url of api at desired point
        @param user_agent a username that is used when calling api, private stored in .env
        '''
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
    
    def haversine(self, lon1, lat1, lon2, lat2):
        '''
        Haversine function to used determine the distance to the closest station

        @param lon1 - longitude of user location
        @param lat1 - latitude of user location
        @param lon2 - longitude of station 1
        @param lat2 - latitude of station 1
        @return the distance between points
        '''
        lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

        dlon = lon2- lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371
        return c * r
    
    def check_units(self, url):
        ''' 
        Checks units preference and pulls si units if necessary.
        
        @param the url of the api request link
        '''
        if self.units == "metric":
            # string added onto api link that modifys what units the data is pulled in
            url += "?units=si"

        return url