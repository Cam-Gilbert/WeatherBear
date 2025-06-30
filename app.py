from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, get_flashed_messages, session
import openai
import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from backend.data_fetcher import Data_Fetcher
from backend.user import User, load_users, save_users, find_user_by_email
from backend.summarizer import Summarizer
from backend.main import main_loop
from datetime import datetime

load_dotenv()
openai.api_key = os.getenv("API_KEY")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

@app.route("/openai", methods=["POST"])
def proxy_openai():
    ''' Function to interact with openai api 
    WAS USED IN DEVELOPMENT BUT NOT CURRENTLY USED
    '''
    try:
        text = request.get_json()
        messages = text.get("messages")

        if not messages:
            return jsonify({"error": "Missing 'messages' in request"}), 400
        
        response = openai.chat.completions.create(model="gpt-4.1-mini", messages=messages)

        ## hoping tyhat this will allow jsonify to handle the resonse ChatCompletion object
        content = response.choices[0].message.content.strip()
        return jsonify({"summary": content})
    except Exception as e:
        return jsonify({"Error": str(e)}), 500
    
# ✅ New routes to serve your HTML pages:
@app.route("/")
def homepage():
    ''' Routing for the homepage html page '''
    return render_template("homepage.html")

@app.route("/emailbot")
def emailbot():
    ''' Routing for the emailbot html page '''
    messages = get_flashed_messages(with_categories=True)
    return render_template("emailbot.html", flash_messages=messages)

@app.route("/about")
def about():
    ''' Routing for the about html page '''
    return render_template("about.html")

@app.route("/set_location", methods=["POST"])
def set_location():
    ''' Routing for the get location function'''
    data = request.get_json()
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    
    print(f"Received location: lat={latitude}, lon={longitude}")

    # Optionally, you can store this in session, database, etc.
    return {"status": "success"}, 200

@app.route("/submit-emailbot", methods=["POST"])
def submit_emailbot():
    ''' Routing for the emailbot form submission '''
    print("hit submission route")
    form = request.form
    user = User(
        name=form.get("name"),
        location=form.get("location"),
        email=form.get("email"),
        preferences={
            "units": form.get("units"),
            "weather_knowledge": form.get("expertise"),
            "send_hours": [int(t.split(":")[0]) for t in form.getlist("send_times")],
            "times_sent": []
        }
    )
    print(user)
    users = load_users()
    print(users)
    existing_user = find_user_by_email(user.email, users)
    if existing_user:
        users = [u for u in users if u.email != user.email]
        flash("Your preferences have been saved!", "signup")
    else:
        flash("You have successsfully signed up!", "signup")
    users.append(user)
    print(users)
    save_users(users)
    return redirect(url_for("emailbot"))

@app.route("/unsubscribe", methods=["POST"])
def unsubscribe():
    ''' Routing for removing from email list '''
    email = request.form.get("unsubscribe_email")
    users = load_users()
    users = [u for u in users if u.email != email]
    save_users(users)
    flash("You have been unsubscribed.", "unsubscribe")
    return redirect(url_for("emailbot"))

