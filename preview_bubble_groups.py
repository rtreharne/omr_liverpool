import cv2
import csv
import numpy as np
import os

# Ask user for directory and image filename
directory = input("Enter the directory containing the scanned image and bubble_coords.csv: ").strip()
filename = input("Enter the name of the .png file to process: ").strip()
img_path = os.path.join(directory, filename)
coords_path = os.path.join(directory, "bubble_coords.csv")

# Load bubble coordinates
bubble_coords = []
with open(coords_path, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        bubble_coords.append((int(row["x"]), int(row["y"])))

# Load scanned image
img = cv2.imread(img_path)

# Detect red ROI box
def detect_red_box(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower1 = np.array([0, 100, 50])
    upper1 = np.array([15, 255, 255])
    lower2 = np.array([160, 100, 50])
    upper2 = np.array([180, 255, 255])
    mask = cv2.inRange(hsv, lower1, upper1) | cv2.inRange(hsv, lower2, upper2)
    edges = cv2.Canny(cv2.GaussianBlur(mask, (5, 5), 0), 30, 100)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    biggest = max(contours, key=cv2.contourArea)
    approx = cv2.approxPolyDP(biggest, 0.02 * cv2.arcLength(biggest, True), True)
    if len(approx) != 4:
        raise ValueError("Red ROI box not a rectangle.")
    return np.squeeze(approx, axis=1)

def order_points(pts):
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    return np.array([
        pts[np.argmin(s)],
        pts[np.argmin(diff)],
        pts[np.argmax(s)],
        pts[np.argmax(diff)]
    ], dtype="float32")

def warp_roi(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    width = int(max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl)))
    height = int(max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl)))
    dst = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (width, height))
    return warped

# Process image
box = detect_red_box(img)
roi = warp_roi(img, box)
roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
_, roi_thresh = cv2.threshold(roi_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# Estimate spacing
x_spacing = int(np.mean([
    bubble_coords[i + 1][0] - bubble_coords[i][0]
    for i in range(4)
]))
half_box = x_spacing // 2

# Analyze bubbles
answers = []
roi_annotated = roi.copy()

for i in range(0, len(bubble_coords), 5):
    group = bubble_coords[i:i + 5]
    if len(group) < 5:
        break

    fill_counts = []
    boxes = []

    for x, y in group:
        x1 = max(0, x - half_box)
        x2 = min(roi.shape[1], x + half_box)
        y1 = max(0, y - half_box)
        y2 = min(roi.shape[0], y + half_box)
        box = roi_thresh[y1:y2, x1:x2]
        filled = np.sum(box < 128)
        fill_counts.append(filled)
        boxes.append((x1, y1, x2, y2))

    selected_idx = int(np.argmax(fill_counts))
    selected_answer = "ABCDE"[selected_idx]
    answers.append(selected_answer)

    for j, (x1, y1, x2, y2) in enumerate(boxes):
        cv2.rectangle(roi_annotated, (x1, y1), (x2, y2), (0, 255, 0), 1)
        cv2.putText(roi_annotated, str(fill_counts[j]), (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        if j == selected_idx:
            cv2.rectangle(roi_annotated, (x1, y1), (x2, y2), (255, 0, 0), -1)
            cv2.putText(roi_annotated, str(fill_counts[j]), (x1 + 3, y1 + 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

# Save results
answers_csv_path = os.path.join(directory, "detected_answers.csv")
img_output_path = os.path.join(directory, "all_bubbles_annotated.png")

with open(answers_csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Question", "Answer"])
    for i, ans in enumerate(answers, 1):
        writer.writerow([i, ans])

cv2.imwrite(img_output_path, roi_annotated)
print(f"✅ Results saved to {answers_csv_path} and {img_output_path}")
