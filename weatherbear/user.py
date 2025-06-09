import re

''' 
User Object for WeatherBear Project. Will contain information on users name, location, unit preferance, email address, 
and a level of weather knowledge

Unit preferance will be set to imperial by default
Weather knowledge will be set to moderate by default
'''
EMAIL_REGEX = re.compile(r"^\S+@\S+\.\S+$")

class User:
    def __init__(self, name, location, email, preferences=None):
        self.name = name
        self.location = location
        # check that email is valid
        if not EMAIL_REGEX.match(email):
            raise ValueError(f"Invalid email: {email}")
        
        self.email = email
        self.preferences = preferences or {}

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