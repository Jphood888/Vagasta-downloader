from flask import Flask, request, send_file, jsonify
import yt_dlp
import os

app = Flask(__name__)

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

    # Example for Instagram
    if platform == 'instagram':
        ydl_opts['cookiefile'] = 'instagram_cookies.txt'  # ✅ Add this line
        if format == 'photo':
            ydl_opts['format'] = 'bestimage'
        elif format == 'video':
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
        else:
            return jsonify({'error': 'Unsupported format for Instagram'}), 400

    # Example for YouTube
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

if __name__ == '__main__':
    app.run(debug=True)
