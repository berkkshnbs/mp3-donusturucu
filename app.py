import os
from flask import Flask, render_template, request, jsonify
import yt_dlp

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

    # Kendi sunucumuzda çalışacak yt-dlp ayarları (En yüksek kalitede sesi bulur)
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,  # Videoyu sunucuya indirip alanı doldurmuyoruz, sadece direkt linki çözüyoruz
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Video bilgilerini YouTube'dan çekiyoruz
            info = ydl.extract_info(video_url, download=False)
            
            # Doğrudan YouTube sunucularından gelen ham ses/indirme linkini alıyoruz
            download_url = info.get('url')
            video_title = info.get('title', 'Şarkı')

            if download_url:
                return jsonify({
                    'status': 'success',
                    'message': f'"{video_title}" başarıyla dönüştürüldü!',
                    'download_url': download_url
                })
            else:
                return jsonify({'status': 'error', 'message': 'Youtubedan indirme bağlantısı alınamadı.'}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Dönüştürme Hatası: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
