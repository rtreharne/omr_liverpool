import csv
import os
import re
from PIL import Image
import matplotlib.pyplot as plt

current_figure = None

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
    error_log_csv = os.path.join(directory, 'error_log.csv')

    if not os.path.isfile(input_csv):
        print("There is no all_detected_answers.csv file in the directory")
        return

    try:
        num_questions = int(input("How many questions should be processed (e.g. 32)? "))
    except ValueError:
        print("Invalid number entered.")
        return

    # Step 1: Load any previously scored rows
    existing_scores = {}
    used_student_ids = set()
    output_headers = None
    if os.path.exists(output_csv):
        with open(output_csv, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            output_headers = next(reader)
            for row in reader:
                filename = row[0]
                existing_scores[filename] = row
                if len(row) >= 4:
                    used_student_ids.add(row[-1])  # student_id

    # Step 2: Load answer key and all responses
    rows = []
    answer_key = None
    with open(input_csv, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        for row in reader:
            if 'answers' in row[0].lower():
                answer_key = row[1:1 + num_questions]
            else:
                rows.append(row)

    if not answer_key:
        print("No answer key row found.")
        return

    # Step 3: Load student info for enrichment
    enrich = input("Would you like to enrich results with student names? (y/n): ").strip().lower()
    student_lookup = {}
    enrich_success = False

    if enrich == 'y':
        lookup_filename = input("Enter the filename of the student info CSV (e.g. grades.csv): ").strip()
        lookup_path = os.path.join(directory, lookup_filename)
        if os.path.isfile(lookup_path):
            with open(lookup_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    raw = row.get('SIS User ID', '').strip()
                    match = re.match(r'^(\d+)', raw)
                    if match:
                        student_id = match.group(1)
                        name = row.get('Student', '').strip()
                        student_lookup[student_id] = name
                enrich_success = True
        else:
            print(f"No file named {lookup_filename} found in the directory. Skipping enrichment.")

    if not output_headers:
        output_headers = ['filename', 'score', 'student_id']
        if enrich_success:
            output_headers.insert(1, 'student_name')

    error_rows = []
    unknown_rows = []

    with open(output_csv, 'a', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        if not existing_scores:
            writer.writerow(output_headers)

        for row in rows:
            filename = row[0]
            if filename in existing_scores:
                continue  # Skip previously processed

            student_answers = row[1:1 + num_questions]
            score = sum(sa == ak for sa, ak in zip(student_answers, answer_key))
            student_id = row[-1]
            student_name = student_lookup.get(student_id, 'Unknown')

            if student_name == 'Unknown':
                unknown_rows.append((filename, score, student_id))
            else:
                used_student_ids.add(student_id)
                output_row = [filename, student_name, score, student_id] if enrich_success else [filename, score, student_id]
                writer.writerow(output_row)
                outfile.flush()

        # Step 4: Handle unknowns
        total_unknown = len(unknown_rows)
        for i, (filename, score, student_id) in enumerate(unknown_rows, 1):
            print(f"\n[{i}/{total_unknown}] Manually identifying: {filename} (ID: {student_id})")

            image_path = os.path.join(directory, filename)
            if os.path.isfile(image_path):
                open_image(image_path)

            suggested_id, suggested_name = find_close_student_id(student_id, student_lookup, used_student_ids) if enrich_success else (None, None)

            if suggested_id:
                print(f"🧠 Suggested match: {suggested_name} (ID: {suggested_id})")
                choice = input("Accept match? (y = yes, m = manual entry): ").strip().lower()
                if choice == 'y':
                    used_student_ids.add(suggested_id)
                    if current_figure:
                        plt.close(current_figure)
                    output_row = [filename, suggested_name, score, suggested_id] if enrich_success else [filename, score, suggested_id]
                    writer.writerow(output_row)
                    outfile.flush()
                    continue

            # Manual fallback
            new_name = input("Enter student name: ").strip()
            new_id = input("Enter student ID (digits only): ").strip()
            used_student_ids.add(new_id)
            if current_figure:
                plt.close(current_figure)
            output_row = [filename, new_name, score, new_id] if enrich_success else [filename, score, new_id]
            writer.writerow(output_row)
            outfile.flush()
            error_rows.append([filename, student_id])

    print(f"\n✅ Finished. Scored answers saved to {output_csv}")

    if error_rows:
        with open(error_log_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['filename', 'original_student_id'])
            writer.writerows(error_rows)
        print(f"⚠️  {len(error_rows)} unmatched original IDs logged to {error_log_csv}")

# Run
if __name__ == '__main__':
    score_answers()
