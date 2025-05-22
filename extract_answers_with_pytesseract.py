
import cv2
import os
import pytesseract
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
    print("=== pytesseract-Based Answer Extractor ===")
    image_path = "student_pages/student_0001.png"

    try:
        image, thresh = preprocess_image(image_path)
        marks = find_right_margin_marks(thresh)

        print(f"✅ Found {len(marks)} alignment marks.")
        cropped_roi = extract_text_roi(image, marks)

        # OCR config
        config = "--psm 6"  # Assume uniform block of text
        ocr_text = pytesseract.image_to_string(cropped_roi, config=config)

        print("\n🧾 OCR Output Between Markers 13–30:")
        print("------------------------------------")
        print(ocr_text)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
