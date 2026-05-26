import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_video():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Veri alınamadı.'}), 400
            
        video_url = data.get('url')
        if not video_url:
            return jsonify({'status': 'error', 'message': 'Lütfen geçerli bir URL girin.'}), 400

        # Şirket destekli, kararlı çalışan ve bot engelini aşan global indirme API'si
        api_url = "https://api.v03.savethevideo.com/tasks"
        
        payload = {
            "url": video_url,
            "format": "mp3",
            "quality": "128"
        }
        
        # İstek atıp dönen indirme bağlantısını doğrudan yakalıyoruz
        response = requests.post(api_url, json=payload, timeout=15)
        
        if response.status_code == 201 or response.status_code == 200:
            result = response.json()
            # API'den gelen indirme linkini senin frontend yapına göre süzüyoruz
            download_url = result.get('downloadUrl') or result.get('href') or result.get('url')
            
            if not download_url and 'result' in result:
                download_url = result['result'].get('url')

            if download_url:
                return jsonify({
                    'status': 'success',
                    'message': 'Video başarıyla MP3 formatına dönüştürüldü!',
                    'download_url': download_url
                })

        # YEDEK HAT: Eğer üstteki sistem o an meşgulse doğrudan indirme veren alternatif servis
        backup_url = f"https://api.shadiao.pro/twb?url={video_url}"
        b_res = requests.get(backup_url, timeout=10)
        if b_res.status_code == 200:
            b_data = b_res.json()
            if b_data.get('code') == 200 and b_data.get('data'):
                return jsonify({
                    'status': 'success',
                    'message': 'Video başarıyla dönüştürüldü!',
                    'download_url': b_data['data']
                })

        return jsonify({'status': 'error', 'message': 'Şu an yoğunluk var, lütfen birkaç saniye sonra tekrar deneyin.'}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Dönüştürme Hatası: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
