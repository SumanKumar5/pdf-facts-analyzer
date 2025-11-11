from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from flask_cors import CORS
import os, re, json, time, uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ---- Directory and cleanup settings ----
UPLOAD_DIR = "uploads"
MAX_FILE_AGE_HOURS = 24  # auto-delete files older than this

# Ensure upload folder exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


def cleanup_old_uploads():
    """Remove uploaded files older than MAX_FILE_AGE_HOURS"""
    now = time.time()
    if not os.path.exists(UPLOAD_DIR):
        return
    for filename in os.listdir(UPLOAD_DIR):
        path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.isfile(path):
            continue
        age_hours = (now - os.path.getmtime(path)) / 3600
        if age_hours > MAX_FILE_AGE_HOURS:
            try:
                os.remove(path)
                print(f"[CLEANUP] Deleted old file: {filename}")
            except Exception as e:
                print(f"[CLEANUP] Failed to delete {filename}: {e}")


# ---- Regex patterns ----
DATE_RE = re.compile(
    r"\b(?:\d{1,2}[./-]\d{1,2}[./-]\d{2,4}"
    r"|\d{4}[./-]\d{1,2}[./-]\d{1,2}"
    r"|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|July|Jul|Aug|Sept|Sep|October|Oct|Nov|December|Dec)\w*\s+\d{4}"
    r"|\b(?:Jan|Feb|Mar|Apr|May|June|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\w*\s+\d{1,2},?\s+\d{4})\b",
    re.I,
)
CURRENCY_RE = re.compile(r"(?:₹|Rs\.?|USD|\$)\s?[0-9,]+(?:\.\d+)?", re.I)
SIGN_RE = re.compile(r"(signed\s+by\s+[A-Z][a-z]+(?:\s[A-Z][a-z]+)*)|(Signature|Signed)", re.I)
EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+", re.I)
PHONE_RE = re.compile(r"\+?\d[\d\s\-]{7,}\d")


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/api/extract", methods=["POST"])
def extract():
    # Auto-clean old files before handling a new upload
    cleanup_old_uploads()

    if "file" not in request.files:
        return jsonify({"error": "no file part"}), 400

    pdf_file = request.files["file"]
    if pdf_file.filename == "":
        return jsonify({"error": "no selected file"}), 400

    # ---- Unique filename generation ----
    original_name = secure_filename(pdf_file.filename)
    name, ext = os.path.splitext(original_name)
    unique_name = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}{ext}"
    save_path = os.path.join(UPLOAD_DIR, unique_name)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    pdf_file.save(save_path)

    # ---- Parse pointers ----
    raw_pointers = request.form.get("pointers")
    if not raw_pointers:
        return jsonify({"error": "missing pointers"}), 400
    try:
        pointers = json.loads(raw_pointers)
    except Exception:
        return jsonify({"error": "invalid JSON for pointers"}), 400

    reader = PdfReader(save_path)
    pages = [{"page": i, "text": page.extract_text() or ""} for i, page in enumerate(reader.pages, start=1)]

    results = []
    for pointer in pointers:
        q = pointer.lower()
        matches = []
        for p in pages:
            text = p["text"]

            # ---- Date detection ----
            if "date" in q or "day" in q:
                for m in DATE_RE.finditer(text):
                    matches.append({
                        "snippet": m.group(),
                        "page": p["page"],
                        "rationale": "Matched flexible date pattern"
                    })

            # ---- Signature detection ----
            elif "sign" in q:
                for m in SIGN_RE.finditer(text):
                    snippet = m.group().strip()
                    matches.append({
                        "snippet": snippet,
                        "page": p["page"],
                        "rationale": "Found signature phrase"
                    })

            # ---- Currency / contract value ----
            elif any(x in q for x in ["total", "value", "amount", "price", "cost"]):
                for m in CURRENCY_RE.finditer(text):
                    matches.append({
                        "snippet": m.group(),
                        "page": p["page"],
                        "rationale": "Matched currency pattern"
                    })

            # ---- Email addresses ----
            elif "email" in q:
                for m in EMAIL_RE.finditer(text):
                    matches.append({
                        "snippet": m.group(),
                        "page": p["page"],
                        "rationale": "Found email address"
                    })

            # ---- Phone numbers ----
            elif "phone" in q or "mobile" in q or "contact" in q:
                for m in PHONE_RE.finditer(text):
                    matches.append({
                        "snippet": m.group(),
                        "page": p["page"],
                        "rationale": "Found phone number"
                    })

        results.append({"query": pointer, "matches": matches})
    return jsonify({"pointers": results}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
