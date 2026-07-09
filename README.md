# PHP Secret Scanner LLM

## Descrição geral
Ferramenta CLI acadêmica desenvolvida em Python para detecção de segredos (senhas, tokens, chaves) expostos em código-fonte PHP.

## Descrição do problema
Segredos frequentemente são acidentalmente inseridos em código PHP (hardcoded) e versionados em repositórios. Isso gera um risco crítico de comprometimento de sistemas por exposição indevida de credenciais a terceiros ou atacantes.

## Motivação
Explorar uma abordagem híbrida que une heurísticas clássicas a Modelos de Linguagem Grande (LLMs) para classificar achados semânticos. A motivação central é melhorar a precisão, mantendo rigoroso controle sobre o que é enviado para fora (sanitização).

## Desenvolvimento assistido por IA
Este projeto é um MVP acadêmico estruturado com apoio de IA, garantindo boas práticas na construção de ferramentas de AppSec, gerência de dependências (uv) e arquitetura modularizada.

## Objetivo
Criar uma prova de conceito que possa varrer um ou múltiplos arquivos PHP, encontrar possíveis segredos, sanitizá-los e gerar um relatório (Markdown/HTML) para o desenvolvedor, com uso opcional de IA para contextualizar e justificar.

## Abordagem adotada
1. Busca de arquivos e leitura linha a linha.
2. Heurísticas baseadas em nomes de variáveis e padrões RegExp.
3. Sanitização instantânea do valor (Ex: `se****23`).
4. Envio do trecho sanitizado para a LLM (opcional).
5. Geração de relatórios com os dados sumarizados.

## Arquitetura da ferramenta
![Arquitetura da solução](docs/images/arquitetura.png)

Entrada -> CLI -> Coleta de arquivos PHP -> Scanner -> Heurísticas -> Sanitização -> LLM opcional -> Relatórios e logs

## Tecnologias utilizadas
- Python >= 3.13
- uv (gerenciador de pacotes rápido)
- Typer (CLI)
- Rich (Formatação de terminal)
- Pytest (Testes)
- SDK da OpenAI

## Estrutura do projeto
- `src/` - Código da ferramenta.
- `examples/` - Arquivos PHP para teste.
- `tests/` - Testes automatizados.
- `docs/` - Documentação.

## Instalação do ambiente Python e uv
Instale o Python 3.13 e o `uv`. Exemplo de instalação do uv:
```bash
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
```

## Instalação e preparação
Clone este repositório e execute:


uv sync

## Configuração do projeto
Copie o arquivo de exemplo de ambiente:

Bash
cp .env.example .env

## Configuração da LLM
No arquivo .env, ajuste LLM_PROVIDER (mock, disabled, openai). Se for openai, preencha LLM_API_KEY.

## Segurança no uso de LLM
Atenção: Segredos completos nunca são enviados para a API de LLM. A função de sanitização mascara o valor (ex: ****) antes do envio ao provedor.

## Uso básico
Bash
uv run php-secret-scan <diretorio_ou_arquivo> --output <saida.html_ou_md>

## Opções da CLI
--output / -o: Relatório gerado (.md ou .html)

--llm-provider: mock, disabled, openai

--llm-model: Modelo desejado

--recursive / --no-recursive: Busca recursiva (padrão sim)

--verbose / -v: Log de configurações no terminal

--llm-prompt-log: Caminho para log JSONL do prompt

## Exemplos de execução
Bash
uv run php-secret-scan examples --output reports/relatorio.html --verbose

## Relatórios gerados
O sistema cria tabelas limpas informando linha, categoria, trecho (sempre sanitizado) e a justificativa (heurística ou da IA).

## Log de prompts da LLM
Pode ser gerado informando --llm-prompt-log logs/prompts.jsonl. Apenas o código já mascarado será salvo.

## Categorias de achados
Senha/Credencial

Token

Chave de API

Secret

Chave privada

String de conexão com credencial

Valor sensível hardcoded

Indefinido

Exemplos de código detectável
PHP
$dbPassword = "senha_ficticia_123"; // Detectado por heurística.
$apiKey = "sk-exemplo"; // Detectado por heurística.
Tratamento de erros
Se a chave da OpenAI não for encontrada e --llm-provider openai for passado, o sistema fará um fallback elegante para heurísticas e alertará no relatório.

## Testes de reprodutibilidade
Veja docs/testes.md.

## Documentação complementar
Veja CONTRIBUTING.md e ROADMAP.md.

## Desenvolvimento
Para testar, use uv run pytest. Para formatar, uv run ruff check ..

## Limitações conhecidas
A ferramenta avalia arquivo por arquivo e não compreende fluxo de controle de variáveis em arquivos diferentes. A sanitização baseia-se em padrões RegExp pré-definidos.

## Boas práticas de segurança
Use variáveis de ambiente (getenv) e cofres de senhas, nunca faça hardcode de credenciais.

## Status do projeto
MVP - Prova de Conceito.

## Aviso
Esta ferramenta é um artefato experimental, desenvolvido exclusivamente para fins acadêmicos no contexto de uma disciplina de curso de mestrado.

O projeto não foi concebido, validado ou homologado para uso real em ambientes de produção, auditorias profissionais de segurança, processos corporativos ou qualquer situação que exija garantia de precisão, completude ou confiabilidade.

A ferramenta pode apresentar falsos positivos, falsos negativos, limitações técnicas e comportamentos inesperados. Portanto, não deve ser utilizada como única fonte de análise para identificação de segredos expostos ou vulnerabilidades em código-fonte.

O autor não se responsabiliza por quaisquer danos, perdas, falhas, decisões, incidentes de segurança, exposições indevidas, interpretações equivocadas ou quaisquer outras situações decorrentes do uso, modificação, distribuição ou execução desta ferramenta.

O uso deste artefato é de inteira responsabilidade de quem o utiliza.

## Licença
Todos os direitos são reservados ao autor.

Não é permitido o uso comercial deste software, de seu código-fonte, documentação, relatórios, exemplos ou quaisquer partes do projeto sem autorização prévia e expressa do autor.

O uso, cópia, modificação ou distribuição deste artefato somente é permitido para fins acadêmicos, educacionais ou de estudo, desde que preservados os créditos de autoria e esta declaração de licença.