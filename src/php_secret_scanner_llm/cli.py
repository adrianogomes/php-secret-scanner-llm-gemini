import os
from pathlib import Path
from typing import Annotated, Optional

import typer
from dotenv import load_dotenv
from rich.console import Console

from php_secret_scanner_llm.scanner import scan_path, scan_file
from php_secret_scanner_llm.report import generate_report

app = typer.Typer(help="Ferramenta CLI para detecção de segredos em código PHP.")
console = Console()

@app.command()
def main(
    input_path: Annotated[Path, typer.Argument(help="Arquivo PHP ou diretório a ser analisado.")],
    output: Annotated[Path, typer.Option("--output", "-o", help="Caminho de saída (.md ou .html)")],
    llm_provider: Annotated[Optional[str], typer.Option(help="Provider (mock, disabled, openai)")] = None,
    llm_model: Annotated[Optional[str], typer.Option(help="Modelo de LLM")] = None,
    recursive: Annotated[bool, typer.Option("--recursive/--no-recursive", help="Busca recursiva")] = True,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Imprime configurações")] = False,
    llm_prompt_log: Annotated[Optional[Path], typer.Option(help="Log JSONL de prompts")] = None,
):
    load_dotenv()

    # Resolução da configuração de LLM (CLI > ENV > Padrão)
    provider = llm_provider or os.getenv("LLM_PROVIDER", "mock")
    model = llm_model or os.getenv("LLM_MODEL", "mock-model")

    if provider not in ["mock", "disabled", "openai"]:
        console.print(f"[bold red]Erro:[/bold red] Provider de LLM inválido: {provider}")
        raise typer.Exit(code=1)

    if not input_path.exists():
        console.print(f"[bold red]Erro:[/bold red] O caminho de entrada {input_path} não existe.")
        raise typer.Exit(code=1)

    if output.is_dir() or output.suffix not in [".md", ".html"]:
        console.print("[bold red]Erro:[/bold red] A saída deve ser um arquivo com extensão .md ou .html.")
        raise typer.Exit(code=1)
        
    if verbose:
        console.print("[bold cyan]--- Configurações ---[/bold cyan]")
        console.print(f"Input: {input_path}")
        console.print(f"Output: {output}")
        console.print(f"Provider: {provider}")
        console.print(f"Model: {model}")
        console.print(f"Recursive: {recursive}")
        console.print(f"Prompt Log: {llm_prompt_log}")
        console.print("[bold cyan]---------------------[/bold cyan]")

    findings, analyzed_files = [], []
    if input_path.is_file():
        if input_path.suffix != ".php":
            console.print("[bold red]Erro:[/bold red] Arquivo de entrada não tem extensão .php.")
            raise typer.Exit(code=1)
        findings = scan_file(input_path, provider, model, llm_prompt_log)
        analyzed_files = [input_path]
    else:
        findings, analyzed_files = scan_path(input_path, recursive, provider, model, llm_prompt_log)
        if not analyzed_files:
            console.print("[bold red]Erro:[/bold red] Nenhum arquivo .php encontrado no diretório.")
            raise typer.Exit(code=1)

    generate_report(findings, analyzed_files, output, input_path, provider, model)
    console.print(f"[bold green]Sucesso![/bold green] Relatório gerado em: {output}")

if __name__ == "__main__":
    app()