import yt_dlp

# URL ของวิดีโอ YouTube
url = "https://youtu.be/5qLuDY7ORTU?si=cdHhNFxwPJJeaDYW"

# ตั้งค่าการดาวน์โหลดเฉพาะเสียง
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'songall/%(title)s.%(ext)s',  # บันทึกเป็นชื่อวิดีโอ
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',  # แปลงเป็น MP3
        'preferredquality': '192',  # คุณภาพ 192kbps
    }],
}

# ดาวน์โหลดไฟล์เสียง
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])