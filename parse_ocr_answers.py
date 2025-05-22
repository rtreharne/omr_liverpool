import re

def parse_ocr_text_file(filepath, max_question=34):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    answers = {}

    question_pattern = re.compile(r"(\d{1,3})[.,\s]")

    for line in lines:
        parts = re.split(question_pattern, line)

        for i in range(1, len(parts) - 1, 2):
            try:
                q_num = int(parts[i])
                if q_num > max_question:
                    continue

                segment = parts[i + 1].strip().upper()

                tokens = re.findall(r"[A-Z@<>=\[\]\\\/|*]+", segment)

                detected = {opt: False for opt in "ABCDE"}

                for token in tokens:
                    token = token.strip()
                    for opt in "ABCDE":
                        # Only mark as present if the token is not just the clean letter
                        if opt in token and token != opt:
                            detected[opt] = True

                # Selected = missing one
                missing = [l for l, present in detected.items() if not present]

                if len(missing) == 1:
                    answers[q_num] = missing[0]
                else:
                    answers[q_num] = None

            except ValueError:
                continue

    return answers


if __name__ == "__main__":
    answers = parse_ocr_text_file("ocr_text.txt")

    print("\nParsed Answers:")
    for q in range(1, 35):
        print(f"Q{q}: {answers.get(q)}")
