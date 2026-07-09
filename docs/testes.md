# Testes de Reprodutibilidade

## Pré-requisitos
- Ter o Python 3.13 e o `uv` instalados.
- Ter executado `uv sync`.

## Estrutura esperada dos arquivos de teste
O diretório `examples/` deve conter no mínimo `safe_example.php`, `vulnerable_example.php` e `nested/config_example.php`.

## Preparação dos arquivos PHP
Os arquivos já foram gerados. Não adicione credenciais reais a eles.

## Teste para gerar relatório HTML
```powershell
uv run php-secret-scan examples --output reports/relatorio.html --verbose
Verifique o arquivo em reports/relatorio.html.

Teste para gerar relatório Markdown
PowerShell
uv run php-secret-scan examples --output reports/relatorio.md --verbose
Teste com --llm-provider disabled
PowerShell
uv run php-secret-scan examples --output reports/relatorio_sem_llm.html --llm-provider disabled --verbose
Teste com --llm-provider openai sem chave e com log de prompt
PowerShell
uv run php-secret-scan examples --output reports/relatorio_openai_sem_chave.html --llm-provider openai --llm-model gpt-5.5 --llm-prompt-log logs/llm_prompts.jsonl --verbose
Validação de que valores sensíveis completos não aparecem no log
PowerShell
Select-String -Path logs/llm_prompts.jsonl -Pattern "sk-exemplo-ficticio-123456789"
(Não deve retornar nada, provando o funcionamento da máscara).

Teste com --no-recursive
PowerShell
uv run php-secret-scan examples --output reports/relatorio_nao_recursivo.html --no-recursive --verbose
Teste de formato inválido
PowerShell
uv run php-secret-scan examples --output reports/relatorio.txt
(Deve falhar com mensagem clara no console).

Teste com arquivo PHP individual
PowerShell
uv run php-secret-scan examples/vulnerable_example.php --output reports/relatorio_arquivo_individual.html --verbose
Teste opcional com OpenAI real
Coloque a chave no .env (ex: LLM_API_KEY=sk-sua-chave) e re-rode o comando com provider openai.

Apenas trechos com máscara (****) chegarão à OpenAI.

Checklist final
[x] O comando executou sem traceback de erro?

[x] Os segredos na tela/relatório estavam como se****23?

[x] A recursividade pegou o subdiretório nested?