import json
import time
from datetime import datetime
from data_fetcher import Data_Fetcher
from summarizer import Summarizer
from emailer import Emailer
from user import User

def main_loop():
    while True:
        users = load_users()
        changes_made = False

        for user in users:
            if user.should_get_email():
                send_email_to_user(user)
                print(f"Email sent to {user.email}")
                changes_made = True

        if changes_made:
            save_users(users)

        # sleep for one hour before checking if sending is necessary again
        time.sleep(3600)


def load_users(path="weatherbear/users.json"):
    ''' responsible for loading users from users.json '''
    try:
        with open(path, "r") as f:
            users = json.load(f)
            return [User(**user) for user in users]
    except Exception as e:
        print(f"Failed to load users: {e}")
        return []
    
def save_users(users, path="users.json"):
    ''' Saves users from the user dictionary into the users.json file for storage '''
    try:
        user_dicts = []
        for user in users:
            user_dicts.append({
                "name": user.name,
                "location": user.location,
                "email": user.email,
                "preferences": user.preferences
            })
        with open(path, "w") as f:
            json.dump(user_dicts, f, indent=2)
    except Exception as e:
        print(f"failed to save users: {e}")
    
def send_email_to_user(user):
    '''
    Executes the process of sending an email to the specified user object
    '''
    try:
        # Collect Data
        df = Data_Fetcher(user.location)
        forecast_discussion, organized_alerts, daily_forecasts, obs_data = df.get_forecast()
        # Summarize response
        summarizer = Summarizer(user.preferences["weather_knowledge"], forecast_discussion)
        summary = summarizer.generate_Message()
        # Generate and send email
        emailer = Emailer(user, obs_data, daily_forecasts, organized_alerts, summary)
        emailer.send_email()
    except Exception as e:
        print(f"Failed to send email to {user.email}: {e}")

if __name__ == "__main__":
    main_loop()