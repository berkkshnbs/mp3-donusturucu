import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_video():
    data = request.get_json()
    video_url = data.get('url')
    
    if not video_url:
        return jsonify({'status': 'error', 'message': 'Lütfen geçerli bir URL girin.'}), 400

    # Güncel ve sorunsuz çalışan Cobalt API'si
    api_url = "https://api.cobalt.tools/"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": video_url,
        "isAudioOnly": True,
        "audioFormat": "mp3",
        "vCodec": "h264"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=15)
        result = response.json()
        
        if response.status_code == 200 and 'url' in result:
            mp3_link = result['url']
            return jsonify({
                'status': 'success',
                'message': 'Video başarıyla MP3 formatına dönüştürüldü!',
                'download_url': mp3_link
            })
        else:
            error_msg = result.get('text', 'API videoyu dönüştüremedi.')
            return jsonify({'status': 'error', 'message': f'Dönüştürme başarısız: {error_msg}'}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Sunucu hatası: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
