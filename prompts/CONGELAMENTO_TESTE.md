<!-- Registro de congelamento gerado em 2026-11-21T01:56:59Z -->

# Congelamento antes da avaliação no teste

Data/hora (UTC): 2026-11-21T01:56:59Z. Até este momento, os rótulos da partição de teste não foram lidos por nenhum script de ajuste: o léxico, o mapeamento do K-means, o prompt v1.3 e os exemplos few-shot foram definidos só com a partição de desenvolvimento. Ajuste feito no desenvolvimento: uma rodada (prompt v1.2 → v1.3, esclarecimento APR_ATIVA × LETRAMENTO) e o critério de cobertura literal das evidências.

| Artefato | SHA-256 |
|---|---|
| `src/categorias.py` | `96dbf2faee34b4d97b13d5fff64b48145104866c09ebf13f3e87c96247dc218e` |
| `src/classificacao_llm.py` | `1431cf3f641b0aa84ff3fdfab8207c63549669214dcd8598fd489919dccc2f4f` |
| `src/avaliacao.py` | `62687ee0d23bbb1ece53f4958d8aad0089aebfd9f3e7380e70ef32cd7acb776c` |
| `prompts/prompt_classificacao_v1.3.md` | `adc0c6810ad7de4273985c9f31c27e58a76f2adc010253a9a7fe35ff8923c4b6` |
| `prompts/exemplos_fewshot.json` | `9c9346c310d3f1cefac790eb28abab0e4c1480e198060cc12ee056fb89ed319c` |
| `data/processed/rotulos_lexico.csv` | `3685830a0615b981228f0735a854bb6490a0ecf59b74f1c9995ca37aa4d5efc8` |
| `data/processed/grupos_kmeans.csv` | `451195bb133a5462bbe724fefefcfdff92fd2b0bce265b17ce3b9fe0455692ec` |
| `anotacao/padrao_ouro_desenvolvimento.csv` | `a6896afc57829db31bbf1e60e543c07840de825fa707dfb48b61867f19a61855` |

## Alterações posteriores ao congelamento

- `src/avaliacao.py`: acrescentadas as funções `rotulos_anotador`, `kappa_medio` e `contra_anotadores` (comparação de cada método com cada anotador). Só leitura de resultados; nenhum método, prompt ou mapeamento foi alterado.
- `src/concordancia.py`: geração da planilha de divergências em `.xlsx`. Não afeta os métodos.
