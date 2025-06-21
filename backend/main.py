import json
import time
from datetime import datetime
from data_fetcher import Data_Fetcher
from summarizer import Summarizer
from emailer import Emailer
from user import User, load_users, save_users

def main_loop():
    while True:
        users = load_users()
        changes_made = False

        for user in users:
            if user.should_get_email():
                send_email_to_user(user)
                time.sleep(30) # sleeping for 30 seconds in order to prevent nws api from not providing the afd
                changes_made = True

        if changes_made:
            save_users(users)

        # sleep for one hour before checking if sending is necessary again
        time.sleep(30) # change back to 3600 after testing is complete
    
def send_email_to_user(user):
    '''
    Executes the process of sending an email to the specified user object
    '''
    try:
        print("Gathering Data")
        # Collect Data
        df = Data_Fetcher(user.location)
        forecast_discussion, organized_alerts, daily_forecasts, obs_data = df.get_forecast()
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
    main_loop()