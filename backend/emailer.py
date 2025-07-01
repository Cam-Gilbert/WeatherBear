import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

# load the env file
load_dotenv()

class Emailer:
    '''
    Emailer class. Contains methods that handle building the email string and sending the email to users. Interacts with main.py to run
    the constant functionality
    '''
    def __init__(self, User, obs, forecast, warnings, afd):
        '''
        Emailer object initialization method (constructor)

        @param User user object, contains important info such as name, email, location, etc...
        @param obs dictionary containing information on the observations from the closest station. Pulled from Data_Fetcher
        @param forecast list of dictionarys (1 dict for every forecast period) containing the basic daily forecast information 
        @param warnings list of dictionarys (1 dict for every alert) containing info on active alerts in the area
        @param afd string containing the summarized forecast discussion
        '''
        self.User = User
        self.obs = obs
        self.forecast = forecast 
        self.warnings = warnings
        self.afd = afd

    def generate_email(self):
        '''
        Handles building the email string that will be sent to users. 
        Example emails can be found at weatherbear.org/emailbot
        '''
        email_string = f"Hello {self.User.name}, "

        ## Get obs from self and account for units because observations dont have a unit modifier, always come in celsius unlike forecast.
        if self.User.preferences["units"] == "imperial":
            temp_unit = "F"
            # observation temperatures & dewpoints are in celcius - must convert to F
            temperature = self.obs['properties']['temperature']['value']
            if temperature is not None:
                temperature = round((temperature * (9/5)) + 32)
            dewpoint = self.obs['properties']['dewpoint']['value']
            if dewpoint is not None:
                dewpoint = round((dewpoint * (9/5)) + 32)
            windChill = self.obs['properties']['windChill']['value']
            if windChill is not None:
                windChill = round((windChill * (9/5)) + 32)
            heatIndex = self.obs['properties']['heatIndex']['value']
            if heatIndex is not None:
                heatIndex = round((heatIndex * (9/5)) + 32)
            station = self.obs['properties']['stationName']
            clouds = self.obs['properties']['textDescription']
            #precip in mm, should convert to inches for imperial
            lastHourPrecip = self.obs['properties']['precipitationLastHour']['value']
            if lastHourPrecip is not None:
                lastHourPrecip = round(lastHourPrecip / 25.4)
            last6HourPrecip = self.obs['properties']['precipitationLast6Hours']['value']
            if last6HourPrecip is not None:
                last6HourPrecip = round(last6HourPrecip / 25.4)
        else:
            temp_unit = "C"
            temperature = self.obs['properties']['temperature']['value']
            dewpoint = self.obs['properties']['dewpoint']['value']
            windChill = self.obs['properties']['windChill']['value']
            heatIndex = self.obs['properties']['heatIndex']['value']
            station = self.obs['properties']['stationName']
            clouds = self.obs['properties']['textDescription']
            lastHourPrecip = self.obs['properties']['precipitationLastHour']['value']
            last6HourPrecip = self.obs['properties']['precipitationLast6Hours']['value']

        # Observation string 
        if heatIndex is not None:
            email_string += f"it is currently {temperature} degrees {temp_unit} with a dewpoint of {dewpoint} {temp_unit}, for a feels-like temperature of {heatIndex} {temp_unit} at {station} with {clouds.lower()} skies. "
        elif windChill is not None:
            email_string += f"it is currently {temperature} degrees {temp_unit} with a dewpoint of {dewpoint} {temp_unit}, for a feels-like temperature of {windChill} {temp_unit} at {station} with {clouds.lower()} skies. "
        else:
            email_string += f"it is currently {temperature} degrees {temp_unit} with a dewpoint of {dewpoint} {temp_unit} at {station} with {clouds} skies. "

        # precip sentence only if necessary
        if lastHourPrecip is not None:
            email_string += f"There has been {lastHourPrecip} of precipitation in the past hour, and {last6HourPrecip} in the past 6 hours.\n"
        else:
            email_string += "\n\n"

        # Forecast strings
        email_string += "Today's Forecast:\n"

        email_string += self.forecast[0]['name'] + ": " + self.forecast[0]['detailed_forecast'] + "\n\n"
        email_string += self.forecast[1]['name'] + ": " + self.forecast[1]['detailed_forecast'] + "\n"

        # Only list watches and warnings if they exist for the area at the time
        if len(self.warnings) != 0:
            email_string = email_string + "\n" + "Watches/Warnings in your area:\n\n"
            for alert in self.warnings:
                email_string += alert['headline'] + "\n"
                if "Special Weather Statement" in alert['headline']:
                    email_string += ": " + alert['description'] + "\n"
                else:
                    email_string += "\n"
            
        # add summarized afd
        email_string += "\nSummarized forecast discussion: \n\n"
        email_string += self.afd

        email_string += "\n\nStay weather aware!\n- WeatherBear 🐻"

        #unsubscribe link
        email_string += "\n\n\nNo longer want forecasts? Unsubscribe at https://weatherbear.org/emailbot"

        return email_string

    def send_email(self):
        ''' 
        Handles sending the email 
        '''
        email_body = self.generate_email()
        email_subject = f"🌦️ Daily Weather Update, {self.User.name}"

        message = EmailMessage()
        message['Subject'] = email_subject
        message['From'] = "weatherbear.emailbot@gmail.com"
        message['To'] = self.User.email
        message.set_content(email_body)

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                smtp.starttls()
                smtp.login(os.getenv("SENDER_EMAIL"), os.getenv("EMAIL_APP_PASSWORD"))
                smtp.send_message(message)
                print(f"Email send to {self.User.name} - {self.User.email}")
        except Exception as e:
            print(f"Failed to send: {e}")