@app.route("/get-forecast", methods=["POST"])
def get_forecast():
    data = request.get_json()
    location = data.get("location")
    lat = data.get("latitude")
    lon = data.get("longitude")
    units = data.get("units", "imperial")
    # verify lat lon exists, use location otherwise
    if lat and lon:
        loc = f"{lat},{lon}"
    elif location:
        loc = location

    df = Data_Fetcher(loc, units)
    forecast_discussion, organized_alerts, daily_forecasts, obs_data, hourly_forecast = df.get_forecast()

    if units == "imperial":
        temp_unit = "F"
        # observation temperatures & dewpoints are in celcius - must convert to F
        temperature = obs_data['properties']['temperature']['value']
        temperature = round((temperature * (9/5)) + 32)
        dewpoint = obs_data['properties']['dewpoint']['value']
        dewpoint = round((dewpoint * (9/5)) + 32)
        windChill = obs_data['properties']['windChill']['value']
        if windChill is not None:
            windChill = round((windChill * (9/5)) + 32)
        heatIndex = obs_data['properties']['heatIndex']['value']
        if heatIndex is not None:
            heatIndex = round((heatIndex * (9/5)) + 32)
        station = obs_data['properties']['stationName']
        clouds = obs_data['properties']['textDescription']
    else:
        temp_unit = "C"
        temperature = obs_data['properties']['temperature']['value']
        dewpoint = obs_data['properties']['dewpoint']['value']
        windChill = obs_data['properties']['windChill']['value']
        if windChill is not None:
            windChill = round(windChill)
        heatIndex = obs_data['properties']['heatIndex']['value']
        if heatIndex is not None:
            heatIndex = round(heatIndex)
        station = obs_data['properties']['stationName']
        clouds = obs_data['properties']['textDescription']

    first_slice = make_hourly_split(hourly_forecast['properties']['periods'][0]['startTime'], daily_forecasts[0]['end_time'], hourly_forecast)
    second_slice = make_hourly_split(daily_forecasts[0]['end_time'], daily_forecasts[1]['end_time'], hourly_forecast)
    third_slice = make_hourly_split(daily_forecasts[1]['end_time'], daily_forecasts[2]['end_time'], hourly_forecast)
    fourth_slice = make_hourly_split(daily_forecasts[2]['end_time'], daily_forecasts[3]['end_time'], hourly_forecast)

    if heatIndex is not None:
        text = f"It is currently {temperature} degrees {temp_unit} with a dewpoint of {dewpoint} {temp_unit}, for a feels-like temperature of {heatIndex} {temp_unit} at {station} with {clouds.lower()} skies. "
    elif windChill is not None:
        text = f"It is currently {temperature} degrees {temp_unit} with a dewpoint of {dewpoint} {temp_unit}, for a feels-like temperature of {windChill} {temp_unit} at {station} with {clouds.lower()} skies. "
    else:
       text = f"It is currently {temperature} degrees {temp_unit} with a dewpoint of {dewpoint} {temp_unit} at {station} with {clouds} skies. "

    current_icon = determine_icon(obs_data['properties']['icon'])

    return jsonify({
        "alerts": organized_alerts,
        "current": {
            "temperature": temperature,
            "dewpoint": dewpoint,
            "station": station,
            "clouds": clouds,
            "windChill": windChill,
            "heatIndex": heatIndex,
            "text": text,
            "icon": current_icon
        }, 
        "first_period": {
            "title": daily_forecasts[0]['name'],
            "temperature": daily_forecasts[0]['temperature'],
            "wind_dir": daily_forecasts[0]['wind_direction'],
            "wind_speed": daily_forecasts[0]['wind_speed'],
            "is_daytime": daily_forecasts[0]['is_daytime'],
            "precip_chance": daily_forecasts[0]['precipitation_chance'],
            "text": daily_forecasts[0]['detailed_forecast'],
            "icon": determine_icon(daily_forecasts[0]['icon']),
            "hourly_forecast": first_slice
        }, 
        "second_period": {
            "title": daily_forecasts[1]['name'],
            "temperature": daily_forecasts[1]['temperature'],
            "wind_dir": daily_forecasts[1]['wind_direction'],
            "wind_speed": daily_forecasts[1]['wind_speed'],
            "is_daytime": daily_forecasts[1]['is_daytime'],
            "precip_chance": daily_forecasts[1]['precipitation_chance'],
            "text": daily_forecasts[1]['detailed_forecast'],
            "icon": determine_icon(daily_forecasts[1]['icon']),
            "hourly_forecast": second_slice
        }, 
        "third_period": {
            "title": daily_forecasts[2]['name'],
            "temperature": daily_forecasts[2]['temperature'],
            "wind_dir": daily_forecasts[2]['wind_direction'],
            "wind_speed": daily_forecasts[2]['wind_speed'],
            "is_daytime": daily_forecasts[2]['is_daytime'],
            "precip_chance": daily_forecasts[2]['precipitation_chance'],
            "text": daily_forecasts[2]['detailed_forecast'],
            "icon": determine_icon(daily_forecasts[2]['icon']),
            "hourly_forecast": third_slice

        }, 
        "fourth_period": {
            "title": daily_forecasts[3]['name'],
            "temperature": daily_forecasts[3]['temperature'],
            "wind_dir": daily_forecasts[3]['wind_direction'],
            "wind_speed": daily_forecasts[3]['wind_speed'],
            "is_daytime": daily_forecasts[3]['is_daytime'],
            "precip_chance": daily_forecasts[3]['precipitation_chance'],
            "text": daily_forecasts[3]['detailed_forecast'],
            "icon": determine_icon(daily_forecasts[3]['icon']),
            "hourly_forecast": fourth_slice
        }
    })

