import cv2
import numpy as np
import csv
import matplotlib
matplotlib.use("TkAgg")  # Use Tk backend
import matplotlib.pyplot as plt
import os
import random

clicked_points = []

def onclick(event):
    if event.xdata is not None and event.ydata is not None:
        x, y = int(event.xdata), int(event.ydata)
        clicked_points.append((x, y))
        print(f"Clicked: ({x}, {y})")
        ax.plot(event.xdata, event.ydata, 'go')
        fig.canvas.draw()

def interpolate_90(p1, p2):
    grid = []
    for row in range(10):
        for col in range(9):
            fx = col / 8
            fy = row / 9
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

# Load image and extract top-right quarter
image = cv2.imread(img_path)
h, w = image.shape[:2]
top_right = image[0:h // 2, w // 2:]

# Display top-right for clicking
top_right_rgb = cv2.cvtColor(top_right, cv2.COLOR_BGR2RGB)
fig, ax = plt.subplots()
ax.imshow(top_right_rgb)
cid = fig.canvas.mpl_connect('button_press_event', onclick)
print("🖱️ Click FIRST and LAST bubble in the 9x10 grid (top-right of image). Close the window when done.")
plt.show()

# Check for correct number of clicks
if len(clicked_points) != 2:
    raise ValueError("You must click exactly two points (first and last bubble in grid).")

# Offset coordinates to full image space
offset_x = w // 2
offset_y = 0
p1 = (clicked_points[0][0] + offset_x, clicked_points[0][1] + offset_y)
p2 = (clicked_points[1][0] + offset_x, clicked_points[1][1] + offset_y)
coords = interpolate_90(p1, p2)

# Save to CSV
csv_path = os.path.join(directory, "student_id_coords.csv")
with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["x", "y"])
    writer.writerows(coords)

# Preview on original image
preview = image.copy()
for (x, y) in coords:
    cv2.circle(preview, (x, y), 4, (0, 0, 255), -1)

preview_rgb = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
plt.figure(figsize=(10, 10))
plt.imshow(preview_rgb)
plt.title("Student ID Bubble Grid (Full Image Preview)")
plt.axis("off")
preview_path = os.path.join(directory, "student_id_preview.png")
plt.savefig(preview_path, dpi=300, bbox_inches='tight')
plt.show()
print(f"✅ Saved {len(coords)} bubbles to {csv_path}")
print(f"🖼️ Preview saved as {preview_path}")
