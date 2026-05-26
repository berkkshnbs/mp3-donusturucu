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

    # Ücretsiz ve harika bir YouTube MP3 API'si kullanıyoruz
    # Bu API, verdiğimiz linki doğrudan MP3 indirme bağlantısına dönüştürür.
    api_url = f"https://api.vexd.workers.dev/youtube?url={video_url}"

    try:
        # API'ye istek atıyoruz
        response = requests.get(api_url, timeout=15)
        result = response.json()
        
        # API'den gelen cevaba göre indirme linkini alıyoruz
        if response.status_code == 200 and 'download_url' in result:
            mp3_link = result['download_url']
            video_title = result.get('title', 'Şarkı')
            
            return jsonify({
                'status': 'success',
                'message': f'"{video_title}" başarıyla dönüştürüldü!',
                'download_url': mp3_link  # Ön yüze hazır indirme linkini gönderiyoruz
            })
        else:
            return jsonify({'status': 'error', 'message': 'API videoyu dönüştüremedi. Lütfen başka bir link deneyin.'}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Sunucu hatası: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)