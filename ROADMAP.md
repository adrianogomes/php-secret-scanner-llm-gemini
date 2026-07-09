# Roadmap

## Status atual
MVP acadêmico funcional (Heurísticas + LLM Mock/OpenAI + Relatórios HTML/MD).

## Funcionalidades já implementadas
- Busca recursiva de arquivos PHP.
- Identificação de senhas e chaves por regex.
- LLM como julgador semântico (mascarando payload).
- Geração de HTML consolidado.

## Curto prazo
- Refinar heurísticas.
- Melhorar sanitização (suporte a mais estruturas complexas do PHP).
- Ampliar testes.

## Médio prazo
- Melhorar documentação técnica.
- Adicionar nível de confiança explícito na saída visual.
- Melhorar integração com LLM para contexto multi-linha.

## Longo prazo
- Avaliar parser PHP em vez de regex.
- Avaliar uso em GitHub Actions (Academic POC).
- Criar dataset artificial para benchmarking de ferramentas.

## Fora do escopo atual
- Suporte futuro a outras linguagens (foco exclusivo em PHP no escopo inicial).
- Integração com sistemas JIRA/Bug Trackers.

## Prioridade recomendada
Aperfeiçoamento da regex de sanitização e parser.

## Observação final
Como o foco é acadêmico, o avanço do roadmap dependerá da necessidade das disciplinas.