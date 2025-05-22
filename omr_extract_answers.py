
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
    width_tol=12,
    height_tol=10,
    min_x_ratio=0.75,
    x_alignment_tolerance=6
):
    """Detect alignment marks near ~55x20px, grouped by vertical alignment."""
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

    if not x_groups:
        return []

    best_group = max(x_groups.values(), key=len)
    best_group.sort(key=lambda b: b[1])  # sort top-to-bottom
    return best_group

def generate_answer_bubble_coords(
    marks_13_to_42,
    col_x_starts,
    h_gap=62,
    bubble_w=30,
    bubble_h=30
):
    """Generate Q1–Q120 → A–E → (x, y, w, h) from alignment marks."""
    bubble_coords = {}
    options = ['A', 'B', 'C', 'D', 'E']

    for row_index, (_, y, _, _) in enumerate(marks_13_to_42):
        for col_index, x_base in enumerate(col_x_starts):
            q_num = row_index * 4 + col_index + 1
            bubble_coords[q_num] = {}
            for i, opt in enumerate(options):
                x = x_base + i * h_gap
                bubble_coords[q_num][opt] = (x, y, bubble_w, bubble_h)

    return bubble_coords

def extract_answers(thresh_img, bubble_coords, min_fill_threshold=1000):
    """Return most filled bubble per question (above threshold)."""
    answers = {}
    for q_num, options in bubble_coords.items():
        max_fill = 0
        selected_option = None

        for option, (x, y, w, h) in options.items():
            roi = thresh_img[y:y+h, x:x+w]
            fill = np.sum(roi) / 255
            if fill > max_fill and fill > min_fill_threshold:
                max_fill = fill
                selected_option = option

        answers[q_num] = selected_option
    return answers

def draw_extracted_answers(image, bubble_coords, answers, output_path):
    """Draw green dots and labels for extracted answers."""
    image_copy = image.copy()
    for q_num, options in bubble_coords.items():
        selected_option = answers.get(q_num)
        if selected_option:
            x, y, w, h = options[selected_option]
            center = (x + w // 2, y + h // 2)
            cv2.circle(image_copy, center, 6, (0, 255, 0), -1)
            cv2.putText(image_copy, f"Q{q_num}", (x + w + 5, y + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    image_rgb = cv2.cvtColor(image_copy, cv2.COLOR_BGR2RGB)
    plt.figure(figsize=(12, 14))
    plt.imshow(image_rgb)
    plt.title("Extracted Answers Overlay")
    plt.axis('off')
    plt.savefig(output_path)
    print(f"✅ Saved overlay with extracted answers to: {output_path}")

def main():
    print("=== OMR Answer Extractor ===")
    image_path = "student_pages/student_0001.png"
    output_path = "output/student_0001_answers.png"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        original, thresh = preprocess_image(image_path)
        marks = find_right_margin_marks(thresh)

        if len(marks) < 42:
            print(f"⚠️ Warning: Only {len(marks)} alignment marks detected. Results may be incomplete.")

        answer_marks = marks[12:42]  # skip first 12 (ID), take next 30 for Q1–Q120

        col_x_starts = [260, 858, 1453, 2055]  # from user-calibration
        h_gap = 62

        bubble_coords = generate_answer_bubble_coords(answer_marks, col_x_starts, h_gap=h_gap)
        answers = extract_answers(thresh, bubble_coords)

        print("\n🧾 Extracted Answers:")
        for q in range(1, 121):
            print(f"Q{q}: {answers.get(q)}")

        draw_extracted_answers(original, bubble_coords, answers, output_path)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
