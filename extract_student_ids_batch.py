import cv2
import numpy as np
import csv
import os
import matplotlib.pyplot as plt
from tqdm import tqdm

# === CONFIGURATION ===
bubble_radius = 10
x_offset_3rd = -588
x_offset_12th = -103

# === FUNCTION: Generate 9×10 Grid from a Single Image ===
def generate_bubble_grid(image):
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
        if area <= 1000:
            continue
        x, y, w_box, h_box = cv2.boundingRect(cnt)
        cx = x + w_box // 2 + offset_x
        cy = y + h_box // 2
        rectangles.append({'center': (cx, cy)})

    rectangles.sort(key=lambda r: r['center'][1])
    if len(rectangles) < 12:
        raise ValueError("Less than 12 alignment boxes found.")

    third_box = rectangles[2]['center']
    twelfth_box = rectangles[11]['center']

    start_point = (third_box[0] + x_offset_3rd, third_box[1])
    end_point = (twelfth_box[0] + x_offset_12th, twelfth_box[1])

    grid_points = []
    for row in range(10):
        y = np.linspace(start_point[1], end_point[1], 10)[row]
        for col in range(9):
            x = np.linspace(start_point[0], end_point[0], 9)[col]
            grid_points.append((int(round(x)), int(round(y))))
    return grid_points

# === FUNCTION: Extract student ID from one image ===
def extract_student_id(image, grid_points):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    columns = [[] for _ in range(9)]
    for i, (x, y) in enumerate(grid_points):
        col_index = i % 9
        columns[col_index].append((x, y))
    for col in columns:
        col.sort(key=lambda p: p[1])  # top to bottom

    filled_digits = []
    for col in columns:
        scores = []
        for (x, y) in col:
            roi = gray[y - bubble_radius:y + bubble_radius, x - bubble_radius:x + bubble_radius]
            if roi.shape[0] == 0 or roi.shape[1] == 0:
                scores.append(float("inf"))
                continue
            blurred = cv2.GaussianBlur(roi, (3, 3), 0)
            scores.append(np.mean(blurred))
        filled_digits.append(int(np.argmin(scores)))
    return ''.join(map(str, filled_digits))

# === FUNCTION: Draw results on image ===
def draw_preview(image, grid_points, filled_digits, preview_path):
    output = image.copy()
    for col_index in range(9):
        for row_index in range(10):
            i = col_index * 10 + row_index
            x, y = grid_points[i]
            color = (0, 255, 0) if row_index == filled_digits[col_index] else (0, 0, 255)
            cv2.circle(output, (x, y), bubble_radius, color, 2)
    cv2.imwrite(preview_path, output)

# === MAIN BATCH PROCESSING ===
def main():
    folder = input("Enter path to folder containing PNG files: ").strip()
    output_csv_path = os.path.join(folder, "file_student_id.csv")
    output_preview_folder = os.path.join(folder, "student_id_previews")
    os.makedirs(output_preview_folder, exist_ok=True)

    results = []
    png_files = sorted([f for f in os.listdir(folder) if f.lower().endswith(".png")])
    if not png_files:
        raise FileNotFoundError("No PNG files found in the folder.")

    for filename in tqdm(png_files, desc="Extracting Student IDs"):
        image_path = os.path.join(folder, filename)
        image = cv2.imread(image_path)
        if image is None:
            print(f"⚠️ Skipping unreadable file: {filename}")
            continue
        try:
            grid_points = generate_bubble_grid(image)
            student_id_str = extract_student_id(image, grid_points)
            results.append((filename, student_id_str))

            preview_path = os.path.join(output_preview_folder, f"{os.path.splitext(filename)[0]}_detected.png")
            draw_preview(image, grid_points, list(map(int, student_id_str)), preview_path)
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            continue

    # Save CSV
    with open(output_csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["file", "student_id"])
        writer.writerows(results)

    print(f"\n📄 Saved student IDs to: {output_csv_path}")
    print(f"🖼️ Previews saved to: {output_preview_folder}")

if __name__ == "__main__":
    main()
