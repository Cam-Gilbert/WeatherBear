import re
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from zoneinfo import ZoneInfo
from datetime import datetime, timezone

''' 
User Object for WeatherBear Project. Will contain information on users name, location, unit preferance, email address, 
and a level of weather knowledge

Unit preferance will be set to imperial by default
Weather knowledge will be set to moderate by default
'''
EMAIL_REGEX = re.compile(r"^\S+@\S+\.\S+$")
_geolocator = Nominatim(user_agent="weatherbear")
_tz_finder = TimezoneFinder()

class User:
    def __init__(self, name, location, email, preferences=None):
        self.name = name
        self.location = location
        # check that email is valid
        if not EMAIL_REGEX.match(email):
            raise ValueError(f"Invalid email: {email}")
        
        self.email = email
        self.preferences = preferences or {}
        self.timeZone = self.get_time_zone()

    @property
    def units(self):
        return self.preferences.get("units", "metric")
    
    @units.setter
    def units(self, value):
        if value not in ("metric", "imperial"):
            raise ValueError("units must be either metric (C) or imperial (F)")
        self.preferences["units"] = value.lower()

    @property
    def weather_knowledge(self):
        return self.preferences.get("weather_knowledge", "moderate")
    
    @weather_knowledge.setter
    def weather_knowledge(self, value):
        if value.lower() not in ("none", "moderate", "expert"):
            raise ValueError("level of weather knowledge must be either none, moderate, or expert")
        self.preferences["weather_knowledge"] = value.lower()

    @property
    def send_hours(self):
        ''' Returns the list of hours the user wants to get emails '''
        return self.preferences.get("send_hours", [7])
    
    @send_hours.setter
    def send_hours(self, hours):
        '''Sets the list of hours (must be integers between 0-23) - Handling conversions should be handled on frontend i think '''
        if not isinstance(hours, list) or not all(isinstance(h, int) and 0 <= h <= 23 for h in hours):
            raise ValueError("send_hours must be a list of integers between 0 and 23")
        self.preferences["send_hours"] = sorted(set(hours))

    @property
    def times_sent(self):
        return self.preferences.get(["times_sent"], [])
    
    @times_sent.setter
    def times_sent(self, value):
        '''Sets the times_sent dictionary, must be a dict'''
        if not isinstance(value, dict):
            raise ValueError("times_sent must be a dictionary")
        self.preferences["times_sent"] = value

    def get_time_zone(self):
        ''' Users geopy geolocator to find users timezone based on location'''
        ## I am really not sure how this part works
        try:
            # get location
            location = _geolocator.geocode(self.location)
            if not location:
                raise ValueError(f"Coudl not geocode location at {self.location}")
            # get timezone
            tz = _tz_finder.timezone_at(lat=location.latitude, lon = location.longitude)
            if not tz:
                raise ValueError(f"Coudl not geocode location at {self.location}")
        except Exception as e:
            print(f"Failed timezone detection at {self.location}")
            # UTC default
            return "UTC"
        
    def should_get_email(self, now_utc=None):
        ''' Checks if the user should get an email based on the current time and the users time preferences
            Returns true if the user should be getting an email, false otherwise
        '''
        if now_utc is None:
            now_utc = datetime.now(timezone.utc)

        try:
            local_time = now_utc.astimezone(ZoneInfo(self.timeZone))
        except Exception as e:
            print(f"invalid time zone {self.email}: {e}")
            return False
        

        hour_key = local_time.strftime("%Y-%m-%d %H")

        if local_time.hour in self.send_hours and hour_key not in self.times_sent:
            self.record_sent_hour(hour_key)
            return True
        
        return False
    
    def record_sent_hour(self, hour_key):
        ''' Adds a new hour to the list. Maintains a queue'''
        sent = self.preferences.setdefault("times_sent", [])
        if hour_key not in sent:
            sent.append(hour_key)
            # onlt keep 5 most recent send timestamps.
            if len(sent) > 5:
                sent.pop(0)