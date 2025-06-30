import json
import time
from datetime import datetime
from backend.data_fetcher import Data_Fetcher
from backend.summarizer import Summarizer
from backend.emailer import Emailer
from backend.user import User, load_users, save_users

def main_loop():
    users = load_users()
    changes_made = False

    for user in users:
        if user.should_get_email():
            send_email_to_user(user)
            time.sleep(30) # sleeping for 30 seconds in order to prevent nws api from not providing the afd
            changes_made = True

    if changes_made:
        save_users(users)

def send_email_to_user(user):
    '''
    Executes the process of sending an email to the specified user object
    '''
    try:
        print("Gathering Data")
        # Collect Data
        df = Data_Fetcher(user.location, user.units)
        forecast_discussion, organized_alerts, daily_forecasts, obs_data, hourly_forecast = df.get_forecast()
        # Summarize response
        summarizer = Summarizer(user.preferences["weather_knowledge"], forecast_discussion)
        print("Generating Summary")
        summary = summarizer.generate_Message()
        # Generate and send email
        emailer = Emailer(user, obs_data, daily_forecasts, organized_alerts, summary)
        print(f"Generating Email")
        emailer.send_email()
        print(f"Email sent to {user.email}")
    except Exception as e:
        print(f"Failed to send email to {user.email}: {e}")

if __name__ == "__main__":
    pass
    #main_loop()