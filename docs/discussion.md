# Company Information Extraction

## Initial Idea

✅ **Your Task Summary**

You want to:

1. Extract structured company info from a **700-page protected PDF** (15+ company entries per page).
2. For  **each company** , extract:
   * **Company name**
   * **PIC (Person in Charge) name**
   * **PIC job position**
   * **Emails (comma-separated)**
3. Fill this into an  **Excel sheet** .

Later you’ll want to upload that Excel to the cloud, but for now you're focusing on steps 1 and 2.

---

### 🔐 Step 0: PDF File Is Copy-Protected – What to Do?

If the PDF  **doesn’t allow copying** , most parsers (like `PyMuPDF`, `pdfplumber`, or `pdfminer`) will still  **fail to extract the text** .

You have  **two options** :

#### ✅ Option A: Unlock the PDF (Recommended)

* Use a tool like `qpdf`:
  ```bash
  qpdf --password=YOURPASSWORD --decrypt input.pdf output.pdf
  ```
* Or online tools like [PDFUnlock](https://www.pdfunlock.com/) if there are no privacy concerns.
* Once decrypted, you can process it page by page.

#### ❌ Option B: OCR (if Unlocking Fails)

* Use `pytesseract` (OCR via Tesseract) or `Azure Read OCR` or `Google Vision OCR`.
* Downside: Slower and less accurate than reading raw text.

---

### 🤖 Step 1: Choose the Model for Info Extraction

#### ✅ Option 1: Call an LLM (like GPT via OpenAI API)

* **Pros** :
* Very high accuracy.
* No setup.
* Can handle missing or reordered fields intelligently.
* **Cons** :
* Costly over hundreds of pages (tokens cost money).
* Slightly slower due to API call latency.

#### ✅ Option 2: Use Local LLM (like `nuextract` via HuggingFace + Haystack)

* **Pros** :
* Cost-effective (free).
* Runs offline.
* **Cons** :
* **Requires decent hardware** (8GB+ RAM minimum, better with GPU).
* Slower unless you're batching inputs.
* Requires setup (Haystack + Python env + model download).

💡 My suggestion:

* **Prototype** with OpenAI API or similar LLM API to validate extraction quality.
* If it works and cost is too high,  **then optimize to local model** .

---

### 🧪 Suggested Development Plan

#### 🔧 Phase 1: Local Dev - PDF to Text per Page

```python
import fitz  # PyMuPDF

def extract_text_by_page(pdf_path):
    doc = fitz.open(pdf_path)
    pages = [page.get_text() for page in doc]
    return pages
```

#### 💬 Phase 2: Call LLM API for Each Page

```python
import openai

def extract_company_info(page_text):
    prompt = f"""
Extract all companies with the following info from this text:
- Company Name
- PIC Name
- PIC Job Position
- Email(s)

Output in JSON list format:
{page_text}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response['choices'][0]['message']['content']
```

You’ll then parse the output and append to Excel.

---

#### 📊 Phase 3: Output to Excel

```python
import pandas as pd

def save_to_excel(data, output_path='companies.xlsx'):
    df = pd.DataFrame(data)
    df.to_excel(output_path, index=False)
```

---

### 🧠 Prompt Engineering Tip

Example prompt to give the model:

> ```
> Text:
> BKK LINK CO., LTD.  
> Mr. Hiroshi Sato, Managing Director  
> www.bkk-link.com  
> japanese@bkk-link.com  
>
> CAREERLINK RECRUITMENT (THAILAND), CO., LTD.  
> Mr. Marshall Ueno, General Manager  
> contact@careerlink.asia
>
> Task:
> Extract the Company Name, PIC Name, Position, and all emails.
>
> Output:
> [
>   {"Company": "BKK LINK CO., LTD.", "PIC": "Mr. Hiroshi Sato", "Position": "Managing Director", "Email": "japanese@bkk-link.com"},
>   {"Company": "CAREERLINK RECRUITMENT (THAILAND), CO., LTD.", "PIC": "Mr. Marshall Ueno", "Position": "General Manager", "Email": "contact@careerlink.asia"}
> ]
> ```

---

### 🗓️ Summary of Recommendations

| Step               | Tool                     | Notes                              |
| ------------------ | ------------------------ | ---------------------------------- |
| 📄 PDF Unlock      | `qpdf`                 | Essential if PDF is copy-protected |
| 📜 Text Extraction | `PyMuPDF`              | Page-by-page for LLM               |
| 🧠 LLM API         | OpenAI or Claude         | Best for first prototype           |
| 🧠 Local Model     | Haystack +`nuextract`  | Use later if API costs too much    |
| 📈 Output          | `pandas + ExcelWriter` | Easy to export to Excel            |

---
