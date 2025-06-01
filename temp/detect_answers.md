# 🧪 Answer Detection and Student ID Extraction (`detect_answers.py`)

This script performs the core Optical Mark Recognition (OMR) task for the S.T.A.P.L.E. system. It extracts student answers from scanned PNG images and automatically reads student IDs from a 9×10 grid of bubbles.

---

1. **What It Does**

- Detects and warps the red ROI box from each PNG image.
- Extracts multiple-choice answers using calibrated bubble positions.
- Reads the student ID from a 9×10 grid using vertical alignment boxes.
- Saves annotated images, extracted answers, and student IDs to CSV.

---

2. **How to Use**

Run the script in your terminal:

```bash
python detect_answers.py
```

You will be prompted to:

- Enter the path to the folder containing PNG files (output from `process_pdf.py`).

The script will:

- Load or prompt for **bubble calibration** and **minimum ROI size**.
- Extract answers from each image.
- Read student ID digits using a grid aligned by right-edge markers.
- Generate annotated output and save results.

---

3. **What It Produces**

Inside the input folder, the following files/folders will be created:

- `bubble_coords.csv`: Coordinates of each bubble (saved during calibration).
- `min_roi_size.txt`: Minimum acceptable red box dimensions.
- `annotated/`: Folder containing annotated PNGs with detected answers.
- `all_detected_answers.csv`: A table of filenames and selected answers, with student ID appended.
- `file_student_id.csv`: A mapping of image filenames to extracted student IDs.

---

4. **Calibration Steps (Interactive)**

The first time the script is run for a folder, it will guide you through two setup steps:

- **Step 1**: Click the top-left and bottom-right of a typical red ROI box (to set minimum width/height).
- **Step 2**: Click the first and last bubbles of each 5×5 grid to interpolate coordinates.

These steps ensure accurate bubble alignment across all scanned sheets.

---

5. **Technical Notes**

- Uses OpenCV for image processing and Matplotlib for interactive point selection.
- Bubble fill intensity is measured using a fixed window (`half_box`), derived from calibration.
- Student IDs are extracted from a 9×10 grid based on two red alignment marks on the right margin.
- The ID is composed by selecting the darkest bubble in each of 9 columns.

---

Make sure this script is run **after** converting PDFs to PNGs using `process_pdf.py`.
