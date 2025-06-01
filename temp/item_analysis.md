# item_analysis.py Documentation

The `item_analysis.py` script generates a detailed PDF report analyzing item-level statistics from a marked multiple-choice question (MCQ) assessment. It uses a reference row (e.g. `answers_____`) to identify correct answers, computes difficulty and discrimination for each question, and includes score summaries and visualizations.

---

## 🔧 Inputs Required

On running, the script prompts the user for:

1. Path to a `scored_answers.csv` file (containing one `answers_____` row with correct answers and student responses beneath).
2. Number of questions to analyze (e.g., 32).
3. Author name.
4. Course name.
5. Assessment name.

---

## 📊 Key Features

### ✅ Answer Key Extraction
The correct answers are taken from the first row where `filename` contains "answers" (case-insensitive). All other rows are treated as student responses.

### 🔍 Item-Level Stats
For each question:
- **Difficulty (p):** Proportion of students answering correctly.
- **Discrimination (r_pb):** Point biserial correlation between student correctness and overall performance.
- **Interpretation labels** are attached to both.

### 📈 Summary Statistics
Calculated across all student scores:
- Mean, Median, Min, Max (as %).

### 📉 Score Histogram
A histogram is generated showing distribution of student scores.

### 📄 PDF Report
The final PDF includes:
- Title page with University and STAPLE branding
- Summary stats
- Histogram of scores
- Item stats table
- Interpretation key for difficulty and discrimination

A footer appears on every page:
> For more information about the S.T.A.P.L.E. system please contact Dr. Robert Treharne (R.Treharne@liverpool.ac.uk)

---

## 🗃️ Outputs

- `item_analysis_output.csv`: Cleaned item statistics.
- A PDF file saved in the same folder, named like `item_analysis_output.pdf`.

---

## 📌 Notes

- This script expects numeric question column headers (`1`, `2`, ..., `32`) and a column `filename`.
- The correct answers row must contain expected answers in these columns.
- If discrimination cannot be calculated (e.g. no variance), "N/A" is shown.

---

## 📤 Example Output

```
=== ITEM ANALYSIS SUMMARY ===
Number of students: 98
Max score (%): 100.0
Mean score (%): 68.25
...

=== ITEM STATISTICS ===
Question  Difficulty (p)  Difficulty Label  Discrimination (r_pb) Discrimination Label
       1            0.85              Easy                  0.321         Very Good
       2            0.42          Moderate                  0.142              Weak
...
```

---

## 📎 Dependencies

- `pandas`
- `matplotlib`
- `scipy`
- `reportlab`
- `cairosvg`

Ensure `logo.svg` and `staple.png` are in the project root.

---

## 🧪 Sample Command

```bash
python item_analysis.py
# Enter path: /path/to/scored_answers.csv
# Number of questions: 32
# Name: Dr. Jane Doe
# Course: PHYS1001
# Assessment: Midterm A
```
