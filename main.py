import json
import time
from datetime import datetime
from weatherbear.data_fetcher import Data_Fetcher
from weatherbear.summarizer import Summarizer
from weatherbear.emailer import Emailer
from weatherbear.user import User



def main_loop():
    while True:
        users = load_users()

        for user in users:
            if check_should_send(user):
                send_email_to_user(user)

        # sleep for one hour before checking if sending is necessary again
        time.sleep(3600)


def load_users(path="users.json"):
    ''' responsible for loading users from users.json '''
    try:
        with open(path, "r") as f:
            users = json.load(f)
            return [User(**user) for user in users]
    except Exception as e:
        print(f"Failed to load users: {e}")
        return []
    
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

def check_should_send(user):
    now = datetime.now()

    return now.hour in [7, 19] and now.minute == 0

if __name__ == "__main__":
    main_loop()