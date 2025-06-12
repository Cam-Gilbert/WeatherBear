from weatherbear.data_fetcher import Data_Fetcher
from weatherbear.summarizer import Summarizer
from weatherbear.emailer import Emailer
from weatherbear.user import User

def test_get_latlon():
    df = Data_Fetcher("Pinehurst")
    coords = df.get_latlon()
    if coords:
        print(f"Latitude: {coords[0]}, Longitude: {coords[1]}")
    else:
        print("Failed to get coordinates.")

#test_get_latlon()

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
    df = Data_Fetcher("Southern Pines")
    forecast_discussion, organized_alerts, daily_forecasts, obs_data = df.get_forecast()

    return forecast_discussion, organized_alerts, daily_forecasts, obs_data


#forecast_discussion, organized_alerts, daily_forecasts, obs_data = test_get_forecast()

def test_summarizer():
    df = Data_Fetcher("San Antonio")
    forecast_discussion, organized_alerts, daily_forecasts, obs_data = df.get_forecast()

    summarizer = Summarizer("moderate", forecast_discussion)
    summary = summarizer.generate_Message()

    return summary

#summary = test_summarizer()
#print(summary)

def test_emailer():
    user = User("Christopher", "Southern Pines", "gilbertchristopher630@gmail.com", preferences={"units": "imperial", "weather_knowledge": "moderate"})
    df = Data_Fetcher(user.location)
    forecast_discussion, organized_alerts, daily_forecasts, obs_data = df.get_forecast()
    summarizer = Summarizer(user.preferences["weather_knowledge"], forecast_discussion)
    summary = summarizer.generate_Message()
    emailer = Emailer(user, obs_data, daily_forecasts, organized_alerts, summary)
    email = emailer.generate_email()
    emailer.send_email()

    return email, user, forecast_discussion

email, user, forecast_discussion = test_emailer()

#print(email)
