
import cv2
import os
import easyocr
from detect_alignment_marks import preprocess_image, find_right_margin_marks

def extract_text_roi(image, marks, q_start=12, q_end=42):
    """
    Crop region between 13th and 30th alignment marks (index 12 to 29)
    """
    if len(marks) < q_end + 1:
        raise ValueError("Not enough alignment marks to extract answers region.")

    y1 = marks[q_start][1] - 10
    y2 = marks[q_end][1] + 30
    cropped = image[y1:y2, :]
    return cropped

def main():
    print("=== EasyOCR-Based Answer Extractor ===")
    image_path = "student_pages/student_0001.png"

    try:
        image, thresh = preprocess_image(image_path)
        marks = find_right_margin_marks(thresh)

        print(f"✅ Found {len(marks)} alignment marks.")
        cropped_roi = extract_text_roi(image, marks)

        # Convert cropped ROI to RGB
        img_rgb = cv2.cvtColor(cropped_roi, cv2.COLOR_BGR2RGB)

        # Run EasyOCR
        reader = easyocr.Reader(['en'], gpu=False)
        results = reader.readtext(img_rgb)

        print("\n🧾 OCR Output Between Markers 13–30:")
        print("------------------------------------")
        for (bbox, text, conf) in results:
            print(f"{text} (conf: {conf:.2f})")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
