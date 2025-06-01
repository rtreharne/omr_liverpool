# 🛠️ PDF Processing (`process_pdf.py`)

This script prepares scanned assessment files for analysis by merging multiple PDFs into one and converting that merged file into high-resolution PNG images.

---

1. **What it Does**

   The script performs two key steps:

   - **Merge PDFs**: Combines all `.pdf` files in a given folder into a single PDF called `single.pdf`.
   - **Convert to PNGs**: Converts each page of the merged PDF into a `.png` image at 300 DPI resolution.

---

2. **How to Use**

   Run the script from your terminal:

   ```bash
   python process_pdf.py
   ```

   You will be prompted to:

   - Enter the path to the folder containing your `.pdf` scan files.
   - Enter the path to the folder where the output PNG images should be saved.

---

3. **Example Workflow**

   Suppose you have a folder called `BIOS101` that contains several scanned PDF files. Run:

   ```bash
   python process_pdf.py
   ```

   - For the input folder, enter: `BIOS101`
   - For the output image folder, enter: `BIOS101/images`

   The script will:
   - Create a file: `BIOS101/single.pdf`
   - Generate PNGs like `page_001.png`, `page_002.png`, … inside `BIOS101/images/`

---

4. **Technical Notes**

   - Uses the `PyMuPDF` (`fitz`) library for both PDF merging and rasterizing pages.
   - Zoom is calculated to ensure output images are 300 DPI.
   - Output filenames are zero-padded (`page_001.png`, `page_002.png`, etc.) for easy sorting.
   - Only `.pdf` files in the top-level of the input folder are processed.

---

You must complete this step before proceeding to answer extraction.
