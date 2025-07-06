from backend.data_fetcher import Data_Fetcher
from backend.summarizer import Summarizer
from backend.emailer import Emailer
from backend.user import User
from datetime import datetime

def test_get_latlon():
    df = Data_Fetcher("Pinehurst", "metric")
    coords = df.get_latlon()
    if coords:
        print(f"Latitude: {coords[0]}, Longitude: {coords[1]}")
    else:
        print("Failed to get coordinates.")
    return coords

#x = test_get_latlon()

def test_get_forecast_office():
    df = Data_Fetcher("Los Angeles")
    coords = df.get_latlon()
    if coords:
        print(f"Latitude: {coords[0]}, Longitude: {coords[1]}")
    else:
        print("Failed to get coordinates.")

    office = df.get_forecast_office(coords[0], coords[1])
    
    print(office)
    return office


#data = test_get_forecast_office()

def test_get_forecast():
    df = Data_Fetcher("Raleigh", "imperial")
    forecast_discussion, organized_alerts, daily_forecasts, obs_data, hourly_forecast = df.get_forecast()

    return forecast_discussion, organized_alerts, daily_forecasts, obs_data, hourly_forecast


#forecast_discussion, organized_alerts, daily_forecasts, obs_data, hourly_forecast = test_get_forecast()

def test_summarizer():
    df = Data_Fetcher("Albany", "imperial")
    forecast_discussion, organized_alerts, daily_forecasts, obs_data, hourly = df.get_forecast()

    summarizer = Summarizer("moderate", forecast_discussion)
    summary = summarizer.generate_Message()

    return summary

#summary = test_summarizer()
#print(summary)

def test_emailer():
    user = User("Chris", "Raleigh", "gilbertcameron03@gmail.com", preferences={"units": "imperial", "weather_knowledge": "moderate"})
    df = Data_Fetcher(user.location)
    forecast_discussion, organized_alerts, daily_forecasts, obs_data = df.get_forecast()
    summarizer = Summarizer(user.preferences["weather_knowledge"], forecast_discussion)
    summary = summarizer.generate_Message()
    emailer = Emailer(user, obs_data, daily_forecasts, organized_alerts, summary)
    email = emailer.generate_email()
    emailer.send_email()

    return email, user, forecast_discussion, obs_data,

#email, user, forecast_discussion, obs_data = test_emailer()

#print(email)

def test_get_tropical_forecast():
    df = Data_Fetcher("Raleigh", "imperial")
    tropical_data, storm_codes = df.get_tropical_data()

    return tropical_data, storm_codes

tropical_data, storm_codes = test_get_tropical_forecast()

def test_get_twd_summary():
    df = Data_Fetcher("Raleigh", "imperial")
    tropical_data = df.get_tropical_data()

    summarizer = Summarizer("expert", twd_discussion = tropical_data['Atlantic']['twd_discussions'][0]['discussion'])
    text = summarizer.generate_Region_Summary()
    
    return text

#text = test_get_twd_summary()

def test_get_storm_summary():
    df = Data_Fetcher("Raleigh", "imperial")
    tropical_data = df.get_tropical_data()

    summarizer = Summarizer("expert", storm_discussion = tropical_data['Atlantic']['Chantal']['discussions'][0]['description'])
    text = summarizer.generate_Storm_Summary()
    
    return text

#text = test_get_storm_summary()