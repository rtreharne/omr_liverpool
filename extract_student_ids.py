import cv2
import numpy as np
import csv
import os
import matplotlib.pyplot as plt

# Parameters
image_path = input("Enter path to image: ")
csv_path = input("Enter path to student_id_coords.csv: ")
output_preview = "student_id_detected.png"
bubble_radius = 10  # adjust if needed

# Load image
image = cv2.imread(image_path)
if image is None:
    raise FileNotFoundError(f"Image not found: {image_path}")

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Load bubble coordinates
coords = []
with open(csv_path, "r") as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    for row in reader:
        coords.append((int(row[0]), int(row[1])))

if len(coords) != 90:
    raise ValueError("Expected 90 bubble coordinates.")

# Group into 9 columns of 10 rows
columns = [[] for _ in range(9)]
for i, coord in enumerate(coords):
    col_index = i % 9
    columns[col_index].append(coord)

# Sort each column top-to-bottom
for col in columns:
    col.sort(key=lambda p: p[1])  # sort by y-coordinate

# Detect filled bubbles
filled_digits = []
for col_index, col in enumerate(columns):
    scores = []
    for (x, y) in col:
        roi = gray[y - bubble_radius:y + bubble_radius, x - bubble_radius:x + bubble_radius]
        if roi.shape[0] == 0 or roi.shape[1] == 0:
            scores.append(float("inf"))
            continue
        blurred = cv2.GaussianBlur(roi, (3, 3), 0)
        filled_score = np.mean(blurred)  # lower means darker
        scores.append(filled_score)
    best_digit = int(np.argmin(scores))  # digit 0–9
    filled_digits.append(best_digit)

# Annotate detected digits
output_image = image.copy()
for col_index, col in enumerate(columns):
    for row_index, (x, y) in enumerate(col):
        color = (0, 255, 0) if row_index == filled_digits[col_index] else (0, 0, 255)
        cv2.circle(output_image, (x, y), bubble_radius, color, 2)

# Save and show result
cv2.imwrite(output_preview, output_image)
print(f"✅ Saved output with detected digits to: {output_preview}")
print(f"📄 Extracted Student ID: {''.join(map(str, filled_digits))}")

# Optionally show with matplotlib
plt.imshow(cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB))
plt.title(f"Detected Student ID: {''.join(map(str, filled_digits))}")
plt.axis("off")
plt.show()
