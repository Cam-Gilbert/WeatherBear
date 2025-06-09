class Emailer:
    def __init__(self, User, obs, warnings, afd):
        self.User = User
        self.obs = obs
        self.warnings = warnings
        self.afd = afd

    def generate_email(self):
        email_string = f"Hello, {self.User.name}, "

        if self.User.preferences.units == "imperial":
            temp_unit = "F"
        else:
            temp_unit = "C"

        if self.obs.heatindex != None:
            email_string += f"it is currently {self.obs.temp} degrees {temp_unit} with a dewpoint of {self.obs.dewpoint} {temp_unit}, for a feels-like temperature of {self.obs.heatIndex} {temp_unit} at {self.obs.location} with {self.obs.clouds} skies. "
        elif self.obs.windchill != None:
            email_string += f"it is currently {self.obs.temp} degrees {temp_unit} with a dewpoint of {self.obs.dewpoint} {temp_unit}, for a feels-like temperature of {self.obs.windchill} {temp_unit} at {self.obs.location} with {self.obs.clouds} skies. "
        else:
            email_string += f"it is currently {self.obs.temp} degrees {temp_unit} with a dewpoint of {self.obs.dewpoint} {temp_unit} at {self.obs.location} with {self.obs.clouds} skies. "

        if self.obs.pastPrecip != None:
            email_string += f"There has been {self.obs.lastHourPrecip} of precipitation in the past hour, and {self.obs.last6HourPrecip} in the past 6 hours.\n"
        else:
            email_string += "\n"

        email_string += self.obs.forecast.detailed_forecast

        if self.warnings != None:
            ## Loop thru watches and warnings and attach to summary.
            email_string = email_string

        email_string += "\n Here is your summarized forecast discussion: \n\n"
        email_string += self.afd

        email_string += "\n\nHave a great day!\nWeatherBear"

        return email_string



