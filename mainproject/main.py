"""ดาวน์โหลดเพลง MP3 จาก YouTube — หน้าตาโปรแกรมด้วย Tkinter"""

import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

import downloader


class LogBus:
    """รับข้อความจาก thread ไหนก็ได้ แล้วให้ main thread มาดูดไปเขียนลง UI

    Tkinter แก้ widget ข้าม thread ไม่ได้ (แครชแบบสุ่ม) เลยต้องพักไว้ใน queue ก่อน
    """

    def __init__(self):
        self.queue = queue.Queue()

    # --- ฝั่ง yt-dlp เรียก (อยู่คนละ thread) ---
    def write_log(self, message):
        self.queue.put(str(message))

    def debug(self, msg):
        if not str(msg).startswith("[debug] "):
            self.write_log(msg)

    def info(self, msg):
        self.write_log(msg)

    def warning(self, msg):
        self.write_log("WARNING: " + str(msg))

    def error(self, msg):
        self.write_log("ERROR: " + str(msg))


class App:
    def __init__(self, root):
        self.root = root
        self.log = LogBus()
        self.busy = False

        root.title("ดาวน์โหลดเพลง MP3")
        root.geometry("560x560")
        root.minsize(480, 460)

        tk.Label(root, text="ใส่ลิงค์ที่นี้", font=("Arial", 18)).pack(pady=(10, 4))

        self.entry = tk.Entry(root, width=55, font=("Arial", 11))
        self.entry.pack(pady=4)
        self.entry.bind("<Return>", lambda _event: self.start_download())
        self.entry.focus()

        options = tk.Frame(root)
        options.pack(pady=4)

        tk.Label(options, text="คุณภาพ:").pack(side=tk.LEFT)
        self.quality = tk.StringVar(value=downloader.DEFAULT_QUALITY)
        ttk.Combobox(options, textvariable=self.quality, values=downloader.QUALITIES,
                     width=5, state="readonly").pack(side=tk.LEFT, padx=(2, 12))

        self.playlist = tk.BooleanVar(value=False)
        tk.Checkbutton(options, text="โหลดทั้งเพลลิสต์",
                       variable=self.playlist).pack(side=tk.LEFT)

        buttons = tk.Frame(root)
        buttons.pack(pady=6)
        self.button = tk.Button(buttons, text="ดาวน์โหลด", font=("Arial", 15),
                                width=12, command=self.start_download)
        self.button.pack(side=tk.LEFT, padx=4)
        tk.Button(buttons, text="เปิดโฟลเดอร์เพลง", font=("Arial", 11),
                  command=self.open_folder).pack(side=tk.LEFT, padx=4)

        self.progress = ttk.Progressbar(root, length=460, mode="determinate")
        self.progress.pack(pady=(4, 2))

        self.status = tk.Label(root, text="พร้อมใช้งาน", font=("Arial", 11), fg="gray30")
        self.status.pack()

        tk.Label(root, text="Log:", font=("Arial", 15)).pack(pady=(6, 0))
        self.text = scrolledtext.ScrolledText(root, width=64, height=12, state=tk.DISABLED)
        self.text.pack(padx=6, pady=(2, 8), fill=tk.BOTH, expand=True)

        self.write(f"yt-dlp เวอร์ชัน {downloader.version()}")
        self.write(f"เพลงจะถูกเก็บไว้ที่: {downloader.output_dir()}")
        if downloader.find_ffmpeg() is None:
            self.write("WARNING: หา ffmpeg ไม่เจอ — จะแปลงเป็น mp3 ไม่ได้")
            self.write("         ติดตั้งด้วย: choco install ffmpeg  (หรือวาง ffmpeg.exe ไว้ข้างๆ โปรแกรมนี้)")

        self.root.after(100, self.drain_log)

    # ---------- UI helpers ----------
    def write(self, message):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, message + "\n")
        self.text.config(state=tk.DISABLED)
        self.text.yview(tk.END)

    def drain_log(self):
        """main thread ดูดข้อความจาก queue มาเขียนลงกล่อง log ทุก 100ms"""
        try:
            while True:
                self.write(self.log.queue.get_nowait())
        except queue.Empty:
            pass
        self.root.after(100, self.drain_log)

    def set_busy(self, busy, status):
        self.busy = busy
        self.button.config(state=tk.DISABLED if busy else tk.NORMAL,
                           text="กำลังโหลด..." if busy else "ดาวน์โหลด")
        self.status.config(text=status)
        if not busy:
            self.progress["value"] = 0

    def open_folder(self):
        path = downloader.output_dir()
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    # ---------- การดาวน์โหลด ----------
    def start_download(self):
        if self.busy:
            return
        url = self.entry.get().strip()
        if not url:
            self.write("ERROR: ยังไม่ได้ใส่ลิงก์!")
            return
        if not url.startswith(("http://", "https://")):
            self.write("ERROR: ลิงก์ต้องขึ้นต้นด้วย http:// หรือ https://")
            return
        if downloader.find_ffmpeg() is None:
            messagebox.showerror("ไม่พบ ffmpeg",
                                 "ต้องติดตั้ง ffmpeg ก่อนถึงจะแปลงเป็น mp3 ได้\n\n"
                                 "เปิด PowerShell แบบ Administrator แล้วพิมพ์:\nchoco install ffmpeg")
            return

        self.set_busy(True, "กำลังดาวน์โหลด...")
        self.write("เริ่มดาวน์โหลด...")
        threading.Thread(target=self.worker, args=(url,), daemon=True).start()

    def worker(self, url):
        """รันใน thread แยก ห้ามแตะ widget ตรงๆ — สั่งงาน UI ผ่าน root.after เท่านั้น"""
        try:
            downloader.download(
                url,
                logger=self.log,
                progress_hook=self.hook,
                quality=self.quality.get(),
                playlist=self.playlist.get(),
            )
            self.log.write_log("เสร็จเรียบร้อย! ไฟล์อยู่ในโฟลเดอร์ song-all")
            self.root.after(0, lambda: self.entry.delete(0, tk.END))
            self.root.after(0, lambda: self.set_busy(False, "เสร็จเรียบร้อย"))
        except Exception as error:
            message = str(error)
            self.log.write_log(f"ERROR: {message}")
            if "sign in" in message.lower() or "nsig" in message.lower():
                self.log.write_log("ลองอัปเดต yt-dlp: pip install -U yt-dlp")
            self.root.after(0, lambda: self.set_busy(False, "ดาวน์โหลดไม่สำเร็จ"))

    def hook(self, d):
        """yt-dlp เรียกจาก thread ดาวน์โหลด — ส่งต่อให้ UI ผ่าน root.after"""
        status = d.get("status")
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            done = d.get("downloaded_bytes") or 0
            percent = (done / total * 100) if total else 0
            self.root.after(0, lambda: self.progress.config(value=percent))
            self.log.write_log(
                f"กำลังโหลด: {d.get('_percent_str', '?').strip()} "
                f"ที่ {d.get('_speed_str', '?').strip()} "
                f"เหลืออีก {d.get('_eta_str', '?').strip()}"
            )
        elif status == "finished":
            self.root.after(0, lambda: self.progress.config(value=100))
            self.root.after(0, lambda: self.status.config(text="กำลังแปลงเป็น mp3..."))
            self.log.write_log("โหลดเสร็จ กำลังแปลงเป็น mp3...")


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
