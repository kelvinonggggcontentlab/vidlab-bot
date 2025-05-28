# 🎬 VidLab Marketing Telegram Bot

A fully automated Telegram bot for managing video footage submissions, editing tasks, and tracking status using Google Sheets, Dropbox, and AI video processing.

---

## 📦 Features

- Telegram staff verification (`/verify`)
- Role-based button menu for SA / Editor / Admin / BIG BOSS
- Google Sheets integration (Footage Log, Main Tracking, Staff List)
- Dropbox video path support
- Auto editing: cut silence, zoom effect, logo overlay (via `Vidlab_AI_AUTOEDIT.py`)
- Optional: face recognition, background blur, etc.

---

## 🧾 Role Permissions (Built-in)

| Role            | Permissions                                               |
|-----------------|-----------------------------------------------------------|
| **BIG BOSS**    | All-access. Can push system-wide notifications, approve everything. |
| **ADMIN**       | Same as BIG BOSS except not owner-level.                 |
| **SA**          | Upload footage, check status, view personal logs.         |
| **EDITOR (SENIOR)** | Can mark videos as done, review SA submissions.   |
| **EDITOR (JUNIOR)** | Limited edit permissions, but can submit videos.   |


## 🚀 Deployment: Render.com (Recommended)

### 1. Create GitHub Repo

Include:
- `start.py` (main bot script)
- `requirements.txt`
- `Vidlab_AI_AUTOEDIT.py` & other helper files
- DON'T commit JSON key file

### 2. Upload to GitHub

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/yourusername/vidlab-bot.git
git push -u origin main

## 👨‍💻 Maintainer

Maintain by **VidLab Bossku Team**.

Any issue? DM terus @CalvinVidlabMarketing_bot (TELEGRAM)  
Kalau urgent nak hantar video tak lepas, jerit kat group 😂

Semua bot ni dijaga oleh @Kelvin (a.k.a Ketua Auto-Edit Dunia)
Semua benda auto, tapi kita tetap standby untuk kau 24 jam (kecuali masa makan tengah hari).
