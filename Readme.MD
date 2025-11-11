# PDF Facts Analyzer

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Backend-black?logo=flask)](https://flask.palletsprojects.com/)
[![Next.js](https://img.shields.io/badge/Next.js-Frontend-black?logo=next.js)](https://nextjs.org/)

A full-stack application that extracts requested facts from PDF documents.

Upload any text-based PDF and type your own pointers like  
"List all dates", "Who signed?", "Total contract value?",  
"List all emails", "Find phone numbers".  

The backend analyzes the PDF and returns results with page numbers, snippets, and rationales.

---

## Tech Stack

| Layer | Technology |
|-------|-------------|
| Backend | Python 3 + Flask, PyPDF2, Regex, Flask-CORS |
| Frontend | Next.js (React 18) with plain CSS |
| Storage | Local /uploads directory (auto-created) |
| Deployment | Works locally or on Docker/Render/Heroku |

---

## Features

- Upload any PDF (single file)
- Enter free-form textual pointers
- Detects automatically:
  - Dates — e.g. June 1, 2025, 02.07.2025
  - Signatures — e.g. Signed by John Doe, Signature valid
  - Currency — e.g. ₹, $, USD, Rs.
  - Emails — e.g. help@domain.com
  - Phone numbers — e.g. +91 98765 43210
- Unique timestamped file names (no overwriting)
- Auto-cleanup of uploads older than 24 hours
- CORS-enabled for frontend API calls

---

## Project Structure

```
pdf-facts-analyzer/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── uploads/           # auto-created; temporary PDFs
├── frontend/
│   ├── pages/
│   │   └── index.js
│   ├── styles/
│   │   └── globals.css
│   ├── package.json
│   └── next.config.js
├── samples/
│   ├── sample.pdf
│   └── pointers.json
└── README.md
```

---

## Setup & Run (Backend)

```bash
cd backend
python -m venv venv
# Activate venv:
#   Windows: venv\Scripts\activate
#   macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Server runs at http://localhost:5000

Test API manually:

```bash
curl -X POST ^
 -F "file=@samples/sample.pdf" ^
 -F "pointers=[\"List all dates\",\"Who signed?\",\"Total contract value?\"]" ^
 http://localhost:5000/api/extract
```

---

## Setup & Run (Frontend)

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:3000

Upload a PDF, enter pointers, and click Submit to view extracted results.

---

## Environment / CORS

CORS is already open in app.py via:

```python
from flask_cors import CORS
CORS(app)
```

Restrict origins in production if needed:

```python
CORS(app, resources={r"/*": {"origins": "https://yourdomain.com"}})
```

---

## Auto-Cleanup Logic

- On every upload, the backend scans /uploads
- Deletes any file older than MAX_FILE_AGE_HOURS = 24
- Keeps local storage lightweight automatically

---

## Architecture Summary

1. Frontend (Next.js) sends FormData → PDF + pointers  
2. Backend (Flask) saves PDF → extracts text with PyPDF2  
3. Applies regex heuristics for each pointer  
4. Returns structured JSON  
5. Frontend renders formatted results grouped by query

---

## Example Response

```json
{
  "pointers": [
    {
      "query": "List all dates",
      "matches": [
        {
          "snippet": "June 1, 2025",
          "page": 1,
          "rationale": "Matched flexible date pattern"
        }
      ]
    },
    {
      "query": "Who signed?",
      "matches": [
        {
          "snippet": "signed by John Doe",
          "page": 1,
          "rationale": "Found signature phrase"
        }
      ]
    },
    {
      "query": "Total contract value?",
      "matches": [
        {
          "snippet": "$12,000",
          "page": 1,
          "rationale": "Matched currency pattern"
        }
      ]
    }
  ]
}
```

---

## License & Attribution
MIT License — for educational and portfolio use.  
Sample PDFs belong to their respective owners.

---

Star this repository if you find it useful for learning or portfolio inspiration.