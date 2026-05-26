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

        # D PLANIDAKİ GİZLİ KÖPRÜ: Bot engeline takılmayan alternatif API
        # Bu API doğrudan indirme linkini hazırlar
        api_url = f"https://api.deveb.co/youtube/info?url={video_url}"
        
        response = requests.get(api_url, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            # API'den gelen ses (audio) formatlarını kontrol ediyoruz
            formats = result.get('info', {}).get('formats', [])
            mp3_link = None
            
            # Önce sadece ses olan (audioonly) en kaliteli linki arayalım
            for f in formats:
                if f.get('audioWithoutVideo') == True or 'audio' in str(f.get('mimeType', '')):
                    mp3_link = f.get('url')
                    break
            
            # Eğer özel ses bulamazsa, ilk çalışan indirme linkini yakala
            if not mp3_link and len(formats) > 0:
                mp3_link = formats[0].get('url')

            if mp3_link:
                video_title = result.get('info', {}).get('title', 'Şarkı')
                return jsonify({
                    'status': 'success',
                    'message': f'"{video_title}" başarıyla dönüştürüldü!',
                    'download_url': mp3_link
                })

        # Eğer ilk köprü o an yanıt vermezse, doğrudan çalışan 2. yedek API hattı
        backup_url = f"https://api.dveb.xyz/api/yt?url={video_url}"
        backup_res = requests.get(backup_url, timeout=15)
        if backup_res.status_code == 200:
            b_result = backup_res.json()
            if 'url' in b_result:
                return jsonify({
                    'status': 'success',
                    'message': 'Video başarıyla dönüştürüldü!',
                    'download_url': b_result['url']
                })

        return jsonify({'status': 'error', 'message': 'YouTube bot koruması nedeniyle şu an bağlantı kurulamadı. Lütfen az sonra tekrar deneyin.'}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Dönüştürme Hatası: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
