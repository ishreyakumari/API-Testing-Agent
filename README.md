# 🧭 API Document Mapper

**Automatically tests and maps file-upload API endpoints using AI (Google Gemini Vision).**

This tool scans a **Postman collection**, detects which APIs require file uploads, and tests them intelligently with real documents.  
It uses **Google Gemini AI** for document classification (OCR + understanding) and error interpretation to automatically learn which document types each API accepts.

---

## ✨ Features

✅ **Gemini-powered document classification** – Reads and understands PDFs or images using OCR.  
✅ **Auto-detect upload APIs** – Finds endpoints that expect file uploads in your Postman collection.  
✅ **Smart error understanding** – Uses LLM reasoning to extract what document type or format the API wants.  
✅ **Auto-retry with correct document** – Retests failed APIs with the right file type automatically.  
✅ **Comprehensive JSON report** – Summarizes which APIs succeeded, failed, or were skipped.  
✅ **Caching** – Saves document classifications and Gemini uploads to save time and cost.

---

## 🧠 How It Works

```

```
            ┌───────────────────────────────┐
            │   Local Documents Folder       │
            │  (PDFs, images, etc.)         │
            └──────────────┬────────────────┘
                           │
         ┌────────────────▼────────────────┐
         │  Gemini Vision (via SDK)        │
         │  → OCR + classify each doc      │
         └────────────────┬────────────────┘
                           │
             ┌─────────────▼──────────────┐
             │  Postman Collection        │
             │  → find upload endpoints   │
             └─────────────┬──────────────┘
                           │
    ┌──────────────────────▼───────────────────────────┐
    │ For each API:                                   │
    │  1️⃣ Pick random doc and test                   │
    │  2️⃣ If error, interpret it with Gemini         │
    │  3️⃣ Retry with correct doc type                │
    └──────────────────────┬───────────────────────────┘
                           │
                ┌──────────▼───────────┐
                │ Generate Report.json │
                │ → success, failure,  │
                │   and doc mappings   │
                └──────────────────────┘
```

```

---

## 🧩 Project Structure

```

📦 api-document-mapper/
├── main.py                         # Main script (CLI entry)
├── prompts/
│   ├── classify_document.md         # System prompt for doc classification
│   └── normalize_error.md           # System prompt for error interpretation
├── .env                             # Contains GOOGLE_API_KEY
├── sample_docs/                     # Folder with test documents
├── postman_collection.json          # Postman collection file
└── outputs/
├── document_classifications.json # Cached Gemini classification results
└── report.json                   # Final report of API tests

````

---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/api-document-mapper.git
cd api-document-mapper
````

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # (Mac/Linux)
venv\Scripts\activate      # (Windows)
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Google Gemini API key

Create a `.env` file in the project root and add:

```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

---

## 🧪 Usage

### Step 1: Prepare your documents

Place your test documents (PDFs, images, etc.) in a folder like `./sample_docs/`.

### Step 2: Provide a Postman collection

Export your collection and environment from Postman as JSON files.

### Step 3: Run the script

```bash
python main.py \
  --postman ./postman_collection.json \
  --env ./postman_env.json \
  --docs ./sample_docs \
  --out ./outputs \
  --random-file-per-api
```

---

## 🧾 Output Example

After running, a structured report appears in `outputs/report.json`.

```json
[
  {
    "api_name": "Upload KYC Document",
    "path": "https://api.example.com/upload",
    "accepted_documents": [
      { "fileName": "pan_card.pdf", "docType": "PAN card" }
    ],
    "rejected_documents": [
      { "nameOfFile": "passport.jpg", "docType": "passport", "errorMessage": "Invalid document type" }
    ],
    "skipped_documents": [
      { "fileName": "blurry_scan.png", "reason": "classification failed" }
    ]
  }
]
```

---

## 🧠 Gemini SDK (Under the Hood)

This project uses Google’s official Python SDK for the Gemini models.

```python
import google.generativeai as genai

genai.configure(api_key="YOUR_GOOGLE_API_KEY")
model = genai.GenerativeModel("gemini-2.5-pro")

# Upload a file
file_ref = genai.upload_file("pan_card.pdf")

# Ask Gemini to classify it
response = model.generate_content([file_ref, "Classify this document"])
print(response.text)
```

---

## 🛡️ Error Handling Strategy

| Tier    | Description                                                     | Function                        |
| ------- | --------------------------------------------------------------- | ------------------------------- |
| **1️⃣** | Use structured API errors if they already include required info | Direct JSON check               |
| **2️⃣** | Quick pattern match for common words (`pdf`, `aadhaar`, etc.)   | `cheap_error_to_struct()`       |
| **3️⃣** | Ask Gemini to interpret vague or unstructured errors            | `normalize_error_with_gemini()` |

---

## 🧠 Example Prompts

### `prompts/classify_document.md`

```markdown
You are a document classification model.
Analyze the attached file (image or PDF) and identify the document type.

Return only valid JSON:
{
  "document_type": "<type>",
  "confidence": <float between 0 and 1>
}
```

### `prompts/normalize_error.md`

```markdown
You are an API response analyzer.
Given an HTTP status, headers, and body, identify:
- required document type (if any)
- required file extension type (if any)

Return JSON in the shape:
{
  "required_extension_type": "<ext or null>",
  "required_document_type": "<type or null>",
  "description": "<plain explanation>"
}
```

---

## 🧩 Technologies Used

| Tool                  | Purpose                         |
| --------------------- | ------------------------------- |
| **Python 3.9+**       | Main programming language       |
| **Pydantic**          | Data validation and modeling    |
| **Requests**          | Making HTTP calls to test APIs  |
| **Google Gemini SDK** | AI classification and reasoning |
| **dotenv**            | Loading environment variables   |
| **Postman JSON**      | Source of API endpoints         |

---

## 📊 Example Report Summary

| API Name             | Accepted Docs      | Rejected Docs  | Notes                |
| -------------------- | ------------------ | -------------- | -------------------- |
| Upload PAN           | `pan_card.pdf`     | `passport.jpg` | Retry succeeded      |
| Upload Address Proof | `utility_bill.pdf` | —              | Success on first try |

---

## 🧰 Future Improvements

* ⚡ Parallelize API testing for speed
* 🔐 Add OAuth or Bearer token handling
* 📊 Build a simple web dashboard for report visualization
* 🧩 Improve document-type ontology (fuzzy matching, synonyms)

---

## 🤝 Contributing

Pull requests and suggestions are welcome!
To contribute:

1. Fork the repo
2. Create a new branch (`feature/your-feature`)
3. Commit and push your changes
4. Submit a Pull Request 🚀

---

> 💡 *“AI shouldn’t just test your APIs — it should understand them.”*
