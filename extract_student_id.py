import cv2
import pytesseract
from pytesseract import Output
import matplotlib.pyplot as plt
import re

# === Load and crop image ===
img_path = "testing/student_0001.png"  # 🔁 Change to your path
image = cv2.imread(img_path)
h, w = image.shape[:2]

# Crop top-right region (adjust as needed)
roi = image[0:int(0.25 * h), int(0.65 * w):w].copy()

# Preprocess
gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
gray = cv2.equalizeHist(gray)  # Enhance contrast

# OCR with bounding boxes
config = r'--oem 3 --psm 11 -c tessedit_char_whitelist=0123456789'
ocr_data = pytesseract.image_to_data(gray, config=config, output_type=Output.DICT)

# Filter for large digits
digit_boxes = []
digit_string = ""

for i, text in enumerate(ocr_data['text']):
    if text.strip().isdigit():
        w_box = ocr_data['width'][i]
        h_box = ocr_data['height'][i]
        if h_box > 10:  # Only keep large text regions
            digit_boxes.append((ocr_data['left'][i], ocr_data['top'][i],
                                ocr_data['width'][i], ocr_data['height'][i], text.strip()))

# Sort by x-coordinate
digit_boxes.sort(key=lambda b: b[0])
digit_string = ''.join([b[4] for b in digit_boxes])

# === Show result ===
annotated = roi.copy()
for x, y, bw, bh, t in digit_boxes:
    cv2.rectangle(annotated, (x, y), (x + bw, y + bh), (0, 255, 0), 2)
    cv2.putText(annotated, t, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

print(f"🆔 Extracted Digits: {digit_string if digit_string else '[None]'}")

plt.figure(figsize=(12, 6))
plt.imshow(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB))
plt.title(f"Detected Digits: {digit_string}")
plt.axis("off")
plt.show()
