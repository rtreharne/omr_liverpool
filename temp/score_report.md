# 📊 Student Score Report (`score_report.py`)

This script generates a polished PDF report listing individual student scores based on the final processed and scored data. It is typically used at the end of the STAPLE workflow to produce a deliverable document for instructors or administrators.

---

1. **What It Does**

- Reads the final `scored_answers.csv` file.
- Extracts `student_id`, `student_name`, and `percentage_score`.
- Sorts students alphabetically.
- Prompts for user input (author, course, assessment).
- Outputs a professionally styled PDF report with logos and a footer.

---

2. **Before You Run**

Ensure you have:

- A complete and correct `scored_answers.csv` file in your working directory.
- The `logo.svg` file (University logo) and `staple.png` (STAPLE system logo) in the same directory.

If `logo.svg` is not already converted, the script will generate a PNG version (`logo_converted.png`) using `cairosvg`.

---

3. **How to Use**

```bash
python score_report.py
```

You will be prompted to enter:

- The path to `scored_answers.csv`
- Your name (to appear as the author of the report)
- The course name (e.g. BIOS101)
- The assessment name (e.g. Midterm MCQ)

The script will generate a PDF report saved to:

```
scored_answers_report.pdf
```

---

4. **Example Output**

The PDF report includes:

- **Title Page** with logos, author, and assessment info
- **Table of student scores**, sorted by name
- **Footer** with STAPLE system contact info and logo

Each page includes the footer and page number automatically.

---

5. **Output Preview (table structure)**

| student_id | student_name    | percentage_score |
|------------|------------------|------------------|
| 201804043  | Charlie Jones    | 96.9             |
| 201805066  | Alice Smith      | 93.8             |
| 201809558  | Unknown          | 84.4             |

---

This report is suitable for internal moderation, distribution to course teams, or formal record-keeping.
