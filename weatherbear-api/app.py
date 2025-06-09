from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("API_KEY")

app = Flask(__name__)

@app.route("/openai", methods=["POST"])
def proxy_openai():
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