from flask import Flask, request, jsonify, render_template
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("API_KEY")

app = Flask(__name__)

@app.route("/openai", methods=["POST"])
def proxy_openai():
    ''' Function to interact with openai api '''
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
    return render_template("emailbot.html")

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

if __name__ == "__main__":
    app.run(debug=True)