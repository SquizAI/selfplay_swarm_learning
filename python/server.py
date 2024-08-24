from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import openai
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for all routes

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/ai_action', methods=['POST'])
def ai_action():
    try:
        user_prompt = request.json.get('prompt')
        if not user_prompt:
            return jsonify({"error": "Prompt is missing"}), 400

        response = openai.Completion.create(
            engine="gpt-4",
            prompt=user_prompt,
            max_tokens=150
        )
        return jsonify({"response": response.choices[0].text.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=8000)
