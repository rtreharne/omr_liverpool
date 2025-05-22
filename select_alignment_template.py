import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
import cv2
import os

rect_coords = None

def onselect(eclick, erelease):
    global rect_coords
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata

    rect_x = int(min(x1, x2))
    rect_y = int(min(y1, y2))
    rect_w = int(abs(x2 - x1))
    rect_h = int(abs(y2 - y1))

    rect_coords = (rect_x, rect_y, rect_w, rect_h)
    print(f"✅ Rectangle: x={rect_x}, y={rect_y}, width={rect_w}, height={rect_h}")
    plt.close()

def main():
    input_path = "student_pages/student_0001.png"
    output_path = "output/student_0001.png"

    if not os.path.exists(input_path):
        print(f"❌ Input image not found at: {input_path}")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Load image using OpenCV, convert to RGB for matplotlib
    img_bgr = cv2.imread(input_path)
    if img_bgr is None:
        print(f"❌ Failed to read image with cv2.")
        return
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    # Show image using matplotlib
    fig, ax = plt.subplots(figsize=(12, 14))
    ax.imshow(img_rgb)
    ax.set_title("Zoom and pan, then click and drag to select a rectangle.\nClose the window when done.")

    toggle_selector = RectangleSelector(
        ax, onselect, useblit=True,
        button=[1],  # Left-click
        minspanx=5, minspany=5,
        spancoords='pixels',
        interactive=True
    )

    plt.show()

    # If user selected a rectangle, draw it and save
    if rect_coords:
        x, y, w, h = rect_coords
        cv2.rectangle(img_bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imwrite(output_path, img_bgr)
        print(f"✅ Saved overlay with rectangle to: {output_path}")
    else:
        print("❌ No rectangle was selected.")

if __name__ == "__main__":
    main()
