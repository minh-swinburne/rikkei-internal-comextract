import os
import json
from app.models.invoice import Invoice

def write_invoices_to_json(invoices: list[Invoice], output_path: str, overwrite: bool = False):
    if not overwrite and os.path.exists(output_path):
        raise FileExistsError(f"File {output_path} already exists.")
    with open(output_path, "w") as f:
        json.dump([i.model_dump() for i in invoices], f, indent=2)