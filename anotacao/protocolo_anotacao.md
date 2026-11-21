<!--
Projeto: Análise de Recomendações Pedagógicas para o Uso de Inteligência Artificial
         Generativa na Educação a Distância por meio de PLN e LLMs
Integrante: Daniel Ribeiro Pauleti - RA 10723162
Arquivo: anotacao/protocolo_anotacao.md
Síntese: livro de códigos e protocolo de anotação manual (padrão-ouro).
Histórico de alterações:
  2026-09-25 - Daniel Ribeiro Pauleti - Versão inicial.
  2026-11-21 - Daniel Ribeiro Pauleti - Registro da execução do desenvolvimento e v1.2.
  2026-11-20 - Daniel Ribeiro Pauleti - Protocolo com dois anotadores independentes,
               fases (desenvolvimento → consenso → congelamento → teste), distinção
               entre concordância e estabilidade e página de anotação.
-->

# Protocolo de anotação manual (padrão-ouro)

## Amostra
- `amostra_anotacao.csv`: **60 publicações** (≈29% do corpus de 208), sorteadas com
  estratificação por ano × idioma (`random_state = 42`) em
  `notebooks/04_baseline_lexico_tfidf.ipynb`.
- **Desenvolvimento (20):** calibração do livro de códigos, ajuste do prompt e escolha dos
  exemplos few-shot e mapeamento dos grupos do K-means.
- **Teste (40):** usado **somente** na avaliação final. Nenhum ajuste de léxico, prompt,
  exemplos ou mapeamento é feito depois de ver os rótulos do teste.

## Anotadores
| Código | Quem | Partições |
|---|---|---|
| A1 | Integrante (Daniel Ribeiro Pauleti) | desenvolvimento + teste |
| A2 | Segundo anotador, independente | desenvolvimento + teste |

Os anotadores trabalham **separadamente**, sem ver as anotações um do outro nem qualquer
saída automática (léxico, K-means ou LLM). A página de anotação não mostra essas saídas.

## Fases
1. **Congelamento prévio.** O léxico (`src/categorias.py`), o livro de códigos v1.1 e o
   prompt v1 são versionados no Git **antes** de qualquer anotação.
2. **Desenvolvimento.** A1 e A2 anotam as 20 publicações de desenvolvimento.
3. **Consenso.** `python src/concordancia.py desenvolvimento A1 A2` gera o kappa por
   categoria e `anotacao/consenso/divergencias_desenvolvimento.csv`. Os anotadores discutem
   cada divergência, registram a decisão (`consenso`) e a justificativa. Regras de decisão
   novas entram no livro de códigos (v1.2), e a página é regenerada.
4. **Congelamento do livro de códigos.** A versão resultante é registrada em commit antes
   do teste.
5. **Teste.** A1 e A2 anotam as 40 publicações de teste de forma independente. O kappa
   **entre anotadores** é calculado sobre essa anotação independente (antes do consenso).
6. **Padrão-ouro.** As divergências do teste são resolvidas por consenso
   (`--padrao-ouro`), gerando `anotacao/padrao_ouro_teste.csv`, que é a referência de
   avaliação de todos os métodos.

## Registro da execução
- **Desenvolvimento (v1.1):** κ médio entre A1 e A2 = 0,01; acordo exato em 25% dos
  documentos (`consenso/pauta_consenso_desenvolvimento.md`). Causa principal: aplicação
  diferente da regra "recomendação × menção".
- **Consenso:** 33 divergências resolvidas (`consenso/divergencias_desenvolvimento.xlsx`);
  padrão-ouro em `padrao_ouro_desenvolvimento.csv`. Regras R1, R2, R4, R5 e R6 aprovadas;
  R3 rejeitada. Livro de códigos atualizado para **v1.2**.
- **Calibração:** não realizada, por restrição de prazo. Consequência: não há medida de
  concordância com a v1.2 antes do teste; o kappa do teste é a primeira medida com as
  novas regras (limitação a relatar no artigo).

## Concordância × estabilidade
- **Concordância entre anotadores** (A1 × A2, kappa de Cohen por categoria): mede se o
  livro de códigos é aplicado da mesma forma por pessoas diferentes. É a medida principal
  de confiabilidade. Meta: κ ≥ 0,61 (concordância substancial, Landis e Koch, 1977).
- **Estabilidade intra-anotador** (opcional): o mesmo anotador reanota a partição de teste
  após ≥ 10 dias, com o código `A1R`, e calcula-se `python src/concordancia.py teste A1 A1R`.
  Mede consistência ao longo do tempo, **não** concordância, e é relatada separadamente.

## Como anotar
1. Abrir `anotacao/pagina_anotacao.html` em qualquer navegador (funciona offline) e
   informar o código do anotador.
2. Ler título e resumo. Para cada categoria, marcar **somente** se o texto **recomenda,
   propõe, orienta ou conclui** algo sobre ela. Mencionar o tema não basta.
3. Responder se há recomendação pedagógica explícita. Se houver recomendação fora das 8
   categorias, descrevê-la em Observações.
4. Clicar em **Concluir e próxima** (Ctrl+Enter). O progresso fica salvo no navegador.
5. Ao fim de cada sessão, **Exportar CSV** e salvar em `anotacao/rotulos/`
   (`rotulos_<anotador>_<data>.csv`). Em outro computador, use **Importar CSV**.

## Categorias (livro de códigos v1.2 — regras de decisão em `src/categorias.py` e na página)
| Código | Categoria | Inclui | Não inclui |
|---|---|---|---|
| APR_ATIVA | Aprendizagem ativa | Tutoria, feedback formativo, prática guiada, personalização, autorregulação com IA como parceira de estudo | IA usada só pelo professor para gerar conteúdo; menção genérica a engajamento |
| AUTORIA | Autoria e integridade acadêmica | Plágio, declaração do uso, políticas de integridade, detectores, autoria | Ética genérica sem relação com autoria |
| PENS_CRITICO | Pensamento crítico | Argumentação, análise, reflexão; evitar dependência | Criatividade sem relação com raciocínio crítico |
| VERIFICACAO | Verificação das respostas | Checar exatidão, alucinações, fontes, confiabilidade | Desempenho do modelo em provas sem orientação ao usuário |
| ETICA | Ética e uso responsável | Vieses, equidade, transparência, uso responsável, impactos sociais | Privacidade e integridade acadêmica, salvo se também tratar de ética ampla |
| AVALIACAO | Avaliação da aprendizagem | Redesenho de avaliações, regras de uso da IA em avaliações, correção/feedback com IA | Avaliar o próprio estudo, a ferramenta ou um programa |
| PRIVACIDADE | Privacidade e proteção de dados | Dados pessoais, consentimento, segurança, LGPD/GDPR | — |
| LETRAMENTO | Letramento em IA | AI literacy, formação de estudantes e professores, engenharia de prompts | Competência digital genérica sem relação com IA |
