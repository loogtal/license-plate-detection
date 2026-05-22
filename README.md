# 🚗 Thai License Plate Detection & Auto-Logger

ระบบตรวจจับป้ายทะเบียนรถยนต์แบบ Real-time ด้วย AI
บันทึกข้อมูลลง Excel อัตโนมัติพร้อม timestamp

-----

## ✨ Features

|Feature             |Detail                 |
|--------------------|-----------------------|
|Real-time Detection |Webcam live feed       |
|Image Upload        |รองรับ JPG, PNG         |
|Auto OCR            |อ่านทะเบียนไทย + อังกฤษ   |
|Auto Excel Log      |บันทึกทะเบียน + วันที่ + เวลา|
|Duplicate Prevention|Cooldown 60 frames     |

-----

## 🚀 Quickstart

```bash
pip install -r requirements.txt

# Webcam mode
python detect.py

# Image mode
python detect.py photo.jpg
```

-----

## 📊 Output (license_plates.xlsx)

|วันที่       |เวลา    |ทะเบียน |แหล่งที่มา|
|----------|--------|-------|-------|
|23/05/2026|14:32:01|กข 1234|webcam |
|23/05/2026|14:35:22|ขค 5678|image  |

-----

## Tech Stack

- **OpenCV** — Image processing & contour detection
- **EasyOCR** — Thai/English text recognition
- **Pandas** — Excel logging
- **Python 3.11**

-----

## Author

**Praeploy Niamnil (Lise Rosario)**
B.Sc. Industrial Mathematics & Data Science, Mahidol University
github.com/loogtal