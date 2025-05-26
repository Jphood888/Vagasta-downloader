from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
import uuid

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"

# Ensure the download directory exists
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@app.route('/')
def home():
    return "Vagasta Downloader Backend is running!"

@app.route('/download', methods=['GET'])
def download_media():
    url = request.args.get('url')
    format_id = request.args.get('format', 'best')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    filename = f"{uuid.uuid4()}.%(ext)s"
    output_path = os.path.join(DOWNLOAD_DIR, filename)

    ydl_opts = {
        'format': format_id,
        'outtmpl': output_path,
        'quiet': True,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            actual_path = ydl.prepare_filename(info)
            return send_file(actual_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

