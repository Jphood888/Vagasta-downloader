from flask import Flask, request, jsonify, send_file
import yt_dlp
import requests
import os
import json

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


# ===== Download Route =====
@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    platform = data.get('platform')
    format = data.get('format')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    ydl_opts = {
        'outtmpl': 'download.%(ext)s',
        'quiet': True,
        'no_warnings': True
    }

    if platform == 'instagram':
        ydl_opts['cookiefile'] = 'cookies/instagram_cookies.txt'
        if format == 'photo':
            ydl_opts['format'] = 'bestimage'
        elif format == 'video':
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
        else:
            return jsonify({'error': 'Unsupported format for Instagram'}), 400

    elif platform == 'youtube':
        if format == 'mp3':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            })
        elif format == 'mp4':
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
        else:
            return jsonify({'error': 'Unsupported format for YouTube'}), 400

    else:
        return jsonify({'error': 'Unsupported platform'}), 400

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== Login Helper Functions =====
def perform_instagram_login(session, username, password):
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://www.instagram.com/accounts/login/',
        'x-csrftoken': 'missing',  # Will update automatically after first request
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
    with open(os.path.join(cookies_dir, 'instagram_cookies.txt'), 'w') as f:
        json.dump(session.cookies.get_dict(), f)


# ===== Run the Flask App =====
if __name__ == '__main__':
    app.run(debug=True)
