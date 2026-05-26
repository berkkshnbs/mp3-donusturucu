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

    api_url = "https://all-in-one-downloader.p.rapidapi.com/v1/social/autolink"
    
    headers = {
        "x-rapidapi-key": "6ca3161c77msh699042b44ec6576p170884jsn332da1e793cb",
        "x-rapidapi-host": "all-in-one-downloader.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": video_url
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=15)
        result = response.json()
        
        if response.status_code == 200 and 'links' in result and len(result['links']) > 0:
            mp3_link = None
            
            # 1. Aşama: Gerçekten ses/mp3 olan bir link var mı diye agresif bir arama yapıyoruz
            for link in result['links']:
                link_type = str(link.get('type', '')).lower()
                link_format = str(link.get('format', '')).lower()
                
                if 'audio' in link_type or 'mp3' in link_format or 'm4a' in link_format:
                    mp3_link = link.get('url')
                    break
            
            # 2. Aşama: Eğer ses bulamadıysa, inat etme! API'nin bulduğu EN İLK indirme linkini ver (Video bile olsa indirsin)
            if not mp3_link:
                mp3_link = result['links'][0].get('url')

            if mp3_link:
                video_title = result.get('title', 'Başarılı')
                return jsonify({
                    'status': 'success',
                    'message': f'"{video_title}" bağlantısı hazırlandı!',
                    'download_url': mp3_link
                })
            
        return jsonify({'status': 'error', 'message': 'API bu video için hiçbir indirme bağlantısı üretemedi.'}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Sunucu hatası: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
