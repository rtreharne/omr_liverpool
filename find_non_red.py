import cv2
import numpy as np

def is_red_pixel(hsv_pixel):
    h, s, v = hsv_pixel
    return ((0 <= h <= 15 or 160 <= h <= 180) and s >= 100 and v >= 50)

def find_red_box_and_mask_non_red_inside(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image at {image_path} not found.")
    
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Mask for red box
    lower_red1 = np.array([0, 100, 50])
    upper_red1 = np.array([15, 255, 255])
    lower_red2 = np.array([160, 100, 50])
    upper_red2 = np.array([180, 255, 255])
    mask_red = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)

    # Find largest red contour (the ROI box)
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(mask_red, kernel, iterations=1)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest = max(contours, key=cv2.contourArea)

    # Get bounding rect and extract ROI
    x, y, w, h = cv2.boundingRect(largest)
    roi_bgr = image[y:y+h, x:x+w]
    roi_hsv = hsv[y:y+h, x:x+w]

    # Create a mask of non-red pixels inside the red box
    mask_inside = np.zeros((h, w), dtype=np.uint8)
    for i in range(h):
        for j in range(w):
            if not is_red_pixel(roi_hsv[i, j]):
                mask_inside[i, j] = 255  # Mark as "not red" (potential answer)

    # Save result
    cv2.imwrite("non_red_inside_roi.png", mask_inside)
    print("Saved: non_red_inside_roi.png")

# Run it
find_red_box_and_mask_non_red_inside("screenshots/scanned.png")
