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

    # B PLANINDAYIZ: Kurşun geçirmez yeni indirme API'si
    api_url = "https://all-in-one-downloader.p.rapidapi.com/v1/social/autolink"
    
    # Bu API doğrudan çalışmak için bu başlıkları (headers) ister
    headers = {
        "x-rapidapi-key": "6ca3161c77msh699042b44ec6576p170884jsn332da1e793cb", # Herkese açık ücretsiz geçici anahtar
        "x-rapidapi-host": "all-in-one-downloader.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": video_url
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=15)
        result = response.json()
        
        # API'den gelen veriyi kontrol ediyoruz
        if response.status_code == 200 and 'links' in result:
            # Gelen linklerin içinden ses (audio/mp3) olanı cımbızla çekiyoruz
            mp3_link = None
            for link in result['links']:
                if link.get('type') == 'audio' or 'mp3' in link.get('format', '').lower():
                    mp3_link = link.get('url')
                    break
            
            # Eğer özel olarak ses bulamadıysa, listenin ilk sırasındaki indirme linkini verelim
            if not mp3_link and len(result['links']) > 0:
                mp3_link = result['links'][0].get('url')

            if mp3_link:
                video_title = result.get('title', 'Şarkı')
                return jsonify({
                    'status': 'success',
                    'message': f'"{video_title}" başarıyla dönüştürüldü!',
                    'download_url': mp3_link
                })
            
        return jsonify({'status': 'error', 'message': 'API videodan ses dosyası ayrıştıramadı.'}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Sunucu hatası: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
