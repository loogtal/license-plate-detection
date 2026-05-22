"""
License Plate Detection System
Supports: Real-time webcam + Image upload
Auto-saves to Excel with timestamp
"""

import cv2
import numpy as np
import easyocr
import pandas as pd
from datetime import datetime
import os
import sys

# Config
EXCEL_FILE = "license_plates.xlsx"
CONFIDENCE_THRESHOLD = 0.3

# Initialize OCR (Thai + English)
reader = easyocr.Reader(['th', 'en'], gpu=False)


def preprocess_plate(img):
    """Enhance plate image for better OCR accuracy."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh


def read_plate_text(plate_img):
    """Extract text from plate image using EasyOCR."""
    processed = preprocess_plate(plate_img)
    results = reader.readtext(processed, detail=1)
    
    texts = []
    for (_, text, conf) in results:
        if conf >= CONFIDENCE_THRESHOLD:
            clean = text.upper().replace(" ", "").strip()
            if len(clean) >= 3:
                texts.append(clean)
    
    return " ".join(texts) if texts else None


def detect_plate_region(frame):
    """Detect license plate region using contours."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.bilateralFilter(gray, 11, 17, 17)
    edges = cv2.Canny(blur, 30, 200)
    
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    
    plate_region = None
    plate_coords = None
    
    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.018 * peri, True)
        
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = w / h
            
            # Thai plates are roughly 4:1 to 6:1 ratio
            if 2.0 <= aspect_ratio <= 7.0 and w > 80:
                plate_region = frame[y:y+h, x:x+w]
                plate_coords = (x, y, w, h)
                break
    
    return plate_region, plate_coords


def save_to_excel(plate_text, source="webcam"):
    """Save detected plate to Excel file."""
    now = datetime.now()
    new_row = {
        "วันที่": now.strftime("%d/%m/%Y"),
        "เวลา": now.strftime("%H:%M:%S"),
        "ทะเบียน": plate_text,
        "แหล่งที่มา": source,
    }
    
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        df = pd.DataFrame([new_row])
    
    df.to_excel(EXCEL_FILE, index=False)
    print(f"✅ บันทึกแล้ว: {plate_text} ({now.strftime('%H:%M:%S')})")
    return df


def process_image(image_path):
    """Process a single image file."""
    print(f"\n📸 กำลังประมวลผล: {image_path}")
    
    frame = cv2.imread(image_path)
    if frame is None:
        print("❌ ไม่สามารถโหลดรูปได้")
        return
    
    plate_region, coords = detect_plate_region(frame)
    
    if plate_region is not None:
        text = read_plate_text(plate_region)
        x, y, w, h = coords
        
        if text:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, text, (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            save_to_excel(text, source="image")
            print(f"🚗 ทะเบียนที่พบ: {text}")
        else:
            print("⚠️ พบป้ายทะเบียนแต่อ่านข้อความไม่ได้")
    else:
        print("❌ ไม่พบป้ายทะเบียนในรูป")
    
    cv2.imshow("License Plate Detection", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def run_webcam():
    """Real-time webcam detection."""
    print("\n🎥 เริ่มต้น Real-time Detection")
    print("กด 'S' เพื่อ capture | กด 'Q' เพื่อออก\n")
    
    cap = cv2.VideoCapture(0)
    last_saved = ""
    cooldown = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        display = frame.copy()
        plate_region, coords = detect_plate_region(frame)
        
        if plate_region is not None and coords:
            x, y, w, h = coords
            cv2.rectangle(display, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(display, "PLATE DETECTED", (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Auto-save every 60 frames to avoid duplicates
        if plate_region is not None and cooldown == 0:
            text = read_plate_text(plate_region)
            if text and text != last_saved:
                save_to_excel(text, source="webcam")
                last_saved = text
                cooldown = 60
                
                x, y, w, h = coords
                cv2.putText(display, f"SAVED: {text}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)
        
        if cooldown > 0:
            cooldown -= 1
        
        # Status bar
        cv2.putText(display, "S=Capture  Q=Quit", (10, display.shape[0]-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        cv2.imshow("License Plate Detection - Real Time", display)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s') and plate_region is not None:
            text = read_plate_text(plate_region)
            if text:
                save_to_excel(text, source="manual")
                print(f"📸 Manual capture: {text}")
    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Image mode
        process_image(sys.argv[1])
    else:
        # Webcam mode
        run_webcam()
