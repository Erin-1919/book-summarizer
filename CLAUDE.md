# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
# Activate virtualenv (Windows Git Bash)
source .venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Run dev server (http://localhost:5000)
python app.py
```

Requires a `.env` file with `OPENAI_API_KEY=sk-...`. Optionally `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` for Google Photos import. No test suite exists.

## Architecture

Single-file Flask app (`app.py`) with one Jinja template, static CSS/JS, and a JSON file for persistence.

### Processing Flow

Two-step upload process with a file reordering step in between:

1. **`POST /upload`** — saves files to `uploads/`, returns file IDs and names (or **Google Photos import** downloads photos to `uploads/` via `/google/picker/import`)
2. User reorders files via drag-and-drop in the browser
3. **`POST /process`** — processes files in confirmed order, saves results, cleans up uploaded files

Both manual upload and Google Photos import converge at the file order panel → `/process`.

**Images** (jpg, png, bmp, tiff, webp): sent as base64 to GPT-4o vision API via `extract_and_summarize_image()`. One API call per image returns both extracted text and summary, parsed by `---EXTRACTED TEXT---` / `---SUMMARY---` delimiters.

**PDFs**: text extracted locally via PyMuPDF (`extract_text_from_pdf()`), then summarized via `summarize_text()` as a separate GPT-4o call.

### Data Model

All data lives in `data/summaries.json` with this hierarchy:
```
books[] → chapters[] → subchapters[] → summaries[]
```
Each summary entry stores `extracted_text`, `summary`, and `timestamp`. Re-uploading to a subchapter replaces its summaries array (not appends).

### Frontend

- `templates/index.html` — Jinja2 template; passes server data to JS via inline `<script>` globals (`booksData`, `selectedBook`, etc.)
- `static/app.js` — all client logic: modals for creating books/chapters/subchapters, two-step upload with drag-and-drop reordering, Google Photos picker flow, summary display
- `static/style.css` — all styles

### API Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Main page (query params: `book`, `chapter`, `subchapter`) |
| `/upload` | POST | Save files temporarily, return IDs |
| `/process` | POST | Extract text + summarize in confirmed order |
| `/book` | POST | Create book |
| `/chapter` | POST | Create chapter |
| `/subchapter` | POST | Create subchapter |
| `/summary/<id>` | DELETE | Delete a summary |
| `/google/auth` | GET | Redirect to Google OAuth consent screen |
| `/google/callback` | GET | OAuth callback, stores tokens in session |
| `/google/status` | GET | Check if user is authenticated with Google |
| `/google/picker/create` | POST | Create a Photos Picker session, return `pickerUri` |
| `/google/picker/poll/<id>` | GET | Poll picker session; returns media items when ready |
| `/google/picker/import` | POST | Download selected photos to `uploads/`, return file list |
