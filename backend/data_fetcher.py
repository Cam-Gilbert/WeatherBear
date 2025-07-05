import requests
import xmltodict
import requests
import re
import math
import shutil
import zipfile
import os
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, Timeout, RequestException

BASE_URL = "https://api.weather.gov"
''' The base url for all nws api interactions'''
USER_AGENT = "WeatherBearApp"
''' Username for interacting with NWS and openstreetmap API'''

''' Location Exception that will bubble up if there is a location error '''
class LocationError(Exception): pass
''' Forecast exception that will bubble up if there is a error getting forecast information '''
class ForecastError(Exception): pass

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
            raise LocationError("Could not find location. Please try a different input.")
        
        try:
            print(coords)
            forecast_office, gridX, gridY, zone_url, obs_station = self.get_forecast_office(coords[0], coords[1])
            if not forecast_office:
                raise ForecastError("Could not get forecast office info from NWS.")
        except Exception as e:
            print(f"Detailed ForecastError: {e}") 
            raise ForecastError("That location is likely outside the NWS coverage area or does not exist. Please try a different location in the U.S. May need to be more specific Ex: Raleigh, NC or Denver, CO")

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
        url = f"https://nominatim.openstreetmap.org/search?q={self.location}&format=json&limit=1&countrycodes=us"

        try:
            parts = self.location.split(",")
            if len(parts) == 2:
                lat_str = parts[0].strip()
                lon_str = parts[1].strip()

                try:
                    lat = float(lat_str)
                    lon = float(lon_str)

                    # Sanity Check
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        return lat, lon
                except ValueError:
                    pass  # Not a valid coordinate pair, fall through to geocoding

            # send a request to api
            response = requests.get(url, headers={"User-Agent": "WeatherBearApp/1.0"}, timeout = 10)
            response.raise_for_status()
            data = response.json()

            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
            else:
                raise LocationError("Could not find that location. Try a different location or a more specific name like 'Raleigh, NC'.")
        except(HTTPError, Timeout, RequestException) as e:
            print(f"Error fetching lat/lon: {e}")
            return None
        
    def get_tropical_data(self):
        '''
        Function that may be used to pull data for a "Tropical Tab" Currently only used for exploration and testing
        '''
        rss_urls = {
            "Atlantic": "https://www.nhc.noaa.gov/index-at.xml",
            "Central_Pacific": "https://www.nhc.noaa.gov/index-cp.xml",
            "Eastern_Pacific": "https://www.nhc.noaa.gov/index-ep.xml"
        }

        tropical_data = {}

        storm_codes = []

        for region, rss_url in rss_urls.items():
            try:
                response = requests.get(rss_url, headers={"User-Agent": USER_AGENT}, timeout=15)
                response.raise_for_status()
                data = xmltodict.parse(response.content)

            except requests.exceptions.HTTPError as e:
                print(f"HTTP error fetching tropical data: {e}")
            except requests.exceptions.Timeout:
                print("Timeout occurred while fetching tropical data.")
            except requests.exceptions.RequestException as e:
                print(f"Request error fetching tropical data: {e}")
            except Exception as e:
                print(f"Unexpected error parsing tropical data: {e}")

            # Get items to iterate thru, this is like tropical weather outlook, public advisorys, summaries, etc...
            items = data['rss']['channel']['item']

            storms = {}
    
            # need to iterate thru each item in order to collect storm info and sort it by name
            for item in items:
                cyclone_info = item.get('nhc:Cyclone', {})
                storm_name = cyclone_info.get('nhc:name')
                storm_codes.append({
                    "name": cyclone_info.get('nhc:name'),
                    "code": cyclone_info.get('nhc:atcf'),
                    "region": region
                })

                if not storm_name:
                    # try and find any non-named invests or any system that doesn't have a nhc:name for whatever reason
                    for prefix in ['Tropical Storm', 'Hurricane', 'Tropical Depression', 'Invest']:
                        if prefix in item['title']:
                            try:
                                parts = item['title'].split()
                                prefix_words = prefix.split()
                                idx = parts.index(prefix_words[-1])
                                storm_name = (parts[idx + 1]).strip().title()
                                break
                            except (ValueError, IndexError):
                                pass

                title_lower = item['title'].lower()

                # need to process local statments separetely because they do not contain a storm name in the traditional manner. So in order to keep logic
                # in tact I am simply moving this out of the messy block that builds my dictionary. 
                if 'local statement' in title_lower:
                    city = item['title'].replace('Local Statement for', '').strip()
                    full_text = self.fetch_local_statement_text(item['link'])

                    # Find the keywords at the beginning of the discussion
                    if not storm_name:
                        lines = full_text.splitlines()[:30]
                        pattern = re.compile(r'(Tropical Storm|Hurricane|Tropical Depression|Invest)\s+(\w+)', re.IGNORECASE)
                        for line in lines:
                            match = pattern.search(line)
                            if match:
                                storm_name = match.group(2).title()
                                break  
                    
                    if not storm_name:
                        storm_name = "Unknown"

                    if storm_name not in storms:
                        storms[storm_name] = {
                            'summary': None,
                            'advisories': [],
                            'discussions': [],
                            'local_statements': []
                        }

                    storms[storm_name]['local_statements'].append({
                        'city': city,
                        'title': item.get('title'),
                        'pubDate': item.get('pubDate'),
                        'description': item.get('description'),
                        'full_text': full_text,
                    })

                    continue

                if not storm_name:
                    continue  # No storm name found

                if storm_name not in storms:
                    storms[storm_name] = {
                        'summary': None,
                        'advisories': [],
                        'discussions': [],
                        'local_statements': []
                    }

                if 'summary' in title_lower:
                    storms[storm_name]['summary'] = item['nhc:Cyclone']
                elif 'advisory' in title_lower:
                    storms[storm_name]['advisories'].append({
                        'title': item.get('title'),
                        'pubDate': item.get('pubDate'),
                        'description': item.get('description')
                    })
                elif 'discussion' in title_lower:
                    storms[storm_name]['discussions'].append({
                        'title': item.get('title'),
                        'pubDate': item.get('pubDate'),
                        'description': item.get('description')
                    })

            tropical_data[region] = storms

        # Now download overall region discussions for summaries
        region_codes = {
            "Atlantic": "AT",
            "Eastern_Pacific": "EP",
            "Central_Pacific": "PQ"
        }

        for region_name, region_code in region_codes.items():
            try:    
                twd_url = f"{BASE_URL}/products/types/TWD/locations/{region_code}/latest"
                twd_data = self.make_request(twd_url, USER_AGENT)

                twd_discussion = {
                    'discussion': twd_data.get('productText'),
                    'issued': twd_data.get('issuanceTime'),
                    'headline': twd_data.get('headline')
                }

                tropical_data.setdefault(region_name, {})
                tropical_data[region_name]['twd_discussions'] = [twd_discussion]

            except Exception as e:
                print(f"Error fetching TWD for {region_name}: {e}")
                tropical_data.setdefault(region_name, {})
                tropical_data[region_name]['twd_discussions'] = []


        #  download shape files for each storm and add their path to the dictionary in the correct location
        base_dir = os.path.dirname(os.path.abspath(__file__))  # current script directory
        storms_folder = os.path.abspath(os.path.join(base_dir, "..", "mnt", "storms"))

        # delete all old files and folders in storms folder
        if os.path.exists(storms_folder):
            shutil.rmtree(storms_folder)
        os.makedirs(storms_folder, exist_ok=True)

        for storm in storm_codes:
            code = storm.get("code")
            name = storm.get("name")
            region = storm.get("region")

            if not code:
                continue  # skip storms without code

            # Sanitize storm name to be a valid folder name
            storm_folder_path = os.path.join(storms_folder, code)
            os.makedirs(storm_folder_path, exist_ok=True)

            zip_url = f"https://www.nhc.noaa.gov/gis/forecast/archive/{code.lower()}_5day_latest.zip"
            local_zip_path = os.path.join(storm_folder_path, f"{code}_5day_latest.zip")

            try:
                resp = requests.get(zip_url, headers={"User-Agent": USER_AGENT}, timeout=20)
                resp.raise_for_status()

                # Save the zip file
                with open(local_zip_path, "wb") as f:
                    f.write(resp.content)
                print(f"Downloaded shapefile zip for {name} ({code}) to {local_zip_path}")

                # Unzip the contents into the storm folder
                with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(storm_folder_path)
                print(f"Extracted shapefile for {name} ({code}) to {storm_folder_path}")

                # Optionally, delete the zip after extraction if you want to save space
                os.remove(local_zip_path)

                # Update tropical_data with the folder path of the extracted shapefile
                tropical_data.setdefault(region, {})
                tropical_data[region].setdefault(name, {})
                tropical_data[region][name]["shapefile_path"] = storm_folder_path

            except Exception as e:
                print(f"Failed to download or extract shapefile for {name} ({code}): {e}")

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
            response = requests.get(endpoint, headers=headers, timeout=15)
            response.raise_for_status()
            return response.json()
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err} - Status code: {response.status_code}")
            raise ForecastError(f"NWS returned an error: {http_err}")
        except Timeout as timeout_err:
            print(f"Request timed out: {timeout_err}")
            raise ForecastError("The request to NWS timed out.")
        except RequestException as req_err:
            print(f"Request error: {req_err}")
            raise ForecastError(f"An error occurred while making the request: {req_err}")
    
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
    
    def fetch_local_statement_text(self, url):
        '''
        Fetches NHC local statements from the url 
        '''
        try:
            response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
            response.raise_for_status()
            html = response.text
            
            # Parse the HTML
            soup = BeautifulSoup(html, "html.parser")
            
            # Extract the main local statement text inside the <pre> tag under div.textproduct
            pre_tag = soup.select_one("div.textproduct > pre")
            if pre_tag:
                clean_text = pre_tag.get_text(separator="\n", strip=True)
                return clean_text
            else:
                # fallback if no <pre> found, return raw text
                return html.strip()
            
        except Exception as e:
            print(f"Failed to fetch local statement from {url}: {e}")
            return None