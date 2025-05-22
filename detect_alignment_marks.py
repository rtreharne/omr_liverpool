import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

def preprocess_image(image_path):
    """Load and binarize the image for contour detection."""
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
    return image, thresh

def find_right_margin_marks(
    thresh_img,
    expected_width=55,
    expected_height=20,
    width_tol=10,
    height_tol=10,
    min_x_ratio=0.7,
    x_alignment_tolerance=10
):
    """
    Detect alignment marks around ~55x20px (+ ID marks), filter by vertical alignment.
    """
    height, width = thresh_img.shape
    min_x = int(width * min_x_ratio)

    contours, _ = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if (
            x >= min_x and
            abs(w - expected_width) <= width_tol and
            abs(h - expected_height) <= height_tol
        ):
            candidates.append((x, y, w, h))

    # Group by similar X positions
    x_groups = defaultdict(list)
    for box in candidates:
        x = box[0]
        matched = False
        for key in x_groups:
            if abs(x - key) <= x_alignment_tolerance:
                x_groups[key].append(box)
                matched = True
                break
        if not matched:
            x_groups[x].append(box)

    # Keep the group with the most boxes
    best_group = max(x_groups.values(), key=len) if x_groups else []
    best_group.sort(key=lambda b: b[1])  # top-to-bottom
    return best_group

def draw_alignment_marks_on_image(image, boxes, output_path):
    """Draw red rectangles over alignment marks and save as image."""
    image_copy = image.copy()
    for i, (x, y, w, h) in enumerate(boxes):
        cv2.rectangle(image_copy, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(image_copy, str(i + 1), (x + w + 5, y + h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

    image_rgb = cv2.cvtColor(image_copy, cv2.COLOR_BGR2RGB)
    plt.figure(figsize=(12, 14))
    plt.imshow(image_rgb)
    plt.title("All Detected Alignment Marks")
    plt.axis('off')
    plt.savefig(output_path)
    print(f"✅ Saved overlay image to {output_path}")

def main():
    print("=== Alignment Mark Detector ===")
    image_path = "student_pages/student_0001.png"#input("Enter path to scanned PNG image: ").strip()
    output_path = "output/student_0001.png"#input("Enter output image path (e.g., overlay.png): ").strip()

    try:
        original, thresh = preprocess_image(image_path)
        marks = find_right_margin_marks(
            thresh,
            expected_width=55,
            expected_height=20,
            width_tol=10,     # Looser width tolerance
            height_tol=10     # Looser height tolerance
        )

        print(f"✅ Found {len(marks)} vertically aligned alignment marks.")
        draw_alignment_marks_on_image(original, marks, output_path)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
