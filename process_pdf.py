import os
import fitz  # PyMuPDF

def merge_pdfs_with_fitz(input_dir, output_pdf_path):
    pdf_files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")])
    if not pdf_files:
        raise FileNotFoundError("No PDF files found in the directory.")

    merged_doc = fitz.open()

    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_dir, pdf_file)
        with fitz.open(pdf_path) as src:
            print(f"📄 Adding {pdf_file} ({len(src)} pages)")
            merged_doc.insert_pdf(src)

    merged_doc.save(output_pdf_path)
    merged_doc.close()
    print(f"\n✅ Merged PDF saved to: {output_pdf_path}")

def convert_pdf_to_pngs(pdf_path, output_folder, dpi=300):
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)
    zoom = dpi / 72  # default resolution is 72 dpi
    mat = fitz.Matrix(zoom, zoom)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=mat)
        output_path = os.path.join(output_folder, f"page_{page_num+1:03}.png")
        pix.save(output_path)
        print(f"🖼️ Saved: {output_path}")

    print(f"\n✅ Converted {len(doc)} pages to PNG images.")
    doc.close()

def main():
    input_dir = input("Enter the path to the folder containing .pdf files: ").strip()
    if not os.path.isdir(input_dir):
        raise NotADirectoryError("Invalid input directory.")

    merged_pdf_path = os.path.join(input_dir, "single.pdf")
    merge_pdfs_with_fitz(input_dir, merged_pdf_path)

    output_img_dir = input("Enter the output folder for PNG images: ").strip()
    convert_pdf_to_pngs(merged_pdf_path, output_img_dir)

if __name__ == "__main__":
    main()
