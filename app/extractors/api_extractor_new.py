import json
from typing import Optional
from openai import OpenAI
from app.settings import settings
from app.extractors.base import BaseExtractor
from app.models.company import CompanyInfo

class APIExtractor(BaseExtractor):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.openrouter_api_key
        self.base_url = base_url or settings.openrouter_base_url
        self.model = model or settings.openrouter_model

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def extract(self, page_text: str) -> list[CompanyInfo]:
        system_prompt = (
                "You are a helpful assistant that extracts product line item data from invoice pages provided by the user.\n"
                "The text is a page of a PDF file (usually converted from image), and it contains a table with multiple purchased items.\n"
                "\n"
                "From the main table, for each line item, return:\n"
                "    - SKU (usually a short product code, e.g., JX7567, 06RZ78)\n"
                "    - Description (multi-line text describing the item, including product name, vendor part number, UPC, serial number, etc.)\n"
                "    - Ordered quantity\n"
                "    - Shipped quantity\n"
                "    - Unit of measure (e.g., EA)\n"
                "    - Unit price (e.g., $34.72)\n"
                "    - Line amount (e.g., $34.72)\n"
                "\n"
                "The first column is usually the SKU. The description often spans multiple lines and may include codes like UPC, VEND PART, or SER NBR.\n"
                "Handling fees or other charges without a SKU should still be included, using \"N/A\" as the SKU and their description as-is.\n"
                "\n"
                "Return the data as a JSON array, with one object per line item, using these exact field names:\n"
                "`SKU`, `Description`, `Ordered`, `Shipped`, `U/M`, `Price`, `Amount`\n"
                "\n"
                "If any fields are missing for a line, return them as empty strings.\n"
                "\n"
        )
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "SKU": {"type": "string"},
                        "Description": {"type": "string"},
                        "Ordered": {"type": "string"},
                        "Shipped": {"type": "string"},
                        "U/M": {"type": "string"},
                        "Price": {"type": "string"},
                        "Amount": {"type": "string"}
                    },
                    "required": ["SKU", "Description", "Ordered", "Shipped", "U/M", "Price", "Amount"],
                    "additionalProperties": False
                }
            }
        }
        # Try structured output (response_format param)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": page_text}
                ],
                response_format=response_format,
                temperature=0,
            )
        except Exception as e:
            # Fallback: try to parse as best-effort
            print(f"Error or model does not support structured output: {e}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": (
                        system_prompt + "\n\n" +
                        "You MUST return a JSON object following this schema (with no code block wrappers, formatting or additional text):\n" +
                        json.dumps(response_format["json_schema"], indent=2) + "\n\n" +
                        "The JSON object must be a valid JSON object, and it must be a list of objects."
                    )},
                    {"role": "user", "content": page_text}
                ],
            )
        finally:
            # The response will be a JSON object as string
            content = response.choices[0].message.content
            data = json.loads(content)
            if isinstance(data, dict) and "companies" in data:
                items = data["companies"]
            elif isinstance(data, list):
                items = data
            else:
                items = [data]
            companies = []
            for item in items:
                # if "emails" in item:
                #     if isinstance(item["emails"], str):
                #         item["emails"] = [e.strip() for e in item["emails"].split(",") if e.strip()]
                #     elif isinstance(item["emails"], list):
                #         item["emails"] = [e.strip() for e in item["emails"] if e.strip()]
                companies.append(CompanyInfo.model_validate(item))
            return companies
