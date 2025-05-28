import cv2
import csv
import numpy as np
import os
from tqdm import tqdm  # Progress bar

# Get directory
directory = input("Enter the directory containing scanned .png files and bubble_coords.csv: ").strip()
coords_path = os.path.join(directory, "bubble_coords.csv")
annotated_dir = os.path.join(directory, "annotated")
os.makedirs(annotated_dir, exist_ok=True)

# Load bubble coordinates
bubble_coords = []
with open(coords_path, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        bubble_coords.append((int(row["x"]), int(row["y"])))

# Detect ROI box
def detect_red_box(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define red color ranges in HSV
    lower1 = np.array([0, 100, 50])
    upper1 = np.array([15, 255, 255])
    lower2 = np.array([160, 100, 50])
    upper2 = np.array([180, 255, 255])
    
    # Create binary mask for red regions
    mask = cv2.inRange(hsv, lower1, upper1) | cv2.inRange(hsv, lower2, upper2)

    # Morphological closing to fill gaps
    kernel = np.ones((5, 5), np.uint8)
    mask_closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Edge detection
    edges = cv2.Canny(mask_closed, 30, 100)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        raise ValueError("No contours found.")

    # Filter by minimum area
    min_area = 1000  # pixels
    contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

    if not contours:
        raise ValueError("No large enough red box found.")

    # Find largest contour
    biggest = max(contours, key=cv2.contourArea)

    # Approximate to polygon
    peri = cv2.arcLength(biggest, True)
    approx = cv2.approxPolyDP(biggest, 0.04 * peri, True)  # relaxed from 0.02 to 0.04

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

# Estimate spacing
x_spacing = int(np.mean([
    bubble_coords[i + 1][0] - bubble_coords[i][0]
    for i in range(4)
]))
half_box = x_spacing // 2

# Results
all_results = []

# List all PNGs
png_files = sorted([f for f in os.listdir(directory) if f.lower().endswith(".png")])

# Process each image with progress bar
for filename in tqdm(png_files, desc="Processing sheets"):
    img_path = os.path.join(directory, filename)
    img = cv2.imread(img_path)

    try:
        box = detect_red_box(img)
        roi = warp_roi(img, box)
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, roi_thresh = cv2.threshold(roi_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

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

        output_img_name = os.path.splitext(filename)[0] + "_annotated.png"
        output_img_path = os.path.join(annotated_dir, output_img_name)
        cv2.imwrite(output_img_path, roi_annotated)

        all_results.append([filename] + answers)

    except Exception as e:
        print(f"\n❌ Error processing {filename}: {e}")

# Save all results to CSV
header = ["filename"] + [str(i) for i in range(1, 36)]
csv_path = os.path.join(directory, "all_detected_answers.csv")
with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(all_results)

print(f"\n✅ Completed. Answers saved to: {csv_path}")
print(f"🖼️ Annotated images saved to: {annotated_dir}")
