import fitz  # PyMuPDF
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------
# PDF to PNG splitter
# ------------------------------
def split_pdf_to_images(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        output_path = os.path.join(output_folder, f"student_{page_num + 1:04}.png")
        pix.save(output_path)
        print(f"✅ Saved {output_path}")

    doc.close()
    print("✅ PDF split complete.")

# ------------------------------
# Preprocess an image
# ------------------------------
def preprocess_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"❌ Could not load image: {image_path}")
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
    return image, gray, thresh

# ------------------------------
# Detect right-margin alignment marks
# ------------------------------
def find_right_margin_marks(thresh_img, min_x=1700, min_width=20, max_width=80):
    contours, _ = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    marks = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if x > min_x and min_width < w < max_width:
            marks.append((x, y, w, h))

    marks.sort(key=lambda b: b[1])
    return marks

# ------------------------------
# Generate grid using 4-column layout
# ------------------------------
def generate_grid_from_alignment_marks(marks, question_start=1):
    options = ['A', 'B', 'C', 'D', 'E']
    bubble_coords = {}

    # X start positions for 4 columns (estimated)
    col_x_starts = [150, 650, 1150, 1650]
    bubble_width = 25
    bubble_height = 25
    h_gap = 50  # Horizontal gap between options A–E

    marks = marks[12:42]  # First 12 are not answers
    if len(marks) < 30:
        print("⚠️ Warning: fewer than 30 answer rows found!")

    for row_index, (_, y, _, _) in enumerate(marks):
        for col_index, x_base in enumerate(col_x_starts):
            q_num = question_start + (row_index * 4) + col_index
            bubble_coords[q_num] = {}
            for opt_index, opt in enumerate(options):
                x = x_base + opt_index * h_gap
                bubble_coords[q_num][opt] = (x, y, bubble_width, bubble_height)

    return bubble_coords

# ------------------------------
# Extract filled bubbles
# ------------------------------
def extract_answers(thresh_img, bubble_coords):
    answers = {}
    filled_positions = []

    for q_num, options in bubble_coords.items():
        max_fill = 0
        selected_option = None
        selected_coords = None

        for option, (x, y, w, h) in options.items():
            roi = thresh_img[y:y+h, x:x+w]
            fill = np.sum(roi) / 255  # white pixels due to threshold inversion
            if fill > max_fill:
                max_fill = fill
                selected_option = option
                selected_coords = (x + w // 2, y + h // 2)

        answers[q_num] = selected_option
        if selected_coords:
            filled_positions.append((q_num, selected_coords))

    return answers, filled_positions

# ------------------------------
# Display detected answers on image
# ------------------------------
def show_overlay_on_image(image, filled_positions, output_folder):
    plt.figure(figsize=(12, 14))
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    plt.imshow(image_rgb)
    for q_num, (x, y) in filled_positions:
        plt.plot(x, y, 'ro')  # red dot
        plt.text(x + 5, y, f"{q_num}", color='yellow', fontsize=7)
    plt.title("Detected Answers (Q1–Q120)")
    plt.axis('off')
    output_path = os.path.join(output_folder, "overlay_result.png")
    plt.savefig(output_path)
    print(f"✅ Overlay image saved to {output_path}")

# ------------------------------
# Main program
# ------------------------------
def main():
    print("=== OMR Sheet Processor ===")

    input_folder = "student_pages"
    output_folder = input("Enter output folder for results: ").strip()
    os.makedirs(output_folder, exist_ok=True)

    if not os.path.exists(input_folder) or not os.listdir(input_folder):
        print(f"📂 '{input_folder}' not found or empty.")
        pdf_path = input("Enter path to scanned PDF: ").strip()
        split_pdf_to_images(pdf_path, input_folder)

    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".png")]
    if not image_files:
        print("❌ No PNG images found.")
        return

    image_path = os.path.join(input_folder, sorted(image_files)[0])
    print(f"🔍 Processing image: {image_path}")

    try:
        orig, gray, thresh = preprocess_image(image_path)
        print("🔎 Detecting right-margin alignment marks...")
        alignment_marks = find_right_margin_marks(thresh)

        print(f"✅ Found {len(alignment_marks)} alignment marks.")
        bubble_coords = generate_grid_from_alignment_marks(alignment_marks)
        answers, filled_positions = extract_answers(thresh, bubble_coords)

        print("🧾 Extracted Answers (Q1–Q120):")
        for q in range(1, 121):
            print(f"Q{q}: {answers.get(q)}")

        show_overlay_on_image(orig, filled_positions, output_folder)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
