import yt_dlp
from tkinter import *

root = Tk() 
root.title("ดาวน์โหลดเพลง")

mylable = Label(root, text="ใส่ลิงค์ที่นี้", font=("Arial", 25)).pack()

e = Entry(root, width=50)
e.pack()

def downloadmusic():
    url = e.get()
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song-all/%(title)s.%(ext)s',  
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',  
            'preferredquality': '192',  
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        

Button(root, text="ดาวน์โหลด", font=("Arial", 15), command=downloadmusic).pack()

root.geometry("500x480")
root.mainloop()