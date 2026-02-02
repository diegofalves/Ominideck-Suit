import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_HTML = BASE_DIR / "rendering" / "html" / "projeto_migracao.html"
OUTPUT_PDF = BASE_DIR / "rendering" / "pdf" / "projeto_migracao.pdf"


def render_pdf(html_path: Path):
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "wkhtmltopdf",
        "--enable-local-file-access",
        "--page-size", "A4",
        "--margin-top", "15mm",
        "--margin-bottom", "15mm",
        "--margin-left", "15mm",
        "--margin-right", "15mm",
        str(html_path),
        str(OUTPUT_PDF)
    ], check=True)

    print(f"PDF gerado em: {OUTPUT_PDF}")


if __name__ == "__main__":
    html_input = Path(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT_HTML
    render_pdf(html_input)
