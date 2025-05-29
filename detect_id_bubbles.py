import cv2
import numpy as np
import matplotlib.pyplot as plt

# ---- INPUT ----
image_path = input("Enter image path (e.g. student_0001.png): ").strip()
output_preview = "grid_overlay_preview.png"

# ---- LOAD IMAGE ----
image = cv2.imread(image_path)
if image is None:
    raise FileNotFoundError(f"Could not read image: {image_path}")
h, w = image.shape[:2]

# ---- CROP RIGHT 5% ----
margin_crop = image[:, int(w * 0.95):]
gray = cv2.cvtColor(margin_crop, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
_, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# ---- FIND CONTOURS ----
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
    rectangles.append({
        'bbox': (cx - w_box // 2, cy - h_box // 2, cx + w_box // 2, cy + h_box // 2),
        'center': (cx, cy),
        'area': area
    })

# ---- SORT + FILTER BOXES 3 TO 12 ----
rectangles.sort(key=lambda r: r['center'][1])
filtered = rectangles[2:12]

# ---- DRAW RECTANGLES + CENTERS ----
preview = image.copy()
for i, rect in enumerate(filtered, start=3):
    x1, y1, x2, y2 = rect['bbox']
    cx, cy = rect['center']
    cv2.rectangle(preview, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.circle(preview, (cx, cy), 4, (0, 255, 0), -1)

# ---- COMPUTE REFERENCE POINTS ----
if len(filtered) >= 10:
    third_box = filtered[0]['center']     # box 3
    twelfth_box = filtered[-1]['center']  # box 12

    start_point = (third_box[0] - 588, third_box[1])  # purple
    end_point = (twelfth_box[0] - 103, twelfth_box[1]) # cyan

    # Draw reference points
    cv2.circle(preview, start_point, 8, (255, 0, 255), -1)  # Purple
    cv2.circle(preview, end_point, 8, (255, 255, 0), -1)    # Cyan

    # ---- GENERATE GRID ----
    grid_points = []
    for row in range(10):
        y = np.linspace(start_point[1], end_point[1], 10)[row]
        for col in range(9):
            x = np.linspace(start_point[0], end_point[0], 9)[col]
            pt = (int(round(x)), int(round(y)))
            grid_points.append(pt)
            cv2.circle(preview, pt, 3, (0, 0, 255), -1)  # Red grid point

    print(f"\n✅ Generated 90 grid points from {start_point} to {end_point}.")

# ---- SAVE + SHOW ----
cv2.imwrite(output_preview, preview)
print(f"🖼️ Grid overlay preview saved as {output_preview}")

plt.imshow(cv2.cvtColor(preview, cv2.COLOR_BGR2RGB))
plt.title("9×10 Grid Overlaid on Image")
plt.axis("off")
plt.show()