@app.route("/get-summary", methods=["POST"])
def get_summary():
    location = request.form.get("location")
    lat = request.form.get("latitude")
    lon = request.form.get("longitude")
    expertise = request.form.get("expertise")
    units = request.form.get("units")

    if location:
        loc = location  # Prefer user-entered location
    elif lat and lon:
        loc = f"{lat},{lon}"  # Fallback to detected coordinates
    else:
        return jsonify({"error": "No location provided"}), 400

    df = Data_Fetcher(loc, units)
    forecast_discussion, *_ = df.get_forecast()
    if forecast_discussion is not None:
        summarizer = Summarizer(expertise, forecast_discussion)
        summarizer_object = summarizer
    else:
        return jsonify({"error": "Missing afd"}), 400

    summary = f"Forecast Summary for {location}\n\n"
    summary += summarizer.generate_Message()

    return jsonify({
        "summary": summary,
        "afd": forecast_discussion,
        "expertise": expertise
    })


def determine_icon(link):
    if link is None:
        return "static/assets/day_clear.png"

    if any(term in link for term in ["skc", "wind_skc", "hot", "cold"]):
        icon = "static/assets/day_clear.png" if "day" in link else "static/assets/moon_clear.png"
    elif any(term in link for term in ["few", "wind_few"]):
        icon = "static/assets/day_clear.png" if "day" in link else "static/assets/moon_clear.png"
    elif any(term in link for term in ["sct", "wind_sct"]):
        icon = "static/assets/sun_partlycloudy.png" if "day" in link else "static/assets/moon_partlycloudy.png"
    elif any(term in link for term in ["bkn", "wind_bkn"]):
        icon = "static/assets/sun_partlycloudy.png" if "day" in link else "static/assets/moon_partlycloudy.png"
    elif any(term in link for term in ["ovc", "wind_ovc"]):
        icon = "static/assets/overcast.png"
    elif "snow" in link:
        icon = "static/assets/sun_scattered_snow.png" if "day" in link else "static/assets/moon_scattered_snow.png"
    elif any(term in link for term in ["rain_snow", "rain_sleet", "snow_sleet", "fzra", "rain_fzra", "snow_fzra", "sleet"]):
        icon = "static/assets/sun_scattered_sleet.png" if "day" in link else "static/assets/moon_scattered_sleet.png"
    elif "rain_showers_hi" in link:
        icon = "static/assets/sun_scattered_rain.png" if "day" in link else "static/assets/moon_scattered_rain.png"
    elif "rain_showers" in link or "rain" in link:
        icon = "static/assets/rain.png"
    elif "tsra_sct" in link:
        icon = "static/assets/sun_scattered_thunderstorm.png" if "day" in link else "static/assets/moon_scattered_thunderstorm.png"
    elif "tsra_hi" in link or "tsra" in link:
        icon = "static/assets/thunderstorm.png"
    elif "tornado" in link:
        icon = "static/assets/tornado.png"
    elif "hurricane" in link or "tropical_storm" in link:
        icon = "static/assets/hurricane.png"
    elif any(term in link for term in ["dust", "smoke", "haze"]):
        icon = "static/assets/sun_hazy.png" if "day" in link else "static/assets/moon_hazy.png"
    elif "blizzard" in link:
        icon = "static/assets/snow.png"
    elif "fog" in link:
        icon = "static/assets/sun_fog.png" if "day" in link else "static/assets/moon_fog.png"
    else:
        icon = "static/assets/day_clear.png"

    return icon


def make_hourly_split(start_time, end_time, hourly_forecast):
    '''
    start_time = hourly_forecast['properties']['periods'][0]['startTime']
    end_time = daily_forecasts[0]['end_time']
    '''
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)

    periods = hourly_forecast['properties']['periods']
    sliced = [
        p for p in periods
        if start_dt <= datetime.fromisoformat(p['endTime']) <= end_dt
    ]

    return sliced


@app.route("/explain-text", methods=["POST"])
def explain_selected_text():
    data = request.get_json()
    selected_text = data.get("text", "").strip()
    summary = data.get("summary", "")
    forecast = data.get("afd", "")
    expertise = data.get("expertise", "")

    if not selected_text or not summary or not forecast or not expertise:
        return jsonify({"explanation": "Missing required fields"}), 400

    if not summary or not forecast or not expertise:
        return jsonify({"explanation": "Session expired or incomplete"}), 400

    # need to implement explain_text 
    summarizer = Summarizer(expertise, forecast)
    explanation = summarizer.explain_text(selected_text, summary)  # your OpenAI or AI logic
    return jsonify({"explanation": explanation})
    #return jsonify({"explanation": "test -- works"})


# start scheduler when Flask starts
scheduler = BackgroundScheduler()
scheduler.add_job(func=main_loop, trigger="interval", seconds=120)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)