"""แกนดาวน์โหลดเสียงจาก YouTube -> MP3 (ไม่พึ่ง tkinter จะได้เทสต์/เรียกใช้จากที่อื่นได้)"""

import os
import shutil
import sys

import yt_dlp

DEFAULT_QUALITY = "192"
QUALITIES = ("128", "192", "256", "320")


def app_dir():
    """โฟลเดอร์หลักของโปรแกรม: ที่อยู่ของ .exe ถ้า build แล้ว ไม่งั้นคือ root ของโปรเจกต์"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def output_dir():
    """โฟลเดอร์ปลายทาง song-all/ (สร้างให้ถ้ายังไม่มี)"""
    path = os.path.join(app_dir(), "song-all")
    os.makedirs(path, exist_ok=True)
    return path


def find_ffmpeg():
    """หา ffmpeg: ดูข้างๆ ตัวโปรแกรมก่อน แล้วค่อยหาใน PATH คืน None ถ้าไม่เจอ"""
    here = app_dir()
    for name in ("ffmpeg.exe", "ffmpeg"):
        if os.path.isfile(os.path.join(here, name)):
            return here
    exe = shutil.which("ffmpeg")
    return os.path.dirname(exe) if exe else None


def build_opts(logger=None, progress_hook=None, quality=DEFAULT_QUALITY,
               playlist=False, outdir=None, simulate=False):
    """สร้าง options ของ yt-dlp"""
    outdir = outdir or output_dir()
    opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(outdir, "%(title)s.%(ext)s"),
        "noplaylist": not playlist,
        "ignoreerrors": playlist,      # เพลลิสต์: ข้ามคลิปที่พังไปตัวเดียว ไม่ล้มทั้งชุด
        "windowsfilenames": True,      # กันชื่อไฟล์ที่ Windows ใช้ไม่ได้
        "quiet": True,
        "noprogress": True,            # เราแสดง progress เองผ่าน hook
        "retries": 5,
        "fragment_retries": 5,
        "writethumbnail": True,        # ไว้ฝังเป็นปกเพลง
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3",
             "preferredquality": quality},
            {"key": "FFmpegMetadata"},   # ใส่ชื่อเพลง/ศิลปินลงไฟล์
            {"key": "EmbedThumbnail"},   # ฝังปกเพลง
        ],
    }

    ffmpeg_dir = find_ffmpeg()
    if ffmpeg_dir:
        opts["ffmpeg_location"] = ffmpeg_dir

    if logger is not None:
        opts["logger"] = logger
    if progress_hook is not None:
        opts["progress_hooks"] = [progress_hook]
    if simulate:
        opts["simulate"] = True
        opts["skip_download"] = True
        opts["writethumbnail"] = False
        opts["postprocessors"] = []

    return opts


def download(url, **kwargs):
    """ดาวน์โหลด 1 ลิงก์ คืน exit code ของ yt-dlp (0 = สำเร็จ)"""
    with yt_dlp.YoutubeDL(build_opts(**kwargs)) as ydl:
        return ydl.download([url])


def probe(url, **kwargs):
    """ดึงข้อมูลคลิปโดยไม่โหลดไฟล์ ใช้เช็กว่าลิงก์ใช้ได้ไหม"""
    kwargs["simulate"] = True
    with yt_dlp.YoutubeDL(build_opts(**kwargs)) as ydl:
        return ydl.extract_info(url, download=False)


def version():
    return yt_dlp.version.__version__
