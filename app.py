import os
from flask import Flask, render_template, request, jsonify
import yt_dlp

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

        # En kararlı sunucu ayarları
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            download_url = info.get('url')
            video_title = info.get('title', 'Şarkı')

            if download_url:
                return jsonify({
                    'status': 'success',
                    'message': f'"{video_title}" başarıyla dönüştürüldü!',
                    'download_url': download_url
                })
            else:
                return jsonify({'status': 'error', 'message': 'İndirme bağlantısı çözülemedi.'}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Dönüştürme Hatası: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
