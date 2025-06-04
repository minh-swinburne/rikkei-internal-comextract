# Company Information Extraction

## 🧾 Project Title: Company Info Extractor from Protected PDFs using LLMs

### 🧠 Purpose:

Extract structured company information (name, PIC, position, emails) from a  **multi-page, copy-protected PDF** , where each page contains 15+ entries in semi-structured text.

The extracted data will be written to an Excel file. The solution supports either:

* Cloud-based LLMs (e.g. OpenAI GPT-4 API)
* Local models (optional, using Haystack + `nuextract`)

---

## 📁 Project Structure Requirements

This should be built as a modular, extensible **Python CLI application** with a clear folder structure, and later convertible to a web backend (e.g., FastAPI). Suggested layout:

```
app/
│
├── main.py                   # Entry point: command-line interface
├── settings.py               # Settings loader (e.g., API keys, model paths)
├── extractors/
│   ├── base.py               # BaseExtractor interface
│   ├── api_extractor.py      # Extractor using OpenAI API
│   └── local_extractor.py    # (Optional) Extractor using local model + Haystack
│
├── readers/
│   └── pdf_reader.py         # PDF loader using PyMuPDF with password support
│
├── writers/
│   └── excel_writer.py       # Writes extracted data to Excel
│
├── utils/
│   └── parser.py             # Helper to parse LLM output into structured dicts
│
└── requirements.txt          # Dependencies
```

---

## 🔐 PDF Support Notes

* Use **PyMuPDF (`fitz`)** to read the PDF and extract text page-by-page.
* If the PDF is password-protected (copy-locked), use:

  ```python
  doc.authenticate(password)
  ```

  This avoids the need for external tools like `qpdf`.

---

## 💬 CLI Interface Requirements

Build a **command-line interface** using `argparse` or `typer`. The CLI should support:

| Argument         | Description                                                                                                 |
| ---------------- | ----------------------------------------------------------------------------------------------------------- |
| `--input`      | Required. Path to the input PDF file.                                                                       |
| `--password`   | Optional, default to None. Password for locked PDF.                                                         |
| `--start-page` | Optional, default to 0 (from start of file). Page to start processing from (for testing)                    |
| `--end-page`   | Optional, default to -1 (to end of file). Page to end processing at (for testing)                           |
| `--method`     | Required. Extraction method:`"api"`or `"local"`                                                         |
| `--output`     | Optional. Output Excel file path (default:`output.xlsx`)                                                  |
| `--overwrite`  | Optional, boolean, default to false. Whether to overwrite the output file, or to append content to the end. |

Example:

```bash
python main.py --input sample.pdf --password secret --method api --output results.xlsx --start-page 1 --end-page 10
```

---

## 🤖 Extractor Logic (Phase 1: LLM API)

### Input:

* Raw text of a single PDF page (which may contain 10–20 company entries).

### Prompt Template:

Structure the prompt clearly for consistent JSON extraction, e.g.:

```plaintext
Extract company data from the following text. For each company, return:
- Company name
- PIC full name
- PIC job title
- Email(s), comma-separated

Return a list of JSON objects like:
[
  {
    "Company": "...",
    "PIC": "...",
    "Position": "...",
    "Email": "..."
  },
  ...
]

Text:
---
{page_text}
```

### Output:

* Parsed JSON-like string (parsed using `json.loads()` or regex with fallback).
* Return list of dicts that can be passed to `pandas`.

---

## 📊 Output Excel Format

Columns:

| Company         | PIC            | Position          | Email(s)                                                      |
| --------------- | -------------- | ----------------- | ------------------------------------------------------------- |
| ABC Co., Ltd.   | Mr. John Doe   | Managing Director | [john@abc.com](mailto:john@abc.com)                              |
| XYZ Recruitment | Ms. Jane Smith | HR Manager        | [jane@xyz.com](mailto:jane@xyz.com),[hr@xyz.com](mailto:hr@xyz.com) |

* One row per company.
* Output should be saved using `pandas.DataFrame.to_excel()`.

---

## 🧠 Phase 2 (Later): Add Local Model Option

To be implemented later using:

* `Haystack` framework
* `nuextract` or similar extraction model on Huggingface
* Optional: GPU acceleration
* Load model from local cache
* Accept same inputs/outputs as API-based extractor

---

## 🔜 Phase 3 (Later): Convert to Backend Server

Future goal:

* Convert the CLI tool into a REST API using  **FastAPI** .
* Accept file uploads and return downloadable Excel file.
* Optionally use a frontend (e.g. React or Streamlit).

---

## ✅ Summary of Features

| Feature                    | Status                              |
| -------------------------- | ----------------------------------- |
| Command-line interface     | ✅ Implement in Phase 1             |
| PDF password support       | ✅ Use PyMuPDF's `authenticate()` |
| LLM API extractor          | ✅ First implementation             |
| Excel writer               | ✅ pandas output                    |
| Local extractor            | 🔜 Optional next phase              |
| FastAPI backend            | 🔜 Later phase                      |
| Logging and error handling | 🔜 Add for robustness               |

---

## Run the App (CLI)

```bash
uv run python -m app.main --input "data\input\Japanese Companies in Thailand-Directory-unlocked.pdf" --start-page 200 --end-page 210 --method api --output "data\output\results.xlsx" --overwrite
```
