import html
from collections import defaultdict
from importlib import resources
from pathlib import Path
from typing import List, Dict

from php_secret_scanner_llm.scanner import Finding

def load_report_css() -> str:
    try:
        from php_secret_scanner_llm import assets
        return resources.files(assets).joinpath("report.css").read_text(encoding="utf-8")
    except Exception:
        return "body { font-family: sans-serif; }"

def escape_markdown_cell(text: str) -> str:
    return text.replace("|", "\\|")

def format_path(path: Path) -> str:
    return str(path).replace("\\", "/")

def group_findings_by_file(findings: List[Finding]) -> Dict[str, List[Finding]]:
    grouped = defaultdict(list)
    for f in findings:
        grouped[format_path(f.file_path)].append(f)
    return grouped

def get_files_without_findings(analyzed_files: List[Path], findings: List[Finding]) -> List[str]:
    found_paths = {format_path(f.file_path) for f in findings}
    return [format_path(p) for p in analyzed_files if format_path(p) not in found_paths]

def generate_markdown_report(
    findings: List[Finding], analyzed_files: List[Path], 
    input_path: Path, provider: str, model: str
) -> str:
    grouped = group_findings_by_file(findings)
    safe_files = get_files_without_findings(analyzed_files, findings)
    
    md = [
        "# Relatório de Segredos Expostos", "",
        "## Resumo geral", "",
        f"- **Caminho analisado:** `{format_path(input_path)}`",
        f"- **Provedor de LLM:** `{provider}`",
        f"- **Modelo de LLM:** `{model}`",
        f"- **Arquivos PHP analisados:** {len(analyzed_files)}",
        f"- **Arquivos com achados:** {len(grouped)}",
        f"- **Arquivos sem achados:** {len(safe_files)}",
        f"- **Total de achados:** {len(findings)}", "",
        "## Arquivos analisados sem achados", ""
    ]
    
    for sf in safe_files:
        md.append(f"- `{sf}`")
    if not safe_files:
        md.append("- Nenhum")
        
    md.extend(["", "## Arquivos analisados com achados", ""])
    
    for file, f_list in grouped.items():
        md.append(f"### Arquivo: `{file}`\n")
        md.append("| Linha | Categoria | Trecho sanitizado | Justificativa |")
        md.append("|------:|-----------|-------------------|---------------|")
        for f in sorted(f_list, key=lambda x: x.line_number):
            linha = f.line_number
            cat = escape_markdown_cell(f.category)
            trecho = escape_markdown_cell(f"`{f.sanitized_snippet}`")
            just = escape_markdown_cell(f.justification)
            md.append(f"| {linha} | {cat} | {trecho} | {just} |")
        md.append("")
        
    return "\n".join(md)

def generate_html_report(
    findings: List[Finding], analyzed_files: List[Path], 
    input_path: Path, provider: str, model: str
) -> str:
    grouped = group_findings_by_file(findings)
    safe_files = get_files_without_findings(analyzed_files, findings)
    css = load_report_css()
    
    html_out = [
        f"<!DOCTYPE html><html lang='pt-BR'><head><meta charset='UTF-8'><title>Relatório de Segredos</title><style>{css}</style></head><body>",
        "<div class='container'>",
        "<h1>Relatório de Segredos Expostos</h1>",
        "<div class='card summary-card'>",
        "<h2>Resumo geral</h2>",
        "<ul>",
        f"<li><strong>Caminho analisado:</strong> <code>{html.escape(format_path(input_path))}</code></li>",
        f"<li><strong>Provedor de LLM:</strong> <code>{html.escape(provider)}</code></li>",
        f"<li><strong>Modelo de LLM:</strong> <code>{html.escape(model)}</code></li>",
        f"<li><strong>Arquivos PHP analisados:</strong> {len(analyzed_files)}</li>",
        f"<li><strong>Arquivos com achados:</strong> <span class='badge danger'>{len(grouped)}</span></li>",
        f"<li><strong>Arquivos sem achados:</strong> <span class='badge safe'>{len(safe_files)}</span></li>",
        f"<li><strong>Total de achados:</strong> {len(findings)}</li>",
        "</ul></div>"
    ]

    html_out.append("<div class='section safe-section'><h2>Arquivos analisados sem achados</h2><ul>")
    for sf in safe_files:
        html_out.append(f"<li><code>{html.escape(sf)}</code></li>")
    if not safe_files:
        html_out.append("<li>Nenhum</li>")
    html_out.append("</ul></div>")

    html_out.append("<div class='section danger-section'><h2>Arquivos analisados com achados</h2>")
    for file, f_list in grouped.items():
        html_out.append(f"<div class='file-card'><h3>Arquivo: <code>{html.escape(file)}</code></h3>")
        html_out.append("<table><thead><tr><th>Linha</th><th>Categoria</th><th>Trecho sanitizado</th><th>Justificativa</th></tr></thead><tbody>")
        for f in sorted(f_list, key=lambda x: x.line_number):
            html_out.append(
                f"<tr><td>{f.line_number}</td><td>{html.escape(f.category)}</td>"
                f"<td><code>{html.escape(f.sanitized_snippet)}</code></td>"
                f"<td>{html.escape(f.justification)}</td></tr>"
            )
        html_out.append("</tbody></table></div>")
    html_out.append("</div>")

    html_out.append("</div></body></html>")
    return "".join(html_out)

def write_report(content: str, output: Path):
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        f.write(content)

def generate_report(
    findings: List[Finding], analyzed_files: List[Path], 
    output: Path, input_path: Path, provider: str, model: str
):
    if output.suffix == ".md":
        content = generate_markdown_report(findings, analyzed_files, input_path, provider, model)
    else:
        content = generate_html_report(findings, analyzed_files, input_path, provider, model)
    write_report(content, output)