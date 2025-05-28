import cv2
import numpy as np
import matplotlib.pyplot as plt

def detect_red_outline_inner_edge(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image at {image_path} not found.")
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Broad red-orange threshold in HSV
    lower_red1 = np.array([0, 100, 50])
    upper_red1 = np.array([15, 255, 255])
    lower_red2 = np.array([160, 100, 50])
    upper_red2 = np.array([180, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    # Smooth, then edge detect
    blurred = cv2.GaussianBlur(mask, (5, 5), 0)
    edges = cv2.Canny(blurred, threshold1=30, threshold2=100)

    # Dilate to strengthen edge continuity
    kernel = np.ones((3, 3), np.uint8)
    edges_dilated = cv2.dilate(edges, kernel, iterations=1)

    # Contour detection
    contours, _ = cv2.findContours(edges_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the largest quadrilateral contour
    best_rect = None
    max_area = 0
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
        area = cv2.contourArea(approx)
        if area > max_area and len(approx) >= 4:
            max_area = area
            best_rect = approx

    # Draw the best contour (inner edge) carefully
    output = image_rgb.copy()
    if best_rect is not None:
        cv2.drawContours(output, [best_rect], -1, (0, 255, 0), 2)
    else:
        print("No red outline detected.")

    # Save output
    plt.figure(figsize=(10, 10))
    plt.imshow(output)
    plt.title("Inner Edge of Red ROI Box")
    plt.axis('off')
    plt.savefig("output_inner_edge.png", bbox_inches='tight', dpi=300)
    print("Saved result to output_inner_edge.png")

# Example usage
#detect_red_outline_inner_edge("screenshot/screenshot.png")
detect_red_outline_inner_edge("screenshots/scanned.png")
