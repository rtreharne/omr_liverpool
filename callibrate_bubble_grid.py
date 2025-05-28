import cv2
import numpy as np
import csv
import matplotlib
matplotlib.use("TkAgg")  # Use Tk backend
import matplotlib.pyplot as plt
import os
import random

clicked_points = []

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

def onclick(event):
    if event.xdata is not None and event.ydata is not None:
        clicked_points.append((int(event.xdata), int(event.ydata)))
        print(f"Clicked: ({int(event.xdata)}, {int(event.ydata)})")
        ax.plot(event.xdata, event.ydata, 'go')
        fig.canvas.draw()

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

# Ask for directory and choose random image
directory = input("Enter directory containing .png files: ")
png_files = [f for f in os.listdir(directory) if f.lower().endswith(".png")]
if not png_files:
    raise ValueError("No PNG files found in the specified directory.")
random_file = random.choice(png_files)
img_path = os.path.join(directory, random_file)
print(f"📄 Selected random image: {img_path}")

# Load and prepare image
image = cv2.imread(img_path)
box = detect_red_box(image)
roi = warp_roi(image, box)

# Save ROI image
roi_path = os.path.join(directory, "roi_flattened.png")
cv2.imwrite(roi_path, roi)
print(f"🖼️ Saved flattened ROI as {roi_path}")

roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

# Show image and capture clicks
fig, ax = plt.subplots()
ax.imshow(roi_rgb)
cid = fig.canvas.mpl_connect('button_press_event', onclick)
print("🖱️ Click FIRST and LAST bubble in each group of 25 (5x5). Close the window when done.")
plt.show()

# Process clicks
if len(clicked_points) % 2 != 0:
    raise ValueError("Uneven number of points. Must be pairs.")

bubble_coords = []
for i in range(0, len(clicked_points), 2):
    p1 = clicked_points[i]
    p2 = clicked_points[i + 1]
    bubble_coords.extend(interpolate_25(p1, p2))

# Save to CSV
csv_path = os.path.join(directory, "bubble_coords.csv")
with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["x", "y"])
    writer.writerows(bubble_coords)

# Preview result
for (x, y) in bubble_coords:
    cv2.circle(roi_rgb, (x, y), 4, (255, 0, 0), -1)

plt.figure(figsize=(10, 10))
plt.imshow(roi_rgb)
plt.title("Bubble Grid Preview")
plt.axis("off")
preview_path = os.path.join(directory, "bubble_calibrated_preview.png")
plt.savefig(preview_path, dpi=300, bbox_inches='tight')
plt.show()
print(f"✅ Saved {len(bubble_coords)} bubbles to {csv_path}")
print(f"🖼️ Preview saved as {preview_path}")
