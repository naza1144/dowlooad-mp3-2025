import yt_dlp
import tkinter as tk
from tkinter import scrolledtext
import threading

class MyLogger:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write_log(self, message):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, message + "\n")
        self.text_widget.config(state=tk.DISABLED)
        self.text_widget.yview(tk.END)

    def debug(self, msg):
        self.write_log(msg)

    def warning(self, msg):
        self.write_log("WARNING: " + msg)

    def error(self, msg):
        self.write_log("ERROR: " + msg)

def download_music_thread(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song-all/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'logger': log_widget,
        'progress_hooks': [hook_function]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            root.after(0, lambda: entry.delete(0, tk.END))
    except Exception as e:
        log_widget.write_log(f"ERROR: {str(e)}")

def start_download():
    url = entry.get()
    if not url:
        log_widget.write_log("ERROR: Please enter a URL!")
        return
    log_widget.write_log("เริ่มดาวน์โหลด...")
    threading.Thread(target=download_music_thread, args=(url,)).start()

def hook_function(d):
    if d['status'] == 'downloading':
        log_widget.write_log(f"Downloading: {d['_percent_str']} at {d['_speed_str']}")
    elif d['status'] == 'finished':
        log_widget.write_log("Download complete! Converting to mp3...")

# Tkinter UI
root = tk.Tk()
root.title("ดาวน์โหลดเพลง")
root.geometry("500x500")

tk.Label(root, text="ใส่ลิงค์ที่นี้", font=("Arial", 18)).pack(pady=5)

entry = tk.Entry(root, width=50)
entry.pack(pady=5)

tk.Button(root, text="ดาวน์โหลด", font=("Arial", 15), command=start_download).pack(pady=5)

tk.Label(root, text="Log:", font=("Arial", 15)).pack(pady=5)

log_widget = MyLogger(scrolledtext.ScrolledText(root, width=60, height=10, state=tk.DISABLED))
log_widget.text_widget.pack(padx=5, pady=5)

root.mainloop()