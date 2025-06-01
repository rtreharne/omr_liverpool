# 🔍 Validating Image Sizes (`validation.py`)

This script is designed to help you **identify scanning issues** by analyzing the dimensions of all PNG images in a folder. Outliers in image area often indicate incorrectly scanned or corrupted files that could disrupt OMR processing.

---

1. **What It Does**

- Loads all `.png` files in a folder.
- Calculates the image **area**, **width**, and **height** for each file.
- Flags **outliers** based on Z-score deviation from the mean area.
- Saves a log file listing all identified outliers.
- Visualizes the results using a scatterplot with ±2σ threshold lines.

---

2. **How to Use**

Run the script:

```bash
python validation.py
```

You will be prompted to:

- Enter the path to the folder containing `.png` images (e.g., `BIOS101/images`).

The script will:

- Analyze image sizes.
- Print warnings for any problematic images.
- Save a log file like `image_outliers_20250601_141200.log`.

---

3. **Example Output**

```log
Outlier: page_004.png - 2380x3200 (Area: 7616000)
Outlier: page_019.png - 1980x2800 (Area: 5544000)

Total outliers: 2 out of 35 images
```

---

4. **Visual Feedback**

A scatterplot is displayed showing:

- Each image's area
- The overall mean
- ±2 standard deviation lines
- Outliers in **red**

This helps you quickly spot inconsistencies in scan resolution or cropping.

---

5. **When to Use This Script**

- After converting PDF pages to PNGs
- Before or after running answer detection
- Whenever you're seeing unexplained failures or empty outputs from `detect_answers.py`

---

This script helps prevent data loss by ensuring only properly scanned sheets are passed through the pipeline.


---

6. **Dealing with Failed Extractions**

The STAPLE extraction system is highly effective, but not foolproof. In practice, approximately **2% of all scanned images fail** during the automated processing stage due to issues such as:

- Misalignment or partial scans
- Excessive noise or low contrast
- Incorrect bubble filling or marks outside detection zones

> For every 100 answer sheets, it is reasonable to expect **manual review and entry for around 2 sheets**.

### Manual Correction Procedure

1. Review the `annotated/` folder and check for missing or obviously incorrect annotations.
2. Cross-reference those files in `all_detected_answers.csv`.
3. Manually open the failed image, interpret the student’s selected answers, and edit the corresponding row in the CSV file.
4. Also update the `student_id` if it was incorrectly extracted or missing.

Once all rows in `all_detected_answers.csv` are complete and accurate, you may proceed to scoring and analysis.

> 💡 Use spreadsheet software like Excel, Numbers, or Google Sheets to simplify editing the CSV file.

# 🔍 Validating Image Sizes (`validation.py`)

This script is designed to help you **identify scanning issues** by analyzing the dimensions of all PNG images in a folder. Outliers in image area often indicate incorrectly scanned or corrupted files that could disrupt OMR processing.

---

1. **What It Does**

- Loads all `.png` files in a folder.
- Calculates the image **area**, **width**, and **height** for each file.
- Flags **outliers** based on Z-score deviation from the mean area.
- Saves a log file listing all identified outliers.
- Visualizes the results using a scatterplot with ±2σ threshold lines.

---

2. **How to Use**

Run the script:

```bash
python validation.py
```

You will be prompted to:

- Enter the path to the folder containing `.png` images (e.g., `BIOS101/images`).

The script will:

- Analyze image sizes.
- Print warnings for any problematic images.
- Save a log file like `image_outliers_20250601_141200.log`.

---

3. **Example Output**

```log
Outlier: page_004.png - 2380x3200 (Area: 7616000)
Outlier: page_019.png - 1980x2800 (Area: 5544000)

Total outliers: 2 out of 35 images
```

---

4. **Visual Feedback**

A scatterplot is displayed showing:

- Each image's area
- The overall mean
- ±2 standard deviation lines
- Outliers in **red**

This helps you quickly spot inconsistencies in scan resolution or cropping.

---

5. **When to Use This Script**

- After converting PDF pages to PNGs
- Before or after running answer detection
- Whenever you're seeing unexplained failures or empty outputs from `detect_answers.py`

---

This script helps prevent data loss by ensuring only properly scanned sheets are passed through the pipeline.


---

6. **Dealing with Failed Extractions**

The STAPLE extraction system is highly effective, but not foolproof. In practice, approximately **2% of all scanned images fail** during the automated processing stage due to issues such as:

- Misalignment or partial scans
- Excessive noise or low contrast
- Incorrect bubble filling or marks outside detection zones

> For every 100 answer sheets, it is reasonable to expect **manual review and entry for around 2 sheets**.

### Manual Correction Procedure

1. Review the `annotated/` folder and check for missing or obviously incorrect annotations.
2. Cross-reference those files in `all_detected_answers.csv`.
3. Manually open the failed image, interpret the student’s selected answers, and edit the corresponding row in the CSV file.
4. Also update the `student_id` if it was incorrectly extracted or missing.

Once all rows in `all_detected_answers.csv` are complete and accurate, you may proceed to scoring and analysis.

> 💡 Use spreadsheet software like Excel, Numbers, or Google Sheets to simplify editing the CSV file.

