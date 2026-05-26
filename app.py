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

        # YouTube bot engelini aşmak için herkese açık, ücretsiz ve çalışan proxy listesi
        # yt-dlp bu proxy üzerinden giderek YouTube duvarını arkadan dolaşır
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            # Herkese açık ücretsiz proxy havuzundan bir IP kullanıyoruz
            'proxy': 'http://45.14.172.5:80'  
        }

        try:
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
        except Exception as yt_error:
            # Eğer üstteki proxy o an yavaşsa veya takıldıysa, proxysiz doğrudan temiz bir ayarla son kez dene
            fallback_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'nocheckcertificate': True
            }
            with yt_dlp.YoutubeDL(fallback_opts) as ydl_fallback:
                info = ydl_fallback.extract_info(video_url, download=False)
                download_url = info.get('url')
                video_title = info.get('title', 'Şarkı')
                
                if download_url:
                    return jsonify({
                        'status': 'success',
                        'message': f'"{video_title}" başarıyla dönüştürüldü!',
                        'download_url': download_url
                    })
                raise yt_error

        return jsonify({'status': 'error', 'message': 'İndirme bağlantısı çözülemedi.'}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Dönüştürme Hatası: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
