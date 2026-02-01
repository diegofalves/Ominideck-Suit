import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

def render_pdf(html_path: str):
    html_path = Path(html_path).resolve()
    output_dir = Path("rendering/pdf")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_pdf = output_dir / (html_path.stem + ".pdf")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_path.as_uri(), wait_until="networkidle")
        page.pdf(
            path=str(output_pdf),
            format="A4",
            print_background=True
        )
        browser.close()

    print(f"PDF gerado em: {output_pdf}")

if __name__ == "__main__":
    render_pdf(sys.argv[1])
