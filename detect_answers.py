import os
import cv2
import csv
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import random
from tqdm import tqdm

# --- Settings ---
bubble_radius = 10
x_offset_3rd = -588
x_offset_12th = -103

# === Red Box Detection ===
def detect_red_box(image, min_width=0, min_height=0, pad=20):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower1 = np.array([0, 100, 50])
    upper1 = np.array([15, 255, 255])
    lower2 = np.array([160, 100, 50])
    upper2 = np.array([180, 255, 255])
    mask = cv2.inRange(hsv, lower1, upper1) | cv2.inRange(hsv, lower2, upper2)

    blurred = cv2.GaussianBlur(mask, (5, 5), 0)
    edges = cv2.Canny(blurred, 30, 100)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        raise ValueError("No red contours found.")

    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)
    if area < 1000:
        raise ValueError("Red contour too small to be ROI.")

    x, y, w, h = cv2.boundingRect(largest)

    if w < min_width or h < min_height:
        x = max(0, x - pad)
        y = max(0, y - pad)
        w = min(image.shape[1] - x, max(w + 2 * pad, min_width))
        h = min(image.shape[0] - y, max(h + 2 * pad, min_height))

    box = np.array([
        [x, y],
        [x + w, y],
        [x + w, y + h],
        [x, y + h]
    ], dtype=np.float32)

    return box

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

def add_purple_border(image, border=20):
    return cv2.copyMakeBorder(image, border, border, border, border, cv2.BORDER_CONSTANT, value=(255, 0, 255))

def interpolate_25(p1, p2):
    grid = []
    for row in range(5):
        for col in range(5):
            fx = col / 4
            fy = row / 4
            x = int(p1[0] + fx * (p2[0] - p1[0]))
            y = int(p1[1] + fy * (p2[1] - p1[1]))
            grid.append((x, y))
    return grid

def calibrate_bubbles(folder, coords_path, min_width, min_height):
    print("🔧 Step 1: Calibrating bubble positions (click pairs of FIRST and LAST bubbles in each 5x5 group)...")
    png_files = [f for f in os.listdir(folder) if f.lower().endswith(".png")]
    img_path = os.path.join(folder, random.choice(png_files))
    image = cv2.imread(img_path)
    box = detect_red_box(image, min_width, min_height)
    roi = warp_roi(image, box)
    roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

    clicked = []
    def onclick(event):
        if event.xdata is not None and event.ydata is not None:
            clicked.append((int(event.xdata), int(event.ydata)))
            ax.plot(event.xdata, event.ydata, 'go')
            fig.canvas.draw()

    fig, ax = plt.subplots()
    ax.imshow(roi_rgb)
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()

    if len(clicked) % 2 != 0 or len(clicked) < 2:
        raise ValueError("Need even number of bubble clicks.")

    bubble_coords = []
    for i in range(0, len(clicked), 2):
        bubble_coords.extend(interpolate_25(clicked[i], clicked[i+1]))

    with open(coords_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["x", "y"])
        writer.writerows(bubble_coords)

def calibrate_min_roi_size(folder, min_size_path):
    print("📐 Step 2: Calibrating minimum ROI dimensions (click top-left and bottom-right)...")
    png_files = [f for f in os.listdir(folder) if f.lower().endswith(".png")]
    img_path = os.path.join(folder, random.choice(png_files))
    image = cv2.imread(img_path)
    box = detect_red_box(image)
    roi = warp_roi(image, box)
    roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

    points = []
    def onclick(event):
        if event.xdata is not None and event.ydata is not None:
            points.append((int(event.xdata), int(event.ydata)))
            ax.plot(event.xdata, event.ydata, 'bo')
            fig.canvas.draw()

    fig, ax = plt.subplots()
    ax.imshow(roi_rgb)
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()

    if len(points) != 2:
        raise ValueError("Need exactly 2 points to define the minimum bounding box.")

    x1, y1 = points[0]
    x2, y2 = points[1]
    min_width = abs(x2 - x1)
    min_height = abs(y2 - y1)

    with open(min_size_path, "w") as f:
        f.write(f"{min_width},{min_height}")
    print(f"✅ Minimum ROI size set to {min_width}x{min_height}")
    return min_width, min_height

