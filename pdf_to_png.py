import fitz  # PyMuPDF
import os

def split_pdf_to_images(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        output_path = os.path.join(output_folder, f"student_{page_num + 1:04}.png")
        pix.save(output_path)
        print(f"✅ Saved {output_path}")

    doc.close()
    print("✅ PDF split complete.")

if __name__ == "__main__":
    input_pdf = input("📄 Enter path to the input PDF file: ").strip()
    output_dir = input("📁 Enter name for the output directory: ").strip()

    if not os.path.isfile(input_pdf):
        print("❌ Error: PDF file not found.")
    else:
        split_pdf_to_images(input_pdf, output_dir)
