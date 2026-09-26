<!--
Projeto: Análise de Recomendações Pedagógicas para o Uso de Inteligência Artificial
         Generativa na Educação a Distância por meio de PLN e LLMs
Integrante: Daniel Ribeiro Pauleti - RA 10723162
Arquivo: anotacao/protocolo_anotacao.md
Síntese: livro de códigos e protocolo de anotação manual (validação humana).
Histórico de alterações:
  2026-09-25 - Daniel Ribeiro Pauleti - Versão inicial.
-->

# Protocolo de anotação manual (padrão-ouro)

## Amostra
- `amostra_anotacao.csv`: **60 publicações** (≈29% do corpus de 208), sorteadas com
  estratificação por ano × idioma (`random_state = 42`), gerada em
  `notebooks/04_baseline_lexico_tfidf.ipynb`.
- Partição **desenvolvimento** (20): usada para calibrar o livro de códigos e escolher os
  exemplos do prompt few-shot.
- Partição **teste** (40): usada **somente** na avaliação final dos métodos (N2).

## Procedimento
1. Ler título e resumo **antes** de ver qualquer saída automática (léxico, K-means ou LLM).
2. Para cada uma das 8 categorias, marcar `1` se o texto **recomenda/propõe/conclui** algo
   sobre ela; `0` caso contrário. Simples menção a um termo **não** conta.
3. Marcar `tem_recomendacao = 1` se houver ao menos uma recomendação pedagógica explícita.
4. Registrar dúvidas em `observacoes`; casos ambíguos são discutidos e a regra de decisão
   é acrescentada a este documento (versão do livro de códigos incrementada).
5. **Confiabilidade:** a partição de teste é anotada por dois anotadores (integrante e um
   segundo leitor voluntário) *ou*, na impossibilidade, reanotada pelo mesmo anotador após
   ≥ 10 dias (confiabilidade intra-anotador). Mede-se o **kappa de Cohen** por categoria;
   κ ≥ 0,61 (concordância substancial) é a meta. Divergências são resolvidas por consenso.

## Categorias (livro de códigos v1)
| Código | Categoria | Inclui | Não inclui |
|---|---|---|---|
| APR_ATIVA | Aprendizagem ativa | tutoria, feedback formativo, prática guiada, personalização, autorregulação | IA apenas como gerador de conteúdo para o professor |
| AUTORIA | Autoria e integridade acadêmica | plágio, declaração de uso, políticas de integridade, detectores | ética genérica sem relação com autoria |
| PENS_CRITICO | Pensamento crítico | argumentação, reflexão, evitar dependência | criatividade sem relação com raciocínio crítico |
| VERIFICACAO | Verificação das respostas | alucinações, checagem de fatos/fontes, confiabilidade | desempenho do modelo em provas sem orientação ao estudante |
| ETICA | Ética e uso responsável | vieses, equidade, transparência, uso responsável | privacidade (usar PRIVACIDADE) |
| AVALIACAO | Avaliação da aprendizagem | redesenho de avaliações, correção automática, avaliação autêntica | "avaliação" no sentido de avaliar o estudo/pesquisa |
| PRIVACIDADE | Privacidade e proteção de dados | dados pessoais, consentimento, segurança, LGPD/GDPR | — |
| LETRAMENTO | Letramento em IA | AI literacy, formação docente/discente, engenharia de prompts | — |