# === Main Pipeline ===
def main():
    folder = input("📂 Enter folder with PNG files: ").strip()
    coords_path = os.path.join(folder, "bubble_coords.csv")
    min_size_path = os.path.join(folder, "min_roi_size.txt")
    answer_csv_path = os.path.join(folder, "all_detected_answers.csv")
    student_id_csv_path = os.path.join(folder, "file_student_id.csv")
    annotated_dir = os.path.join(folder, "annotated")
    os.makedirs(annotated_dir, exist_ok=True)

    if not os.path.exists(min_size_path):
        min_width, min_height = calibrate_min_roi_size(folder, min_size_path)
    else:
        with open(min_size_path) as f:
            min_width, min_height = map(int, f.read().strip().split(","))

    if not os.path.exists(coords_path):
        calibrate_bubbles(folder, coords_path, min_width, min_height)

    with open(coords_path, newline="") as f:
        bubble_coords = [(int(row["x"]), int(row["y"])) for row in csv.DictReader(f)]

    half_box = int(np.mean([bubble_coords[i + 1][0] - bubble_coords[i][0] for i in range(4)]) // 2)
    png_files = sorted([f for f in os.listdir(folder) if f.lower().endswith(".png")])
    all_results = []
    student_ids = []

    for filename in tqdm(png_files, desc="Processing Sheets"):
        try:
            img = cv2.imread(os.path.join(folder, filename))
            box = detect_red_box(img, min_width, min_height)
            roi = warp_roi(img, box)

            roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            _, roi_thresh = cv2.threshold(roi_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            answers = []
            roi_annotated = roi.copy()

            for i in range(0, len(bubble_coords), 5):
                group = bubble_coords[i:i + 5]
                fill_counts, boxes = [], []
                for x, y in group:
                    x1, x2 = max(0, x - half_box), min(roi.shape[1], x + half_box)
                    y1, y2 = max(0, y - half_box), min(roi.shape[0], y + half_box)
                    box_img = roi_thresh[y1:y2, x1:x2]
                    fill_counts.append(np.sum(box_img < 128))
                    boxes.append((x1, y1, x2, y2))

                selected = int(np.argmax(fill_counts))
                answers.append("ABCDE"[selected])
                for j, (x1, y1, x2, y2) in enumerate(boxes):
                    color = (255, 0, 0) if j == selected else (0, 255, 0)
                    thickness = -1 if j == selected else 1
                    cv2.rectangle(roi_annotated, (x1, y1), (x2, y2), color, thickness)

            all_results.append([filename] + answers)
            student_grid = generate_student_id_grid(img)
            student_ids.append((filename, extract_student_id(img, student_grid)))
            cv2.imwrite(os.path.join(annotated_dir, f"{os.path.splitext(filename)[0]}_annotated.png"), roi_annotated)

        except Exception as e:
            print(f"\n❌ {filename} failed: {e}")

    with open(student_id_csv_path, "w", newline="") as f:
        csv.writer(f).writerows([["file", "student_id"]] + student_ids)

    student_map = dict(student_ids)
    header = ["filename"] + list(map(str, range(1, 36))) + ["student_id"]
    with open(answer_csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in all_results:
            writer.writerow(row + [student_map.get(row[0], "")])

    print("\n✅ Processing complete.")

# === Student ID Grid + Extraction ===
def generate_student_id_grid(image):
    h, w = image.shape[:2]
    right_crop = image[:, int(w * 0.95):]
    gray = cv2.cvtColor(right_crop, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    offset_x = int(w * 0.95)
    rects = [(x + w // 2 + offset_x, y + h // 2)
             for c in contours if cv2.contourArea(c) > 1000
             for x, y, w, h in [cv2.boundingRect(c)]]
    rects.sort(key=lambda pt: pt[1])
    if len(rects) < 12:
        raise ValueError("Not enough vertical markers")
    start = (rects[2][0] + x_offset_3rd, rects[2][1])
    end = (rects[11][0] + x_offset_12th, rects[11][1])

    grid = []
    for r in range(10):
        y = np.linspace(start[1], end[1], 10)[r]
        for c in range(9):
            x = np.linspace(start[0], end[0], 9)[c]
            grid.append((int(round(x)), int(round(y))))
    return grid

def extract_student_id(image, grid_points):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cols = [[] for _ in range(9)]
    for i, (x, y) in enumerate(grid_points):
        cols[i % 9].append((x, y))
    for col in cols:
        col.sort(key=lambda p: p[1])
    digits = []
    for col in cols:
        scores = []
        for (x, y) in col:
            roi = gray[y - bubble_radius:y + bubble_radius, x - bubble_radius:x + bubble_radius]
            scores.append(np.mean(cv2.GaussianBlur(roi, (3, 3), 0)) if roi.size else float("inf"))
        digits.append(np.argmin(scores))
    return ''.join(map(str, digits))

if __name__ == "__main__":
    main()
