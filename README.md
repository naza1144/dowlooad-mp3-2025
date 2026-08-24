# dowlooad-mp3-2025

โปรแกรมเล็กๆ สำหรับโหลดเสียงจาก YouTube มาเก็บเป็นไฟล์ MP3 หน้าตาเป็น GUI ง่ายๆ
วางลิงก์ กดปุ่ม แล้วรอ ไฟล์จะไปโผล่ในโฟลเดอร์ `song-all/`

**สิ่งที่ทำได้**
- โหลดเป็น MP3 เลือกคุณภาพได้ 128 / 192 / 256 / 320 kbps
- ใส่ชื่อเพลง ศิลปิน ปี และปกเพลงลงในไฟล์ให้อัตโนมัติ
- โหลดทั้งเพลลิสต์ได้ (ติ๊กช่อง "โหลดทั้งเพลลิสต์")
- มีแถบ progress + log บอกสถานะ และปุ่มเปิดโฟลเดอร์เพลง

---

## ติดตั้ง

### 1. ffmpeg (จำเป็น ไม่มีตัวนี้แปลง mp3 ไม่ได้)

บน Windows ใช้ [Chocolatey](https://chocolatey.org/install) ง่ายสุด — เปิด PowerShell **แบบ Run as Administrator** แล้วพิมพ์:

```powershell
choco install ffmpeg
```

ถ้าไม่อยากลง choco ก็โหลด `ffmpeg.exe` มาวางไว้ข้างๆ ตัวโปรแกรมได้เลย โปรแกรมหาเจอเอง

### 2. Python package

**Windows**

```powershell
pip install -U -r requirements.txt
```

**Linux (Debian / Ubuntu)**

Debian 12 ขึ้นไปห้าม pip ลงทับ Python ของระบบ (PEP 668) ถ้าลงตรงๆ จะเจอ
`error: externally-managed-environment` ต้องทำ venv แยกก่อน:

```bash
sudo apt install python3-venv python3-tk ffmpeg
```

```bash
python3 -m venv .venv && .venv/bin/pip install -U -r requirements.txt
```

แล้วรันด้วย `.venv/bin/python` แทน `python3` เสมอ

> `tkinter` ไม่ต้องลงผ่าน pip — มันติดมากับ Python อยู่แล้ว
> บน Debian/Ubuntu ตัว tkinter ถูกแยกออกมาเป็น `python3-tk` ต้อง apt ลงเพิ่มเอง
> (venv มองเห็น stdlib ของระบบ ลง apt แล้วใช้ได้เลย ไม่ต้องสร้าง venv ใหม่)

### 3. JavaScript runtime (แนะนำ)

yt-dlp รุ่นใหม่ต้องใช้ JS runtime ในการถอดรหัสลิงก์ของ YouTube ถ้าไม่มีจะขึ้น warning
และบางคลิปอาจโหลดไม่ได้ ติดตั้ง deno เพิ่มก็หายแล้ว:

```powershell
choco install deno
```

---

## วิธีใช้

```bash
python mainproject/main.py     # Windows
```

```bash
.venv/bin/python mainproject/main.py   # Linux (ที่ทำ venv ไว้)
```

หรือถ้าใช้ตัว `.exe` ที่ build ไว้แล้ว ก็ดับเบิลคลิกได้เลย — เพลงจะไปอยู่ในโฟลเดอร์
`song-all` ที่อยู่ข้างๆ ไฟล์ .exe

---

## build เป็น .exe เอง

```bash
pip install pyinstaller
pyinstaller main.spec
```

ได้ไฟล์ที่ `dist/main.exe` (ถ้าอยากได้ไอคอน ให้เอา `icon.ico` มาวางไว้ที่โฟลเดอร์หลักก่อน build)

---

## เจอปัญหา?

| อาการ | วิธีแก้ |
|---|---|
| `The page needs to be reloaded` / `Sign in to confirm` | yt-dlp เก่าไป — `pip install -U yt-dlp` |
| แปลงเป็น mp3 ไม่ได้ / ได้ไฟล์ `.webm` | ยังไม่ได้ลง ffmpeg (ดูข้อ 1) |
| `No supported JavaScript runtime` | ลง deno (ดูข้อ 3) |
| `error: externally-managed-environment` | Debian/Ubuntu ต้องใช้ venv (ดูข้อ 2) |
| `ModuleNotFoundError: No module named 'tkinter'` | `sudo apt install python3-tk` |
| บางคลิปโหลดไม่ได้ | คลิปอาจถูกจำกัดอายุหรือเป็นคลิปส่วนตัว |

**ข้อควรรู้:** YouTube แก้ระบบบ่อยมาก ถ้าอยู่ๆ โหลดไม่ได้ ให้ `pip install -U yt-dlp`
เป็นอย่างแรกเสมอ ส่วนใหญ่หายด้วยวิธีนี้

---

## โครงสร้างโปรเจกต์

```
mainproject/
  main.py         หน้าตาโปรแกรม (Tkinter)
  downloader.py   แกนดาวน์โหลด เรียกใช้เดี่ยวๆ ก็ได้
main.spec         ไฟล์ build ของ PyInstaller
song-all/         เพลงที่โหลดมาจะอยู่ที่นี่
requirements.txt
```

โหลดเฉพาะคลิปที่คุณมีสิทธิ์โหลดนะครับ
