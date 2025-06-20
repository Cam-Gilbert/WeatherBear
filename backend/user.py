import re
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import requests
import json
import os
from requests.exceptions import HTTPError, Timeout, RequestException
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
USER_PATH = "/mnt/data/users.json"

class User:
    def __init__(self, name, location, email, preferences = None, timeZone = None):
        self.name = name
        self.location = location
        # check that email is valid
        if not EMAIL_REGEX.match(email):
            raise ValueError(f"Invalid email: {email}")
        
        self.email = email
        self.preferences = preferences or {}
        self.timeZone = timeZone or self.get_time_zone()

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
        if value.lower() not in ("none", "moderate", "expert", "no_summary"):
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
        return self.preferences.get("times_sent", [])
    
    @times_sent.setter
    def times_sent(self, value):
        '''Sets the times_sent dictionary, must be a dict'''
        if not isinstance(value, dict):
            raise ValueError("times_sent must be a dictionary")
        self.preferences["times_sent"] = value

    def get_time_zone(self):
        '''Uses OpenStreetMap API to get lat/lon and then TimezoneFinder to get timezone'''
        try:
            url = f"https://nominatim.openstreetmap.org/search?q={self.location}&format=json&limit=1"
            response = requests.get(url, headers={"User-Agent": "WeatherBearApp/1.0"})
            response.raise_for_status()
            data = response.json()

            if not data:
                raise ValueError(f"Could not find location for: {self.location}")

            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])

            tz = _tz_finder.timezone_at(lat=lat, lng=lon)
            if not tz:
                raise ValueError(f"Could not determine timezone for location: {self.location}")

            return tz

        except (HTTPError, Timeout, RequestException, ValueError) as e:
            print(f"⚠️ Failed timezone detection at {self.location}: {e}")
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

    def to_dict(self):
        ''' Returns a dictionary representation of the user '''
        return {
            "name": self.name,
            "location": self.location,
            "email": self.email,
            "preferences": self.preferences,
            "timeZone": self.timeZone
        }

def load_users():
    ''' Loads users from the database '''
    if not os.path.exists(USER_PATH):
        print("creating empty one")
        with open(USER_PATH, "w") as f:
            json.dump([], f)

    try:
        with open(USER_PATH, "r") as f:
            users_data = json.load(f)
        return [User(
            name=user_dict["name"],
            location=user_dict["location"],
            email=user_dict["email"],
            preferences=user_dict.get("preferences", {}),
            timeZone=user_dict.get("timeZone")
        ) for user_dict in users_data]
    except FileNotFoundError:
        return []
        
def save_users(users):
    ''' Handles saving users to db '''
    os.makedirs(os.path.dirname(USER_PATH), exist_ok=True)
    with open(USER_PATH, "w") as f:
        json.dump([u.to_dict() for u in users], f, indent=2)
    
def find_user_by_email(email, users):
        ''' Finds a user by email address '''
        for user in users:
            if user.email == email:
                return user
        return None

