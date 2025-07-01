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
# regex string that should catch invalid emails 
EMAIL_REGEX = re.compile(r"^\S+@\S+\.\S+$")
# geolocator
_geolocator = Nominatim(user_agent="weatherbear")
# time zone finder object, used to get users time zone from the 
_tz_finder = TimezoneFinder()
# USER_PATH path to users.json on server, this path does not exist on local machine or repo
USER_PATH = "/mnt/data/users.json"

class User:
    '''
    User object, stores important information for all functionality on the webpage. Including, name, location, email address,
    units perferences, weather knowledge level, hours users want to recieve emails, the past times emails have been sent, and users time zone
    '''
    def __init__(self, name, location, email, preferences = None, timeZone = None):
        '''
        User object initialization method (constructor)

        @param name users name
        @param location users location
        @param email users email address
        @param preferences preferences data structure containing the users units, weather_knowledge, send_hours, times_sent fields, none by default
        @param timeZone users timezone, none by default until filled
        '''
        self.name = name
        self.location = location
        # check that email is valid - might not be necessary as js checks form inputs but probably a nice safety net so I will leave it. 
        if not EMAIL_REGEX.match(email):
            raise ValueError(f"Invalid email: {email}")
        
        self.email = email
        self.preferences = preferences or {}
        self.timeZone = timeZone or self.get_time_zone()

    @property
    def units(self):
        '''
        allows field access like User.units
        
        @return the users units
        '''
        return self.preferences.get("units", "metric")
    
    @units.setter
    def units(self, value):
        '''
        Used to set the units portion of the users properties field
        
        @param value either "metric" or "imperial" for unit designation
        '''
        if value not in ("metric", "imperial"):
            raise ValueError("units must be either metric (C) or imperial (F)")
        self.preferences["units"] = value.lower()

    @property
    def weather_knowledge(self):
        '''
        allows field access like User.weather_knowledge
        
        @return the users weather_knowledge
        '''
        return self.preferences.get("weather_knowledge", "moderate")
    
    @weather_knowledge.setter
    def weather_knowledge(self, value):
        '''
        Used to set the weather_knowledge portion of the users properties field
        
        @param value either "none", "moderate", "expert" or "no_summary" for summary-level designation
        '''
        if value.lower() not in ("none", "moderate", "expert", "no_summary"):
            raise ValueError("level of weather knowledge must be either none, moderate, or expert")
        self.preferences["weather_knowledge"] = value.lower()

    @property
    def send_hours(self):
        '''
        allows field access like User.send_hours
        
        @return the users send_hours, when to send the users emails
        '''
        return self.preferences.get("send_hours", [7])
    
    @send_hours.setter
    def send_hours(self, hours):
        '''
        Used to set the weather_knowledge portion of the users properties field
        
        @param hours list of integers between 0 and 23 indicating the hours (users local time) to send emails
        '''
        if not isinstance(hours, list) or not all(isinstance(h, int) and 0 <= h <= 23 for h in hours):
            raise ValueError("send_hours must be a list of integers between 0 and 23")
        self.preferences["send_hours"] = sorted(set(hours))

    @property
    def times_sent(self):
        '''
        allows field access like User.times_sent
        
        @return the users times_sent, the past times emails were successfully sent
        '''
        return self.preferences.get("times_sent", [])
    
    @times_sent.setter
    def times_sent(self, value):
        '''
        Used to set the times_sent portion of the users properties field
        
        @param value dictionary containing information on the past times an email has been sent. Used to prevent repeat sends
        '''
        if not isinstance(value, dict):
            raise ValueError("times_sent must be a dictionary")
        self.preferences["times_sent"] = value

    def get_time_zone(self):
        '''
        Uses OpenStreetMap API to get lat/lon and then TimezoneFinder to get timezone
        '''
        try:
            # Try to get time zone from location using openstreetmap api based on the users location
            url = f"https://nominatim.openstreetmap.org/search?q={self.location}&format=json&limit=1"
            response = requests.get(url, headers={"User-Agent": "WeatherBearApp/1.0"})
            response.raise_for_status()
            data = response.json()

            if not data:
                raise ValueError(f"Could not find location for: {self.location}")

            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])

            # use timezone finder object
            tz = _tz_finder.timezone_at(lat=lat, lng=lon)
            if not tz:
                raise ValueError(f"Could not determine timezone for location: {self.location}")

            return tz

        except (HTTPError, Timeout, RequestException, ValueError) as e:
            print(f"could not detect timezone at {self.location}: {e}")
            return "UTC"
        
    def should_get_email(self, now_utc=None):
        ''' 
        Checks if the user should get an email based on the current time and the users time preferences
            
        @param now_utc if not utc time is given, the current utc time ised
        @return true if the user should be getting an email, false otherwise
        '''
        # if no utc time, get the current one
        if now_utc is None:
            now_utc = datetime.now(timezone.utc)

        # try to convert the current utc time to the local time based on the users timezone
        try:
            local_time = now_utc.astimezone(ZoneInfo(self.timeZone))
        except Exception as e:
            print(f"invalid time zone {self.email}: {e}")
            return False
        

        hour_key = local_time.strftime("%Y-%m-%d %H")

        # add that the hour was sent to times_sent dictionary
        if local_time.hour in self.send_hours and hour_key not in self.times_sent:
            self.record_sent_hour(hour_key)
            return True
        
        return False
    
    def record_sent_hour(self, hour_key):
        ''' 
        Adds a new hour to the list. Maintains a queue

        @param hour_key, the hour email was sent in the format Year-Month-Day hour
        '''
        sent = self.preferences.setdefault("times_sent", [])
        if hour_key not in sent:
            sent.append(hour_key)
            # onlt keep 5 most recent send timestamps.
            if len(sent) > 5:
                sent.pop(0)

    def to_dict(self):
        ''' 
        @return a dictionary representation of the user 
        '''
        return {
            "name": self.name,
            "location": self.location,
            "email": self.email,
            "preferences": self.preferences,
            "timeZone": self.timeZone
        }

def load_users():
    ''' 
    Loads users from the database.

    @return a list of user objects pulled from the users.json file
    '''
    # Used to set up a users.json file when first deploying app
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
    ''' 
    Handles saving users to db 
    
    @param a list of users to save to the users.json file
    '''
    os.makedirs(os.path.dirname(USER_PATH), exist_ok=True)
    with open(USER_PATH, "w") as f:
        json.dump([u.to_dict() for u in users], f, indent=2)
    
def find_user_by_email(email, users):
        ''' 
        Finds a user by email address. Simply iterates thru list of users and checks if an email already exists in the list. 

        @param email email address to be found
        @param users list to be searced
        '''
        for user in users:
            if user.email.lower() == email.lower():
                return user
        return None