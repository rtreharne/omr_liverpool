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


---

6. **Sample Output (`all_detected_answers.csv`)**

Below is a snippet of what the output CSV file looks like after running the script:

```csv
filename,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,student_id
answers_____,B,D,B,B,C,C,A,C,B,D,C,B,B,C,A,B,A,C,C,A,C,A,B,B,D,B,A,D,A,D,D,B,B,B,B,699889898
page_002.png,C,D,B,C,D,C,C,B,B,D,B,C,A,D,B,A,B,D,C,D,C,A,B,C,C,D,A,D,C,D,D,A,B,B,B,201809558
page_003.png,B,C,A,A,C,A,A,C,B,D,D,A,B,C,A,D,D,B,B,A,C,A,B,C,C,B,A,D,A,D,C,B,B,B,B,201804043
page_004.png,D,B,B,A,C,C,C,C,B,A,C,D,A,D,B,D,A,B,B,D,C,B,C,A,A,B,A,D,C,D,C,A,B,D,D,201819578
page_005.png,D,D,B,C,D,C,B,C,A,D,C,B,A,C,A,C,D,A,B,A,C,A,B,A,C,C,A,D,A,B,C,A,B,B,B,201805066
page_006.png,A,C,B,C,C,A,B,C,B,D,C,A,A,D,A,A,D,C,C,D,C,B,C,C,C,C,A,D,C,A,D,A,B,D,B,201778206
```

Each row represents a student's scanned response, showing their selected options (Q1–Q35) and their extracted student ID.


---

7. **Annotated Image Examples**

After processing, annotated versions of each input sheet are saved to the `annotated/` folder. These highlight the selected answers and the bubble regions used during detection.

Here’s an example of a correctly processed sheet:

![Correctly Annotated](/annotated_example.png)

And here’s an example where extraction failed due to alignment or scanning issues:

![Failed Extraction](/outlier_example.png)

---

The next section will show you how to **identify and resolve failed extractions**, including tips on troubleshooting misaligned scans or incorrect calibrations.
