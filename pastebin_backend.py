from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Load credentials from environment variables (set these on Render)
API_DEV_KEY = os.getenv("API_DEV_KEY")
API_USER = os.getenv("API_USER")
API_PASS = os.getenv("API_PASS")

# This will store the session key
api_user_key = None

def login_to_pastebin():
    global api_user_key
    payload = {
        'api_dev_key': API_DEV_KEY,
        'api_user_name': API_USER,
        'api_user_password': API_PASS
    }

    response = requests.post("https://pastebin.com/api/api_login.php", data=payload)
    if "Bad API request" in response.text:
        print("Login failed:", response.text)
        return None

    api_user_key = response.text.strip()
    print("Pastebin login successful")
    return api_user_key

@app.route('/get_paste', methods=['POST'])
def get_paste():
    global api_user_key

    data = request.get_json()
    paste_id = data.get('paste_id')

    if not paste_id:
        return jsonify({"error": "Missing paste_id"}), 400

    # Log in if needed
    if not api_user_key:
        login_to_pastebin()

    payload = {
        'api_dev_key': API_DEV_KEY,
        'api_user_key': api_user_key,
        'api_paste_code': paste_id,
        'api_option': 'show_paste'
    }

    response = requests.post("https://pastebin.com/api/api_post.php", data=payload)

    if "Bad API request" in response.text:
        return jsonify({"error": response.text}), 400

    return jsonify({"content": response.text})

if __name__ == '__main__':
    login_to_pastebin()  # Login at startup
    app.run(host='0.0.0.0', port=5000)
