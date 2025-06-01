import csv
import os
import re
from PIL import Image
import matplotlib.pyplot as plt

current_figure = None  # Global reference to the active image figure

def open_image(filepath):
    """Open only the top 25% of the image using matplotlib."""
    global current_figure
    try:
        img = Image.open(filepath)
        width, height = img.size
        top_crop = img.crop((0, 0, width, int(0.25 * height)))
        current_figure = plt.figure()
        plt.imshow(top_crop)
        plt.axis('off')
        plt.title(os.path.basename(filepath))
        plt.show(block=False)
    except Exception as e:
        print(f"⚠️ Could not open image {filepath}: {e}")

def count_digit_differences(a: str, b: str) -> int:
    return sum(x != y for x, y in zip(a.zfill(len(b)), b.zfill(len(a)))) if len(a) == len(b) else 99

def find_close_student_id(student_id, student_lookup, used_ids):
    for known_id, name in student_lookup.items():
        if known_id in used_ids:
            continue
        if len(student_id) == len(known_id):
            diff = count_digit_differences(student_id, known_id)
            if diff <= 2:
                return known_id, name
    return None, None

def score_answers():
    directory = input("Enter the path to the directory containing all_detected_answers.csv: ").strip()
    input_csv = os.path.join(directory, 'all_detected_answers.csv')
    output_csv = os.path.join(directory, 'scored_answers.csv')

    if not os.path.isfile(input_csv):
        print("❌ No all_detected_answers.csv found.")
        return

    try:
        num_questions = int(input("How many questions should be processed (e.g. 32)? "))
    except ValueError:
        print("❌ Invalid number entered.")
        return

    enrich = input("Would you like to enrich results with student names? (y/n): ").strip().lower()
    student_lookup = {}
    full_ids = {}
    simple_ids = {}
    enrich_success = False

    if enrich == 'y':
        lookup_filename = input("Enter the filename of the student info CSV (e.g. grades.csv): ").strip()
        lookup_path = os.path.join(directory, lookup_filename)
        if os.path.isfile(lookup_path):
            with open(lookup_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sis_user_id_raw = row.get('SIS User ID', '').strip()
                    match = re.match(r'^(\d+)', sis_user_id_raw)
                    if match:
                        student_id = match.group(1)
                        student_lookup[student_id] = row.get('Student', '').strip()
                        full_ids[student_id] = sis_user_id_raw
                        simple_ids[student_id] = row.get('ID', '').strip()
                enrich_success = True
        else:
            print(f"⚠️ No file named {lookup_filename} found. Skipping enrichment.")

    if not os.path.isfile(output_csv):
        rows = []
        answer_key = None
        with open(input_csv, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)
            for row in reader:
                if 'answers' in row[0].lower():
                    answer_key = row[1:1 + num_questions]
                else:
                    rows.append(row)

        if not answer_key:
            print("❌ No answer key row found.")
            return

        output_headers = ['filename', 'score', 'percentage_score', 'student_id']
        if enrich_success:
            output_headers.insert(1, 'student_name')
            output_headers.extend(['sis_user_id', 'ID'])

        scored_data = []
        used_ids = set()
        for row in rows:
            filename = row[0]
            student_answers = row[1:1 + num_questions]
            score = sum(sa == ak for sa, ak in zip(student_answers, answer_key))
            percentage = round(100 * score / num_questions, 1)
            raw_id = row[-1]

            out_row = {
                'filename': filename,
                'score': score,
                'percentage_score': percentage,
                'student_id': raw_id,
                'student_name': 'Unknown',
                'sis_user_id': '',
                'ID': ''
            }

            if enrich_success and raw_id in student_lookup:
                out_row['student_name'] = student_lookup[raw_id]
                out_row['sis_user_id'] = full_ids.get(raw_id, '')
                out_row['ID'] = simple_ids.get(raw_id, '')
                used_ids.add(raw_id)

            scored_data.append(out_row)

        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=output_headers)
            writer.writeheader()
            writer.writerows(scored_data)

    # Continue from existing scored_answers.csv to resolve unknowns
    with open(output_csv, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
        headers = rows[0].keys()

    used_ids = set(r['student_id'] for r in rows if r['student_name'] != 'Unknown')

    for i, row in enumerate(rows):
        if row['student_name'] != 'Unknown':
            continue

        print(f"\n[{i+1}/{len(rows)}] Resolving: {row['filename']} (ID: {row['student_id']})")
        image_path = os.path.join(directory, row['filename'])
        if os.path.isfile(image_path):
            open_image(image_path)

        suggested_id, suggested_name = find_close_student_id(row['student_id'], student_lookup, used_ids) if enrich_success else (None, None)

        if suggested_id:
            print(f"🧠 Suggested: {suggested_name} (ID: {suggested_id})")
            choice = input("Accept match? (y = yes, m = manual entry): ").strip().lower()
            if choice == 'y':
                row['student_name'] = suggested_name
                row['student_id'] = suggested_id
                row['sis_user_id'] = full_ids.get(suggested_id, '')
                row['ID'] = simple_ids.get(suggested_id, '')
                used_ids.add(suggested_id)
                if current_figure:
                    plt.close(current_figure)
                _update_csv_row(output_csv, row)
                continue

        row['student_name'] = input("Enter student name: ").strip()
        row['student_id'] = input("Enter student ID (digits only): ").strip()
        used_ids.add(row['student_id'])
        row['sis_user_id'] = full_ids.get(row['student_id'], '')
        row['ID'] = simple_ids.get(row['student_id'], '')
        if current_figure:
            plt.close(current_figure)
        _update_csv_row(output_csv, row)

    print(f"\n✅ Completed. File updated: {output_csv}")

def _update_csv_row(csv_path, updated_row):
    with open(csv_path, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
        headers = rows[0].keys() if rows else updated_row.keys()

    for row in rows:
        if row['filename'] == updated_row['filename']:
            row.update(updated_row)
            break

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == '__main__':
    score_answers()
