import json
from typing import Optional
from openai import OpenAI
from app.settings import settings
from app.extractors.base import BaseExtractor
from app.models.invoice import Invoice

class APIExtractor(BaseExtractor):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.openrouter_api_key
        self.base_url = base_url or settings.openrouter_base_url
        self.model = model or settings.openrouter_model

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def extract(self, page_text: str) -> Invoice:
        system_prompt = (
            "You are a helpful assistant that extracts invoice data from the text provided by the user.\n"
            "The text is a page of a PDF file, and it contains information about the invoice with multiple items and their details.\n"
            "The invoice contains the following information:\n"
            "\t- ID\n"
            "\t- Date\n"
            "\t- Seller (The company that created this invoice)\n"
            "\t- Buyer (The company that received this invoice)\n"
            "\t- A table of product items\n"
            "\t- Net Price (The total price of the items before tax)\n"
            "\t- Total Price (The total price of the items after tax)\n"
            "For each item in the table, return:\n"
            "\t- ID\n"
            "\t- Description\n"
            "\t- Ordered Quantity\n"
            "\t- Shipped Quantity (may be different from the ordered quantity if some items are not shipped, for instance, ordered 3 but 2 shipped today, and 1 shipped tomorrow)\n"
            "\t- Unit Price\n"
            "\t- Total Price (The total price of this item, i.e. Unit Price * Ordered Quantity)\n"
        )
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "invoice",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": "If the PDF shows PURCHASE ORDER, than it is 'purchase order', else, it is 'invoice'"
                        },
                        "id": {
                            "type": "string",
                            "description": "The ID of the invoice (e.g. 60-67977-11)"
                        },
                        "date": {
                            "type": "string",
                            "description": "The date of the invoice in YYYY-MM-DD format (e.g. 2025-01-01)"
                        },
                        "seller": {
                            "type": "string",
                            "description": "The name of the company that created this invoice (e.g. INGRAM MICRO INC.)"
                        },
                        "buyer": {
                            "type": "string",
                            "description": "The name of the company that received this invoice (e.g. KDDI AMERICA INC)"
                        },
                        "items": {
                            "type": "array",
                            "description": "The list of items in the invoice",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {
                                        "type": "string",
                                        "description": "The ID of the item (e.g. JX7567, 06RZ78)"
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "The description of the item, may consist of multiple lines"
                                    },
                                    "ordered_quantity": {
                                        "type": "number",
                                        "description": "The ordered quantity of the item (e.g. 1, 100, 1000)"
                                    },
                                    "shipped_quantity": {
                                        "type": "number",
                                        "description": "The shipped quantity of the item (e.g. 1, 100, 1000). If type is a Purchase order, this field is empty."
                                    },
                                    "unit_price": {
                                        "type": "number",
                                        "description": "The unit price of the item (e.g. 100, 1000)"
                                    },
                                    "total_price": {
                                        "type": "number",
                                        "description": "The total price of the item (e.g. 100, 1000)"
                                    }
                                },
                                "required": ["id", "description", "ordered_quantity", "unit_price", "total_price"],
                                "additionalProperties": False
                            }
                        },
                        "net_price": {
                            "type": "number",
                            "description": "The net price of the invoice (e.g. 100, 1000)"
                        },
                        "total_price": {
                            "type": "number",
                            "description": "The total price of the invoice (e.g. 100, 1000)"
                        }
                    },
                    "required": ["id", "date", "seller", "buyer", "items", "net_price", "total_price"],
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
                        "You MUST return a JSON object following this schema (with no code block wrappers like ```json, formatting or additional text):\n" +
                        json.dumps(response_format["json_schema"], indent=2) + "\n\n" +
                        "The JSON object must be a valid JSON object, and it must be a single object."
                    )},
                    {"role": "user", "content": page_text}
                ],
            )
        finally:
            # The response will be a JSON object as string
            content = response.choices[0].message.content
            
            # Remove Markdown code block wrappers if present
            if content.strip().startswith("```json"):
                content = content.strip()[7:-3].strip()  # remove ```json and ending ```
            elif content.strip().startswith("```"):
                content = content.strip()[3:-3].strip()  # just in case it uses plain ```

            data = json.loads(content)
            invoice = Invoice.model_validate(data)
            return invoice