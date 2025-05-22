import cv2
import os

click_points = []

def mouse_callback(event, x, y, flags, param):
    global click_points
    if event == cv2.EVENT_LBUTTONDOWN:
        click_points.append((x, y))
        print(f"🖱️ Click {len(click_points)}: x={x}, y={y}")
        cv2.circle(param, (x, y), 5, (0, 0, 255), -1)
        cv2.imshow("Click A-bubbles (4 columns) then A+B bubble", param)

def main():
    input_path = "student_pages/student_0001.png"
    if not os.path.exists(input_path):
        print(f"❌ Input image not found: {input_path}")
        return

    img = cv2.imread(input_path)
    clone = img.copy()

    print("🖱️ Click: A-bubble in each of the 4 columns, then A and B bubble in the same row.")
    print("Press any key when done.")

    cv2.namedWindow("Click A-bubbles (4 columns) then A+B bubble", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Click A-bubbles (4 columns) then A+B bubble", mouse_callback, clone)
    cv2.imshow("Click A-bubbles (4 columns) then A+B bubble", clone)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    if len(click_points) != 6:
        print("❌ You must click exactly 6 points (4 columns + A + B).")
        return

    col_x_starts = sorted([x for (x, y) in click_points[:4]])
    h_gap = abs(click_points[4][0] - click_points[5][0])

    print("\n✅ Final Output:")
    print(f"Column X starts: {col_x_starts}")
    print(f"Estimated bubble horizontal gap (A to B): {h_gap}")

if __name__ == "__main__":
    main()
