import extract_answers_with_pytesseract as exte
import parse_ocr_answers as pocr
import os
import pandas as pd

def save_answers_to_csv(results_dict, output_path="consolidated_answers.csv"):
    data = []

    for filename, answers in results_dict.items():
        for q_num, (answer, confidence) in enumerate(answers, start=1):
            data.append({
                "filename": filename,
                "question_number": q_num,
                "answer": answer,
                "confidence": confidence
            })

    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"✅ Saved to {output_path}")

def main(folder_path):

    results_dict = {}
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".png"):
            
            
            file_path = os.path.join(folder_path, filename)
            print("Processing PNG:", file_path)

            ocr_text = exte.main(file_path)

            answers = pocr.main(ocr_text)


            results_dict[filename] = answers

            save_answers_to_csv(results_dict)

if __name__ == "__main__":
    main("png")


            

