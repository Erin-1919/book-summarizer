import os
import json
import uuid
from datetime import datetime

from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
from openai import OpenAI

load_dotenv()

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")
app.config["DATA_FILE"] = os.path.join(os.path.dirname(__file__), "data", "summaries.json")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "tiff", "pdf"}

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Uncomment and set if Tesseract is not on PATH:
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def load_data():
    path = app.config["DATA_FILE"]
    if not os.path.exists(path):
        return {"books": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    path = app.config["DATA_FILE"]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def find_book(data, book_id):
    return next((b for b in data["books"] if b["id"] == book_id), None)


def extract_text_from_image(image_path):
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        text = pytesseract.image_to_string(img)
    return text.strip()


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    texts = []
    for page in doc:
        text = page.get_text()
        if text.strip():
            texts.append(text.strip())
    doc.close()
    return "\n\n".join(texts)


def extract_text(filepath):
    ext = filepath.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        return extract_text_from_pdf(filepath)
    return extract_text_from_image(filepath)


def summarize_text(text):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful reading assistant. The user will provide OCR text from a book page photo. "
                    "Focus only on the 'Key Points' section — these are bullet points at the top of the page. "
                    "Write exactly one paragraph per bullet point. The number of paragraphs must match the number of bullet points. "
                    "State the ideas and opinions directly as facts. "
                    "Do NOT use phrases like 'the text suggests', 'the author argues', 'the excerpt discusses', etc. "
                    "Just state the points."
                ),
            },
            {"role": "user", "content": text},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


@app.route("/")
def index():
    data = load_data()
    selected_book = request.args.get("book")
    selected_chapter = request.args.get("chapter")
    selected_subchapter = request.args.get("subchapter")

    # Default to first book if none selected
    if not selected_book and data["books"]:
        selected_book = data["books"][0]["id"]

    book = find_book(data, selected_book) if selected_book else None

    return render_template(
        "index.html",
        data=data,
        book=book,
        selected_book=selected_book,
        selected_chapter=selected_chapter,
        selected_subchapter=selected_subchapter,
    )


@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("file")
    if not files or all(f.filename == "" for f in files):
        return jsonify({"error": "No file uploaded"}), 400
    for f in files:
        if not allowed_file(f.filename):
            return jsonify({"error": f"Invalid file type: {f.filename}. Use JPG, PNG, BMP, or TIFF."}), 400

    book_id = request.form.get("book_id")
    chapter_id = request.form.get("chapter_id")
    subchapter_id = request.form.get("subchapter_id")
    if not book_id or not chapter_id or not subchapter_id:
        return jsonify({"error": "Please select a book, chapter, and sub-chapter."}), 400

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    saved_paths = []
    for f in files:
        filename = secure_filename(f"{uuid.uuid4().hex}_{f.filename}")
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        f.save(filepath)
        saved_paths.append(filepath)

    try:
        all_texts = []
        for filepath in saved_paths:
            text = extract_text(filepath)
            if text:
                all_texts.append(text)
        if not all_texts:
            return jsonify({"error": "Could not extract any text from the images."}), 400
        extracted_text = "\n\n".join(all_texts)
        summary = summarize_text(extracted_text)
    finally:
        for filepath in saved_paths:
            if os.path.exists(filepath):
                os.remove(filepath)

    data = load_data()
    book = find_book(data, book_id)
    if not book:
        return jsonify({"error": "Book not found."}), 404
    chapter = next((c for c in book["chapters"] if c["id"] == chapter_id), None)
    if not chapter:
        return jsonify({"error": "Chapter not found."}), 404
    subchapter = next((s for s in chapter["subchapters"] if s["id"] == subchapter_id), None)
    if not subchapter:
        return jsonify({"error": "Sub-chapter not found."}), 404

    entry = {
        "id": uuid.uuid4().hex[:8],
        "extracted_text": extracted_text,
        "summary": summary,
        "timestamp": datetime.now().isoformat(),
    }
    subchapter["summaries"] = [entry]
    save_data(data)

    return jsonify({"success": True, "entry": entry})


@app.route("/book", methods=["POST"])
def create_book():
    title = request.json.get("title", "").strip()
    authors = request.json.get("authors", "").strip()
    if not title:
        return jsonify({"error": "Book title is required."}), 400
    data = load_data()
    book = {
        "id": uuid.uuid4().hex[:8],
        "title": title,
        "authors": authors,
        "chapters": [],
    }
    data["books"].append(book)
    save_data(data)
    return jsonify({"success": True, "book": book})


@app.route("/chapter", methods=["POST"])
def create_chapter():
    book_id = request.json.get("book_id", "").strip()
    name = request.json.get("name", "").strip()
    if not book_id or not name:
        return jsonify({"error": "Book ID and chapter name are required."}), 400
    data = load_data()
    book = find_book(data, book_id)
    if not book:
        return jsonify({"error": "Book not found."}), 404
    chapter = {
        "id": uuid.uuid4().hex[:8],
        "name": name,
        "subchapters": [],
    }
    book["chapters"].append(chapter)
    save_data(data)
    return jsonify({"success": True, "chapter": chapter})


@app.route("/subchapter", methods=["POST"])
def create_subchapter():
    book_id = request.json.get("book_id", "").strip()
    chapter_id = request.json.get("chapter_id", "").strip()
    name = request.json.get("name", "").strip()
    if not book_id or not chapter_id or not name:
        return jsonify({"error": "Book ID, chapter ID, and sub-chapter name are required."}), 400
    data = load_data()
    book = find_book(data, book_id)
    if not book:
        return jsonify({"error": "Book not found."}), 404
    chapter = next((c for c in book["chapters"] if c["id"] == chapter_id), None)
    if not chapter:
        return jsonify({"error": "Chapter not found."}), 404
    subchapter = {
        "id": uuid.uuid4().hex[:8],
        "name": name,
        "summaries": [],
    }
    chapter["subchapters"].append(subchapter)
    save_data(data)
    return jsonify({"success": True, "subchapter": subchapter})


@app.route("/summary/<summary_id>", methods=["DELETE"])
def delete_summary(summary_id):
    data = load_data()
    for book in data["books"]:
        for chapter in book["chapters"]:
            for subchapter in chapter["subchapters"]:
                for i, s in enumerate(subchapter["summaries"]):
                    if s["id"] == summary_id:
                        subchapter["summaries"].pop(i)
                        save_data(data)
                        return jsonify({"success": True})
    return jsonify({"error": "Summary not found."}), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)
