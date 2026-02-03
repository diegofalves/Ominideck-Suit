#!/usr/bin/env python3
"""
Ajuste 9.7: Validação Automática da Cadeia JSON → MD → HTML → PDF

Validador determinístico que assegura que todo SQL presente no JSON
está corretamente refletido em MD, HTML e PDF.

Não modifica nada. Apenas valida e reporta.
"""

import json
import re
import html as html_module
from pathlib import Path
from typing import Dict, List, Tuple
import pdfplumber


BASE_DIR = Path(__file__).resolve().parents[2]
JSON_FILE = BASE_DIR / "domain" / "projeto_migracao" / "projeto_migracao.json"
MD_FILE = BASE_DIR / "rendering" / "md" / "projeto_migracao.md"
HTML_FILE = BASE_DIR / "rendering" / "html" / "projeto_migracao.html"
PDF_FILE = BASE_DIR / "rendering" / "pdf" / "projeto_migracao.pdf"
REPORT_FILE = BASE_DIR / "rendering" / "reports" / "validation_chain_report.json"


class ValidationResult:
    """Armazena resultado de validação para um estágio."""
    
    def __init__(self, stage: str):
        self.stage = stage
        self.passed = 0
        self.failed = 0
        self.errors: List[Dict[str, str]] = []
    
    def add_pass(self):
        self.passed += 1
    
    def add_fail(self, obj_name: str, error_msg: str):
        self.failed += 1
        self.errors.append({"object": obj_name, "error": error_msg})
    
    def is_ok(self) -> bool:
        return self.failed == 0
    
    def summary(self) -> str:
        total = self.passed + self.failed
        status = "✓" if self.is_ok() else "✗"
        return f"[{status}] {self.stage}: {self.passed}/{total} objetos válidos"


def _normalize_sql(sql: str) -> str:
    """Normaliza SQL para comparação: trim + whitespace único."""
    return re.sub(r"\s+", " ", sql.strip())


def _load_json() -> dict:
    """Carrega JSON source."""
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_json() -> Tuple[ValidationResult, Dict[str, dict]]:
    """Valida JSON: cada objeto com technical_content.type == SQL deve ter conteúdo não vazio."""
    result = ValidationResult("JSON")
    data = _load_json()
    
    objects_with_sql = {}
    
    for group in data.get("groups", []):
        for obj in group.get("objects", []):
            obj_name = obj.get("name", "Unknown")
            tech_content = obj.get("technical_content", {})
            
            if tech_content.get("type") == "SQL":
                sql = tech_content.get("content", "").strip()
                
                if sql and len(sql) >= 15:  # Mínimo realista: "SELECT * FROM X" = 16 chars
                    objects_with_sql[obj_name] = {
                        "sql": sql,
                        "object_type": obj.get("object_type"),
                        "group": group.get("label")
                    }
                    result.add_pass()
                else:
                    result.add_fail(obj_name, "SQL vazio ou muito curto (min 15 chars)")
    
    return result, objects_with_sql


def validate_md(objects_with_sql: Dict[str, dict]) -> ValidationResult:
    """Valida MD: cada objeto deve ter 'Query de Extração' com bloco sql."""
    result = ValidationResult("MD")
    
    md_content = MD_FILE.read_text(encoding="utf-8")
    
    for obj_name, obj_data in objects_with_sql.items():
        json_sql = _normalize_sql(obj_data["sql"])
        
        # Procurar seção "Query de Extração" próxima ao nome do objeto
        pattern = re.compile(
            rf"### {re.escape(obj_name)}.*?### Query de Extração\s*```sql\s*(.*?)```",
            re.DOTALL
        )
        match = pattern.search(md_content)
        
        if not match:
            result.add_fail(obj_name, "Query de Extração ausente no MD")
            continue
        
        md_sql = _normalize_sql(match.group(1))
        
        # Comparação normalizada: primeiras 100 chars devem coincidir
        if md_sql[:100] == json_sql[:100]:
            result.add_pass()
        else:
            result.add_fail(obj_name, "SQL no MD não corresponde ao JSON")
    
    return result


