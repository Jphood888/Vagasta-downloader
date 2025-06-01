from flask import Flask, request, jsonify, send_file
import yt_dlp
import requests
import os
import re

from utils.insta_signup import perform_instagram_signup  # Make sure this file is correct

app = Flask(__name__)

# ===== Instagram Login Route =====
@app.route('/login', methods=['POST'])
def login_instagram():
    data = request.get_json()
    username = data['username']
    password = data['password']

    session = requests.Session()
    login_success = perform_instagram_login(session, username, password)

    if login_success:
        save_session_cookies(session, username)
        return jsonify({"status": "ok", "message": "Logged in!"})
    else:
        return jsonify({"status": "fail", "error": "Login failed!"}), 401

# ===== Instagram Signup Route =====
@app.route('/signup', methods=['POST'])
def signup_instagram():
    try:
        result = perform_instagram_signup()  # Async signup inside utils
        return jsonify(result)
    except Exception as e:
        print("❌ Signup error:", str(e))
        return jsonify({"status": "fail", "error": str(e)}), 500

# ===== Instagram Download Route =====
@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    platform = data.get('platform')
    format = data.get('format')
    username = data.get('username')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    if platform != 'instagram':
        return jsonify({'error': 'Only Instagram supported'}), 400
    if not username:
        return jsonify({'error': 'Username required for Instagram download'}), 400

    safe_username = re.sub(r'[^\w\-_.]', '_', username)
    cookie_file = os.path.join('cookies', f'instagram_cookies_{safe_username}.txt')
    if not os.path.exists(cookie_file):
        return jsonify({'error': 'User not logged in'}), 403

    ydl_opts = {
        'outtmpl': 'download.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'ffmpeg_location': '/usr/bin/ffmpeg',
        'cookiefile': cookie_file
    }

    if format == 'photo':
        ydl_opts['format'] = 'bestimage'
    elif format == 'video':
        ydl_opts['format'] = 'bestvideo+bestaudio/best'
    else:
        return jsonify({'error': 'Unsupported format for Instagram'}), 400

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        response = send_file(filename, as_attachment=True)
        os.remove(filename)  # Clean up
        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== Helper Functions =====
def perform_instagram_login(session, username, password):
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://www.instagram.com/accounts/login/',
        'x-csrftoken': 'missing',
    }

    session.get('https://www.instagram.com/')
    csrf_token = session.cookies.get('csrftoken')
    headers['x-csrftoken'] = csrf_token

    payload = {
        'username': username,
        'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:&:{password}',
        'queryParams': {},
        'optIntoOneTap': 'false'
    }

    response = session.post(login_url, data=payload, headers=headers)
    return response.status_code == 200 and response.json().get("authenticated", False)

def save_session_cookies(session, username):
    cookies_dir = 'cookies'
    os.makedirs(cookies_dir, exist_ok=True)
    safe_username = re.sub(r'[^\w\-_.]', '_', username)
    filename = os.path.join(cookies_dir, f'instagram_cookies_{safe_username}.txt')
    with open(filename, 'w') as f:
        for cookie in session.cookies:
            f.write(f"{cookie.domain}\tTRUE\t{cookie.path}\t{str(cookie.secure).upper()}\t{cookie.expires}\t{cookie.name}\t{cookie.value}\n")

# ===== Run Flask App =====
if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=8080)
