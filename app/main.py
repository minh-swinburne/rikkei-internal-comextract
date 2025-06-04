import argparse
from app.readers import read_pdf_pages
from app.extractors import APIExtractor
from app.writers.excel_writer import write_companies_to_excel
from rich.progress import Progress

def main():
    parser = argparse.ArgumentParser(description="Company Info Extractor")
    parser.add_argument('--input', required=True, help='Path to input PDF')
    parser.add_argument('--password', default=None, help='PDF password')
    parser.add_argument('--start-page', type=int, default=0, help='Start page (0-indexed)')
    parser.add_argument('--end-page', type=int, default=-1, help='End page (0-indexed), -1 for last page')
    parser.add_argument('--method', choices=['api', 'local'], default='api', help='Extraction method, either "api" or "local"')
    parser.add_argument('--output', default='output.xlsx', help='Output Excel file')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite output file')
    args = parser.parse_args()

    print(f"Reading PDF: {args.input}")
    pages = read_pdf_pages(args.input, args.password, args.start_page, args.end_page)
    print(f"Extracting company info from {len(pages)} pages...")

    if args.method == 'api':
        extractor = APIExtractor()
        print(f"Using API extractor with model: {extractor.model}")
    elif args.method == 'local':
        raise NotImplementedError("Local extraction method is not implemented yet.")
        extractor = LocalExtractor()
        print(f"Using local extractor with model: {extractor.model}")
    else:
        raise NotImplementedError("Only 'api' and 'local' methods are available.")

    companies = []
    with Progress() as progress:
        task = progress.add_task("Extracting pages...", total=len(pages))
        for page_num, text in pages.items():
            data = extractor.extract(text)
            progress.console.print(f"Page {page_num}: extracted {len(data)} companies.")
            companies.extend(data)
            progress.update(task, advance=1)
        progress.console.print(f"Completed extracting {len(companies)} companies from {len(pages)} pages.")
    write_companies_to_excel(companies, args.output, overwrite=args.overwrite)
    print(f"Done. Results written to {args.output}")

if __name__ == "__main__":
    main()