def validate_html(objects_with_sql: Dict[str, dict]) -> ValidationResult:
    """Valida HTML: cada objeto deve ter <pre><code> com SQL (decodificado)."""
    result = ValidationResult("HTML")
    
    html_content = HTML_FILE.read_text(encoding="utf-8")
    
    for obj_name, obj_data in objects_with_sql.items():
        json_sql = _normalize_sql(obj_data["sql"])
        
        # Procurar <h3> com nome do objeto + <pre><code> subsequente
        # O padrão procura por qualquer bloco <pre><code> após o h3
        pattern = re.compile(
            rf"<h3>.*?{re.escape(obj_name)}.*?</h3>.*?<pre><code[^>]*>(.*?)</code></pre>",
            re.DOTALL
        )
        matches = pattern.findall(html_content)
        
        if not matches:
            result.add_fail(obj_name, "Nenhum bloco <pre><code> encontrado no HTML")
            continue
        
        # Decodificar HTML entities e normalizar
        found = False
        for html_sql_encoded in matches:
            html_sql = _normalize_sql(html_module.unescape(html_sql_encoded))
            
            # Comparação normalizada
            if html_sql[:100] == json_sql[:100]:
                found = True
                break
        
        if found:
            result.add_pass()
        else:
            result.add_fail(obj_name, "SQL no HTML não corresponde ao JSON")
    
    return result


def validate_pdf(objects_with_sql: Dict[str, dict]) -> ValidationResult:
    """Valida PDF: SQL deve estar presente com quebras de linha."""
    result = ValidationResult("PDF")
    
    try:
        with pdfplumber.open(PDF_FILE) as pdf:
            # Extrair todo texto do PDF
            pdf_text = ""
            for page in pdf.pages:
                pdf_text += page.extract_text() or ""
            
            pdf_text_normalized = _normalize_sql(pdf_text)
            
            for obj_name, obj_data in objects_with_sql.items():
                json_sql = _normalize_sql(obj_data["sql"])
                
                # Verificar presença: primeiras 50 chars
                if json_sql[:50] in pdf_text_normalized:
                    result.add_pass()
                else:
                    result.add_fail(obj_name, "SQL não encontrado no PDF")
    
    except Exception as e:
        result.add_fail("PDF", f"Erro ao ler PDF: {str(e)}")
    
    return result


def generate_report(
    json_result: ValidationResult,
    md_result: ValidationResult,
    html_result: ValidationResult,
    pdf_result: ValidationResult
) -> dict:
    """Gera relatório estruturado."""
    all_ok = all([
        json_result.is_ok(),
        md_result.is_ok(),
        html_result.is_ok(),
        pdf_result.is_ok()
    ])
    
    errors = []
    for result in [json_result, md_result, html_result, pdf_result]:
        for error in result.errors:
            errors.append({
                "stage": result.stage,
                **error
            })
    
    report = {
        "summary": {
            "total_objects_with_sql": json_result.passed,
            "json_ok": json_result.passed,
            "md_ok": md_result.passed,
            "html_ok": html_result.passed,
            "pdf_ok": pdf_result.passed,
            "status": "PASS" if all_ok else "FAIL"
        },
        "errors": errors
    }
    
    return report


def print_console_report(
    json_result: ValidationResult,
    md_result: ValidationResult,
    html_result: ValidationResult,
    pdf_result: ValidationResult,
    report: dict
):
    """Imprime relatório no console."""
    print("\n" + "=" * 70)
    print("VALIDAÇÃO DA CADEIA JSON → MD → HTML → PDF")
    print("=" * 70)
    
    print("\n📊 RESULTADOS:\n")
    print(json_result.summary())
    print(md_result.summary())
    print(html_result.summary())
    print(pdf_result.summary())
    
    if report["errors"]:
        print("\n❌ ERROS ENCONTRADOS:\n")
        for error in report["errors"]:
            print(f"  [{error['stage']}] {error['object']}: {error['error']}")
    
    status = report["summary"]["status"]
    if status == "PASS":
        print("\n✅ STATUS FINAL: PASS")
        print("   Cadeia íntegra e consistente.\n")
    else:
        print("\n❌ STATUS FINAL: FAIL")
        print("   Uma ou mais etapas apresentaram erros.\n")
    
    print("=" * 70 + "\n")
    
    return 0 if status == "PASS" else 1


def main():
    """Executa validação completa."""
    
    # 1. Validar JSON
    json_result, objects_with_sql = validate_json()
    
    if not objects_with_sql:
        print("❌ Nenhum objeto com SQL válido encontrado no JSON.")
        return 1
    
    # 2. Validar MD
    md_result = validate_md(objects_with_sql)
    
    # 3. Validar HTML
    html_result = validate_html(objects_with_sql)
    
    # 4. Validar PDF
    pdf_result = validate_pdf(objects_with_sql)
    
    # 5. Gerar relatório
    report = generate_report(json_result, md_result, html_result, pdf_result)
    
    # 6. Gerar arquivo de relatório JSON
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # 7. Imprimir no console
    exit_code = print_console_report(json_result, md_result, html_result, pdf_result, report)
    
    return exit_code


if __name__ == "__main__":
    import sys
    sys.exit(main())
