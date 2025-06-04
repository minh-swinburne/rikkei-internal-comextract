import pandas as pd
import os
from app.models.company import CompanyInfo

def write_companies_to_excel(companies: list[CompanyInfo], output_path: str, overwrite: bool = False):
    # Prepare data for DataFrame
    rows = [
        {
            "Company Name": c.company_name,
            "PIC Name": c.pic_name,
            "PIC Position": c.pic_position,
            "Emails": ", ".join(c.emails)
        }
        for c in companies
    ]
    df = pd.DataFrame(rows)
    # If not overwrite and file exists, append (without duplicating header)
    if not overwrite and os.path.exists(output_path):
        existing = pd.read_excel(output_path)
        df = pd.concat([existing, df], ignore_index=True)
    # Always write with header
    df.to_excel(output_path, index=False) 