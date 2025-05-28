import cv2
import numpy as np

def extract_red_roi(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 100, 50])
    upper_red1 = np.array([15, 255, 255])
    lower_red2 = np.array([160, 100, 50])
    upper_red2 = np.array([180, 255, 255])
    mask = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)
    kernel = np.ones((3, 3), np.uint8)
    blurred = cv2.GaussianBlur(mask, (5, 5), 0)
    edges = cv2.Canny(blurred, 30, 100)
    dilated = cv2.dilate(edges, kernel, iterations=1)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("No red ROI detected.")
    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)
    roi = image[y:y+h, x:x+w]
    return roi

def get_coordinates_from_user():
    print("Enter 5 (x, y) coordinates for bubbles A, B, C, D, E in order:")
    coords = []
    for label in ["A", "B", "C", "D", "E"]:
        raw = input(f"  {label}: ").strip()
        try:
            x, y = map(int, raw.strip("()").split(","))
            coords.append((x, y))
        except Exception as e:
            print(f"Invalid format. Use (x, y). Error: {e}")
            return []
    return coords

def analyze_bubbles(image_path):
    full_image = cv2.imread(image_path)
    if full_image is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")
    roi = extract_red_roi(full_image)
    cv2.imwrite("roi_debug.png", roi)
    print("Saved ROI crop to roi_debug.png — open it and pick your (x, y) coordinates.")

    coords = get_coordinates_from_user()
    if len(coords) != 5:
        print("Aborting due to invalid coordinate entry.")
        return

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 15, 10)

    print("\nFilled pixel ratios:")
    bubble_values = {}
    for i, (x, y) in enumerate(coords):
        label = chr(65 + i)
        size = 20
        x1, x2 = max(0, x - size), min(thresh.shape[1], x + size)
        y1, y2 = max(0, y - size), min(thresh.shape[0], y + size)
        region = thresh[y1:y2, x1:x2]

        if region.size == 0:
            print(f"  Warning: region for Bubble {label} is empty or out of bounds. Skipping.")
            continue

        filled_ratio = np.sum(region == 255) / (region.shape[0] * region.shape[1])
        bubble_values[label] = filled_ratio
        print(f"  Bubble {label}: {filled_ratio:.3f}")

    if not bubble_values:
        print("No valid bubbles could be analyzed. Check your coordinates.")
        return

    most_filled = max(bubble_values, key=bubble_values.get)
    print(f"\nMost filled bubble: {most_filled}")

if __name__ == "__main__":
    analyze_bubbles("screenshots/scanned.png")
