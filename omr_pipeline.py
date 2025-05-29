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

# === Interactive Calibration if Needed ===
def detect_red_box(image):
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

    # Use bounding box instead of requiring exact 4-point polygon
    x, y, w, h = cv2.boundingRect(largest)
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

def run_calibration(folder, coords_path):
    print("🔧 Calibrating bubble grid (interactive)...")
    png_files = [f for f in os.listdir(folder) if f.lower().endswith(".png")]
    random_file = random.choice(png_files)
    img_path = os.path.join(folder, random_file)
    image = cv2.imread(img_path)
    box = detect_red_box(image)
    roi = warp_roi(image, box)
    roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

    clicked_points = []
    def onclick(event):
        if event.xdata is not None and event.ydata is not None:
            clicked_points.append((int(event.xdata), int(event.ydata)))
            ax.plot(event.xdata, event.ydata, 'go')
            fig.canvas.draw()

    fig, ax = plt.subplots()
    ax.imshow(roi_rgb)
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    print("🖱️ Click FIRST and LAST bubble in each 5x5 group (close window when done)...")
    plt.show()

    if len(clicked_points) % 2 != 0:
        raise ValueError("Uneven number of points. Must be pairs.")

    bubble_coords = []
    for i in range(0, len(clicked_points), 2):
        p1 = clicked_points[i]
        p2 = clicked_points[i + 1]
        bubble_coords.extend(interpolate_25(p1, p2))

    with open(coords_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["x", "y"])
        writer.writerows(bubble_coords)

    print(f"✅ Saved {len(bubble_coords)} bubble coordinates to: {coords_path}")

# === Student ID Grid Generation ===
def generate_student_id_grid(image):
    h, w = image.shape[:2]
    right_crop = image[:, int(w * 0.95):]
    gray = cv2.cvtColor(right_crop, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    offset_x = int(w * 0.95)
    rectangles = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 1000:
            x, y, w_box, h_box = cv2.boundingRect(cnt)
            cx = x + w_box // 2 + offset_x
            cy = y + h_box // 2
            rectangles.append((cx, cy))

    rectangles.sort(key=lambda pt: pt[1])
    if len(rectangles) < 12:
        raise ValueError("Less than 12 vertical alignment markers found.")
    start = (rectangles[2][0] + x_offset_3rd, rectangles[2][1])
    end = (rectangles[11][0] + x_offset_12th, rectangles[11][1])

    grid = []
    for row in range(10):
        y = np.linspace(start[1], end[1], 10)[row]
        for col in range(9):
            x = np.linspace(start[0], end[0], 9)[col]
            grid.append((int(round(x)), int(round(y))))
    return grid

def extract_student_id(image, grid_points):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    columns = [[] for _ in range(9)]
    for i, (x, y) in enumerate(grid_points):
        columns[i % 9].append((x, y))
    for col in columns:
        col.sort(key=lambda p: p[1])
    digits = []
    for col in columns:
        scores = []
        for (x, y) in col:
            roi = gray[y - bubble_radius:y + bubble_radius, x - bubble_radius:x + bubble_radius]
            if roi.shape[0] == 0 or roi.shape[1] == 0:
                scores.append(float("inf"))
                continue
            scores.append(np.mean(cv2.GaussianBlur(roi, (3, 3), 0)))
        digits.append(np.argmin(scores))
    return ''.join(map(str, digits))

# === Main Pipeline ===
def main():
    folder = input("Enter path to folder containing PNG files: ").strip()
    coords_path = os.path.join(folder, "bubble_coords.csv")
    answer_csv_path = os.path.join(folder, "all_detected_answers.csv")
    student_id_csv_path = os.path.join(folder, "file_student_id.csv")
    annotated_dir = os.path.join(folder, "annotated")
    os.makedirs(annotated_dir, exist_ok=True)

    if not os.path.exists(coords_path):
        run_calibration(folder, coords_path)

    # Load bubble coordinates
    bubble_coords = []
    with open(coords_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bubble_coords.append((int(row["x"]), int(row["y"])))

    # Estimate spacing
    x_spacing = int(np.mean([
        bubble_coords[i + 1][0] - bubble_coords[i][0]
        for i in range(4)
    ]))
    half_box = x_spacing // 2

    # Collect PNGs
    png_files = sorted([f for f in os.listdir(folder) if f.lower().endswith(".png")])
    all_results = []
    student_ids = []

    for filename in tqdm(png_files, desc="Processing Sheets"):
        img_path = os.path.join(folder, filename)
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
                    box_img = roi_thresh[y1:y2, x1:x2]
                    filled = np.sum(box_img < 128)
                    fill_counts.append(filled)
                    boxes.append((x1, y1, x2, y2))

                selected = int(np.argmax(fill_counts))
                answers.append("ABCDE"[selected])
                for j, (x1, y1, x2, y2) in enumerate(boxes):
                    cv2.rectangle(roi_annotated, (x1, y1), (x2, y2), (0, 255, 0), 1)
                    if j == selected:
                        cv2.rectangle(roi_annotated, (x1, y1), (x2, y2), (255, 0, 0), -1)

            all_results.append([filename] + answers)
            student_grid = generate_student_id_grid(img)
            student_id = extract_student_id(img, student_grid)
            student_ids.append((filename, student_id))

            out_img = os.path.join(annotated_dir, f"{os.path.splitext(filename)[0]}_annotated.png")
            cv2.imwrite(out_img, roi_annotated)

        except Exception as e:
            print(f"\n❌ Error processing {filename}: {e}")

    # Save student_id.csv
    with open(student_id_csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["file", "student_id"])
        writer.writerows(student_ids)

    # Save answers + student ID merged
    student_id_map = {row[0]: row[1] for row in student_ids}
    header = ["filename"] + [str(i) for i in range(1, 36)] + ["student_id"]
    with open(answer_csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in all_results:
            sid = student_id_map.get(row[0], "")
            writer.writerow(row + [sid])

    print(f"\n✅ All results saved to {answer_csv_path}")
    print(f"🆔 Student IDs saved to {student_id_csv_path}")
    print(f"🖼️ Annotated images in {annotated_dir}")

if __name__ == "__main__":
    main()
