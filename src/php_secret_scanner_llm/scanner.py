import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional

from php_secret_scanner_llm.llm import classify_with_llm

@dataclass(frozen=True)
class Finding:
    file_path: Path
    line_number: int
    category: str
    sanitized_snippet: str
    justification: str

def mask_value(value: str) -> str:
    """Mascarar valores mantendo caracteres úteis limitados."""
    if len(value) <= 4:
        return "****"
    return f"{value[:2]}****{value[-2:]}"

def sanitize_assignment_value(line: str) -> str:
    """Busca o valor atribuído a uma variável de interesse e aplica máscara."""
    # Heurística para achar o que está entre aspas em uma atribuição
    match = re.search(r'=\s*[\'"](.*?)[\'"]', line)
    if match:
        original = match.group(1)
        masked = mask_value(original)
        return line.replace(original, masked)
    
    # Tratamento para string de conexão explícita sem aspas na mesma regex
    conn_match = re.search(r'(mysql|postgres|mongodb|redis)://[^:]+:([^@]+)@', line)
    if conn_match:
        original_pass = conn_match.group(2)
        return line.replace(original_pass, mask_value(original_pass))
        
    return line

def sanitize_line(line: str) -> str:
    return sanitize_assignment_value(line).strip()

def deduplicate_findings(findings: List[Finding]) -> List[Finding]:
    return list(set(findings))

def scan_line(
    line: str,
    line_number: int,
    file_path: Path,
    provider: str,
    model: str,
    prompt_log_path: Optional[Path]
) -> Optional[Finding]:
    
    # Heurísticas de detecção de segredos
    patterns = [
        r'(?i)(password|passwd|pwd|senha|secret|token|apiKey|api_key|api-key|access_key|auth_token|db_pass|database_password|client_secret)\s*=\s*[\'"].+?[\'"]',
        r'-----BEGIN .* PRIVATE KEY-----',
        r'(?i)Bearer\s+[a-zA-Z0-9\-\._~]+',
        r'AKIA[0-9A-Z]{16}',
        r'(mysql|postgres|mongodb|redis)://[^:]+:[^@]+@'
    ]
    
    for pattern in patterns:
        if re.search(pattern, line):
            sanitized = sanitize_line(line)
            # Aciona LLM para classificar (ou fallback)
            llm_result = classify_with_llm(
                code_line=sanitized,
                provider=provider,
                model=model,
                file_path=str(file_path),
                line_number=line_number,
                prompt_log_path=prompt_log_path
            )
            
            if llm_result.get("is_secret"):
                return Finding(
                    file_path=file_path,
                    line_number=line_number,
                    category=str(llm_result.get("category", "Indefinido")),
                    sanitized_snippet=sanitized,
                    justification=str(llm_result.get("justification", "Identificado via heurística"))
                )
    return None

def scan_file(
    file_path: Path,
    provider: str,
    model: str,
    prompt_log_path: Optional[Path]
) -> List[Finding]:
    findings = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, start=1):
                finding = scan_line(line, i, file_path, provider, model, prompt_log_path)
                if finding:
                    findings.append(finding)
    except Exception:
        pass
    return deduplicate_findings(findings)

def collect_php_files(path: Path, recursive: bool) -> List[Path]:
    if recursive:
        return list(path.rglob("*.php"))
    return list(path.glob("*.php"))

def scan_path(
    path: Path,
    recursive: bool,
    provider: str,
    model: str,
    prompt_log_path: Optional[Path]
) -> Tuple[List[Finding], List[Path]]:
    files = collect_php_files(path, recursive)
    all_findings = []
    for file in files:
        all_findings.extend(scan_file(file, provider, model, prompt_log_path))
    return all_findings, files