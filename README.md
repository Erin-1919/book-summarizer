# Book Page Summarizer

A reading companion app that extracts text from photos of book pages and generates AI-powered summaries. Images are sent directly to GPT-4o's vision capability, which reads and summarizes in one step. PDFs use PyMuPDF for text extraction. Summaries are organized by book, chapter, and sub-chapter, and persist locally across sessions.

Currently pre-loaded with the structure for **Prediction Machines** by Ajay Agrawal, Joshua Gans, and Avi Goldfarb. You can add more books through the UI.

## Features

- Upload one or multiple files at once — images (JPG, PNG, BMP, TIFF, WebP) or PDFs
- Import photos directly from Google Photos (via the Picker API)
- GPT-4o vision reads and summarizes book page images in one API call
- Direct text extraction via PyMuPDF for PDFs, then GPT-4o summarization
- Summaries focus on "Key Points" sections
- Organize summaries by book > chapter/part > sub-chapter
- Re-uploading to a sub-chapter overwrites the previous summary
- All data persists in a local JSON file

## Prerequisites

1. **Python 3.10+**
2. **OpenAI API key**

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

### Google Photos Import (optional)

To enable importing photos from Google Photos:

1. Go to [Google Cloud Console](https://console.cloud.google.com) and create a project
2. Enable the **Photos Picker API**
3. Go to **APIs & Services → OAuth consent screen**, set to External, add scope `photospicker.mediaitems.readonly`, and add your email as a test user
4. Go to **APIs & Services → Credentials**, create an **OAuth 2.0 Client ID** (Web application) with redirect URI `http://localhost:5000/google/callback`
5. Add the credentials to your `.env`:

```
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

## Run

```bash
python app.py
```

Open http://localhost:5000 in your browser.

## Usage

1. Select a book from the sidebar dropdown (or add a new one)
2. Expand a chapter and click a sub-chapter to view its summary
3. Select images or PDFs (or a mix), pick the chapter and sub-chapter, then click **Upload**
4. Or click **Import from Google Photos** to select photos from your Google Photos library
5. Reorder files if needed via drag-and-drop, then click **Confirm & Summarize**
6. The extracted text and AI summary will appear and be saved automatically
