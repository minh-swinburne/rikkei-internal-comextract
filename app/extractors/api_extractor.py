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
            "You are a helpful assistant that extracts company data from the text provided by the user.\n"
            "The text is a page of a PDF file, and it contains information about multiple companies and their contact details.\n"
            "For each company, return:\n"
            "\t- Company name\n"
            "\t- PIC (Person in Charge / Representative) full name with title\n"
            "\t- PIC job position / title\n"
            "\t- Email(s), comma-separated\n"
            "Information about the PIC / representative is usually wrapped in lenticular brackets, with a leading symbol / letter. For example, `【rMr. Kentaro Taki, CEO】` means the PIC is Mr. Kentaro Taki, and the job position is CEO.\n"
            "Sometimes, the PIC information and email are not available, in that case, return an empty string for the PIC and email fields.\n"
        )
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "companies",
                "schema": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "company_name": {
                                "type": "string",
                                "description": "The name of the company (e.g. HONDA SAFETY RIDING PARK)"
                            },
                            "pic_name": {
                                "type": "string",
                                "description": "The full name of the person in charge / representative of the company with title (e.g. Mr. Toshinobu Hirano)"
                            },
                            "pic_position": {
                                "type": "string",
                                "description": "The job position / title of the person in charge / representative of the company (e.g. Managing Director)"
                            },
                            "emails": {
                                "type": "array",
                                "description": "The email(s) of the person in charge of the company or the company",
                                "items": {
                                    "type": "string",
                                    "description": "The email of the person in charge of the company or the company (e.g. t.hirano@honda-safety-riding-park.com, marketing@honda-safety-riding-park.com)"
                                }
                            }
                        },
                        "required": ["company_name", "pic_name", "pic_position", "emails"],
                        "additionalProperties": False
                    }
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
                if "emails" in item:
                    if isinstance(item["emails"], str):
                        item["emails"] = [e.strip() for e in item["emails"].split(",") if e.strip()]
                    elif isinstance(item["emails"], list):
                        item["emails"] = [e.strip() for e in item["emails"] if e.strip()]
                companies.append(CompanyInfo.model_validate(item))
            return companies
