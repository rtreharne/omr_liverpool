# ⚙️ Installation

Follow these steps to install and run the S.T.A.P.L.E. system on your machine.

---

1. Clone the Repository

   ```bash
   git clone https://github.com/your-username/staple.git
   cd staple
   ```

   > Replace `your-username` with your actual GitHub username.

2. Create a Virtual Environment

   - On **Linux/macOS**:

     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

   - On **Windows**:

     ```cmd
     python -m venv venv
     venv\Scripts\activate
     ```

   > 💡 **Tip for Windows users**: Install [Git for Windows](https://git-scm.com/download/win) to get **Git Bash**, a terminal that supports Unix-style commands like `ls`, `source`, and `cd`. After installing, right-click in your project folder and select **“Git Bash Here”**.

3. Install Python Dependencies

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Install System Dependencies

   Some libraries require system-level dependencies. Install them as follows:

   - On **Ubuntu/Debian**:

     ```bash
     sudo apt update
     sudo apt install -y \
       build-essential \
       poppler-utils \
       tesseract-ocr \
       libglib2.0-0 \
       libsm6 \
       libxext6 \
       libxrender1 \
       libmagic1 \
       libpango1.0-0 \
       libcairo2 \
       libopencv-dev
     ```

   - On **macOS** (using Homebrew):

     ```bash
     brew install poppler tesseract cairo pango opencv
     ```

   - On **Windows**:

     1. **Tesseract OCR**  
        - Download from: [https://github.com/tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract)  
        - Ensure the install path (e.g. `C:\Program Files\Tesseract-OCR`) is added to your system `PATH`.

     2. **Poppler**  
        - Download from: [http://blog.alivate.com.au/poppler-windows/](http://blog.alivate.com.au/poppler-windows/)  
        - Extract the ZIP file and add the `bin/` directory to your system `PATH`.

     3. **GTK / Cairo / Pango (optional)**  
        - Usually bundled via Python packages (`cairocffi`, `reportlab`)  
        - If needed, install [GTK+ for Windows](https://www.gtk.org/download/windows.php) and add its `bin/` folder to your system `PATH`.

5. Verify the Setup

   Run this test command:

   ```bash
   python -c "import cv2; import easyocr; import pytesseract; print('All good!')"
   ```

   If no errors appear, the environment is ready.

---

Need help? Contact **Dr. R. E. Treharne** at **R.Treharne@liverpool.ac.uk**
