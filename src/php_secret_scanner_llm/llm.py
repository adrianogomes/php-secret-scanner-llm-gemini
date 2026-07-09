import os
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

def write_prompt_log(
    log_path: Path, provider: str, model: str, file_path: str,
    line_number: int, sent_to_provider: bool, sanitized_code: str,
    system_instructions: str, user_prompt: str
):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
        "model": model,
        "file_path": file_path,
        "line_number": line_number,
        "sent_to_provider": sent_to_provider,
        "sanitized_code_line": sanitized_code,
        "system_instructions": system_instructions,
        "user_prompt": user_prompt
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def normalize_category(category: str) -> str:
    allowed = ["Senha/Credencial", "Token", "Chave de API", "Secret", 
               "Chave privada", "String de conexão com credencial", 
               "Valor sensível hardcoded", "Indefinido"]
    return category if category in allowed else "Indefinido"

def normalize_confidence(conf: Any) -> float:
    try:
        return float(conf)
    except (ValueError, TypeError):
        return 0.0

def build_system_instructions() -> str:
    return (
        "Você é um analisador de segurança. Analise o trecho sanitizado de código PHP "
        "e retorne um JSON com is_secret (bool), category (str), justification (str em pt-br) e confidence (float)."
    )

def build_user_prompt(code: str, ctx: str) -> str:
    return f"Analise o seguinte trecho: {code}"

def extract_json_object(text: str) -> dict:
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        return json.loads(text[start:end])
    except Exception:
        return {}

def classify_with_llm(
    code_line: str, provider: str = "mock", model: str = "mock-model",
    variable_context: str = "", file_path: str = "",
    line_number: Optional[int] = None, prompt_log_path: Optional[Path] = None
) -> Dict[str, Any]:
    
    sys_inst = build_system_instructions()
    user_prompt = build_user_prompt(code_line, variable_context)
    sent = False
    result = {
        "is_secret": True,
        "category": "Indefinido",
        "justification": "Identificado por heurística",
        "confidence": 0.5
    }

    if provider == "disabled":
        pass
    
    elif provider == "mock":
        # Simulação simples
        if "senha" in code_line.lower() or "password" in code_line.lower():
            result["category"] = "Senha/Credencial"
        elif "sk-" in code_line.lower() or "api" in code_line.lower():
            result["category"] = "Chave de API"
        else:
            result["category"] = "Secret"
        result["justification"] = "Classificado via modelo mock (simulação)."
        
    elif provider == "openai":
        api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            result["justification"] = "Heurística (OpenAI sem chave configurada)."
        else:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": sys_inst},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                raw_json = response.choices[0].message.content or "{}"
                parsed = extract_json_object(raw_json)
                result["is_secret"] = parsed.get("is_secret", True)
                result["category"] = normalize_category(parsed.get("category", "Indefinido"))
                result["justification"] = parsed.get("justification", "Avaliado via OpenAI")
                result["confidence"] = normalize_confidence(parsed.get("confidence", 0.9))
                sent = True
            except Exception as e:
                result["justification"] = f"Erro na API ({str(e)}) - Fallback heurístico."
                
    if prompt_log_path:
        write_prompt_log(
            prompt_log_path, provider, model, file_path, line_number or 0, 
            sent, code_line, sys_inst, user_prompt
        )
        
    return result