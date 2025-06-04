# Company Information Extraction

## 🧾 Project Title: Company Info Extractor from Protected PDFs using LLMs

### 🧠 Purpose

Extract structured company information (company name, PIC, position, emails) from multi-page, copy-protected PDF directories. Each page may contain 15+ semi-structured company entries. The extracted data is saved to an Excel file for further use.

---

## 🚀 Features

- **Reads copy-protected PDFs** (supports password-protected files)
- **Extracts company info** using LLMs (OpenRouter API, OpenAI SDK)
- **Writes results to Excel** (with append/overwrite support)
- **CLI interface** with progress bar
- **Modular, extensible codebase**

---

## 🏗️ How It Works

1. **PDF Reading:** Loads and unlocks (if needed) the PDF, extracting text page-by-page.
2. **Extraction:** Sends each page's text to an LLM (via OpenRouter) to extract structured company info.
3. **Excel Writing:** Writes all extracted companies to an Excel file, with options to overwrite or append.

---

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd <project-folder>
   ```
2. **Create a virtual environment and install dependencies:**
   ```bash
   uv venv .venv
   .venv\Scripts\activate  # On Windows
   uv pip install -r requirements.txt
   # Or, if requirements.txt is missing:
   uv pip install pymupdf openpyxl pandas rich pydantic-settings python-dotenv openai
   ```
3. **Set up environment variables:**
   - Copy `.env.sample` to `.env` and fill in your OpenRouter API key and model info.
   - Example `.env`:
     ```env
     OPENROUTER_API_KEY=sk-or-...
     OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
     OPENROUTER_MODEL=google/gemini-2.0-flash-001
     ```

---

## 🖥️ Usage

Run the CLI from the project root:

```bash
python -m app.main --input <PDF_PATH> [options]
```

Or, if using uv:

```bash
uv run python -m app.main --input "data/input/your.pdf" --start-page 0 --end-page 10 --method api --output "data/output/results.xlsx" --overwrite
```

Example:

```bash
uv run python -m app.main --input "data/input/Japanese Companies in Thailand-Directory-unlocked.pdf" --start-page 21 --end-page 670 --method api --output "data/output/results_full.xlsx" --overwrite
```

### CLI Options

| Option       | Type | Default     | Description                                                |
| ------------ | ---- | ----------- | ---------------------------------------------------------- |
| --input      | str  | (required)  | Path to input PDF file                                     |
| --password   | str  | None        | Password for locked PDF (if needed)                        |
| --start-page | int  | 0           | Start page (0-indexed)                                     |
| --end-page   | int  | -1          | End page (0-indexed, -1 for last page)                     |
| --method     | str  | api         | Extraction method: 'api' (OpenRouter) or 'local' (not yet) |
| --output     | str  | output.xlsx | Output Excel file path                                     |
| --overwrite  | flag | False       | Overwrite output file (otherwise append)                   |

### Example

```bash
python -m app.main --input "data/input/Companies.pdf" --password secret --start-page 1 --end-page 10 --method api --output "results.xlsx" --overwrite
```

---

## 📝 Output Excel Format

| Company Name    | PIC Name       | PIC Position      | Emails                   |
| --------------- | -------------- | ----------------- | ------------------------ |
| ABC Co., Ltd.   | Mr. John Doe   | Managing Director | john@abc.com             |
| XYZ Recruitment | Ms. Jane Smith | HR Manager        | jane@xyz.com, hr@xyz.com |

---

## 🛠️ Troubleshooting

- **openpyxl not found:** Install with `uv pip install openpyxl`.
- **.env not loaded:** Ensure `.env` is in the project root and variables are set.
- **API errors:** Check your OpenRouter API key and model in `.env`.
- **PDF password issues:** Make sure to provide the correct password if the PDF is protected.

---

## 🧩 Project Structure

```
app/
  main.py                # CLI entry point
  settings.py            # Loads environment/config
  extractors/            # Extraction logic (API, local)
  readers/               # PDF reading logic
  writers/               # Excel writing logic
  models/                # Pydantic models
```

---

## 🧠 Extending the Project

- Add a local extractor (see `app/extractors/local_extractor.py`)
- Convert to a FastAPI backend for web use
- Add more robust error handling and logging

---

## 📄 License

MIT License
