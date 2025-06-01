# 🧾 Scoring and Enrichment (`process_answers.py`)

This script performs automatic scoring of student multiple-choice responses and allows optional enrichment of the results using a Canvas-exported student gradebook. It also supports manual resolution of unknown or mismatched student IDs.

---

1. **Before You Begin**

You must first **export the gradebook from Canvas** for the module in question:

- Go to the Canvas module.
- Navigate to **Grades** → **Actions** → **Export** → **CSV**.
- Save the exported file (e.g., `grades.csv`) in the **same folder** as your scanned answer data (where `all_detected_answers.csv` exists).

---

2. **What It Does**

- Reads `all_detected_answers.csv` and extracts the answer key + student responses.
- Scores each student’s answers.
- Optionally enriches results using student names and IDs from Canvas.
- Saves the output to `scored_answers.csv`.
- Allows manual verification and correction of unmatched or unknown student IDs.

---

3. **How to Use**

Run the script:

```bash
python process_answers.py
```

You will be prompted to:

- Enter the path to the folder containing `all_detected_answers.csv`.
- Enter the number of questions to score (e.g. 32).
- Choose whether to enrich with student names (type `y` or `n`).
- If enriching, enter the filename of the Canvas export (e.g. `grades.csv`).

---

4. **Output Files**

- `scored_answers.csv`: Contains all scores with student name and ID (if enrichment succeeds).
- Rows include: `filename`, `score`, `percentage_score`, `student_id`, and optionally `student_name`, `SIS User ID`, `ID`.

---

5. **Handling Unknown Students**

If any rows cannot be matched with a student from the Canvas export:

- The script displays the top portion of the student's scanned sheet.
- Attempts to auto-suggest a close match based on digit similarity.
- You can:
  - Accept the suggestion (`y`)
  - Manually enter student name and ID (`m`)

All edits are saved live to the CSV file.

---

6. **Example Output (Partial)**

```csv
filename,student_name,score,percentage_score,student_id,sis_user_id,ID
page_001.png,Alice Smith,30,93.8,201805066,201805066@student.liv.ac.uk,10566
page_002.png,Unknown,27,84.4,201809558,,
page_003.png,Charlie Jones,31,96.9,201804043,201804043@student.liv.ac.uk,10443
```

---

7. **Best Practices**

- Run this script **after** validating and completing `all_detected_answers.csv`.
- Ensure your Canvas export includes the correct columns: `Student`, `SIS User ID`, and `ID`.
- Only fill in unmatched rows once, then re-run if necessary to finish resolving.

---

After scoring is complete, you're ready to generate item-level analysis and summary reports.
