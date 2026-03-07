# Book Page Summarizer

A reading companion app that extracts text from photos of book pages using OCR and generates AI-powered summaries. Summaries are organized by book, chapter, and sub-chapter, and persist locally across sessions.

Currently pre-loaded with the structure for **Prediction Machines** by Ajay Agrawal, Joshua Gans, and Avi Goldfarb. You can add more books through the UI.

## Features

- Upload one or multiple files at once — images (JPG, PNG, BMP, TIFF) or PDFs
- OCR text extraction via Tesseract (images), direct text extraction via PyMuPDF (PDFs)
- AI summarization via OpenAI GPT-4o (focuses on "Key Points" sections)
- Organize summaries by book > chapter/part > sub-chapter
- Re-uploading to a sub-chapter overwrites the previous summary
- All data persists in a local JSON file

## Prerequisites

1. **Python 3.10+**
2. **Tesseract OCR** — download and install from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki). If not added to PATH, update the path in `app.py`:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
   ```
3. **OpenAI API key**

## Setup

```bash
# Create and activate virtual environment
python -m venv .venv
# Windows CMD:
.venv\Scripts\activate
# Windows Git Bash / WSL / macOS / Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-your-key-here
```

## Run

```bash
python app.py
```

Open http://localhost:5000 in your browser.

## Usage

1. Select a book from the sidebar dropdown (or add a new one)
2. Expand a chapter and click a sub-chapter to view its summary
3. Select images or PDFs (or a mix), pick the chapter and sub-chapter, then click **Summarize**
4. The extracted text and AI summary will appear and be saved automatically
