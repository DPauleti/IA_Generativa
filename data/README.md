# Dataset — Publicações sobre IA generativa na educação a distância (OpenAlex, 2023–2026)

**Fonte:** [OpenAlex](https://openalex.org/) — catálogo aberto de publicações científicas,
dados sob licença **CC0** (domínio público). Coleta via API pública em **25/09/2026**
(`src/coleta_openalex.py`). Os textos pertencem aos respectivos autores/editoras; o
dataset contém apenas metadados e resumos, usados para fins de pesquisa, sempre com o DOI
para citação da obra original.

## Consultas (aplicadas a título + resumo, anos 2023–2026)
| Consulta | Termos | Registros |
|---|---|---|
| Q1 | IA generativa (*generative AI*, ChatGPT, *large language model(s)*, GPT-4) **E** (*distance education*, *distance learning*, *open and distance learning*) | 256 |
| Q2 | IA generativa **E** (*online learning*, *online education*) **E** *higher education* | 167 |
| Q3 | Termos em português/espanhol (IA generativa, ChatGPT **E** educação/ensino a distância, EaD, *educación a distancia*) | 57 |

## Funil de seleção (`processed/funil_selecao.csv`)
| Etapa | Registros |
|---|---|
| Registros únicos (ID OpenAlex) | 471 |
| Remoção de duplicatas por DOI | 470 |
| Remoção de duplicatas por título normalizado | 424 |
| Tipo documental (artigo, revisão, evento, capítulo, preprint) | 375 |
| Idioma (en, pt, es) — idioma ausente inferido com *langdetect* | 357 |
| Resumo com 50 a 1000 palavras | 309 |
| Menciona IA generativa **e** contexto pedagógico | 307 |
| Centralidade: IA generativa no título ou ≥ 2 menções no resumo | **208** |

## Arquivos
| Arquivo | Descrição |
|---|---|
| `raw/openalex_bruto.jsonl` | Resposta bruta da API (1 registro JSON por linha; inclui `_consulta`). Resumo em **índice invertido**. |
| `raw/consultas.json` | Consultas, período e data da coleta. |
| `processed/corpus.csv` | **Corpus final (208 publicações)**, com resumo reconstruído. |
| `processed/funil_selecao.csv` | Quantidade de registros em cada etapa de seleção. |
| `processed/rotulos_lexico.csv` | Rótulos do baseline léxico (8 categorias) e termos de evidência. |
| `processed/grupos_kmeans.csv` | Grupo K-means (k = 8) de cada resumo em inglês. |
| `processed/licencas.csv` | Licença de cada publicação segundo o OpenAlex (`coletar_licencas()` em `src/coleta_openalex.py`). |
| `resultados/llm/*.jsonl` | Respostas dos LLMs (uma linha por publicação): rótulos, evidências aceitas/rejeitadas, resposta bruta, tokens e tempo. `historico/` guarda as execuções do prompt v1.2. |
| `resultados/avaliacao/*.csv` | Tabelas da avaliação final (notebook 05): comparação dos métodos, concordância com os anotadores, operação dos LLMs, erros, panorama por ano e taxonomia. |

## Dicionário de dados — `processed/corpus.csv`
| Coluna | Descrição |
|---|---|
| `openalex_id` | Identificador OpenAlex (ex.: W4377094181) |
| `doi` | DOI (6 registros sem DOI) |
| `titulo` | Título da publicação |
| `ano`, `data_publicacao` | Ano e data de publicação |
| `idioma` | `en`, `pt` ou `es` |
| `idioma_origem` | `openalex` (informado) ou `langdetect` (inferido) |
| `tipo` | article, conference-paper, book-chapter, preprint, review |
| `resumo` | Resumo reconstruído a partir do índice invertido |
| `n_palavras_resumo` | Nº de palavras do resumo |
| `palavras_chave` | Palavras-chave atribuídas pelo OpenAlex (separadas por `; `) |
| `topico_principal`, `area` | Tópico e área principal (classificação do OpenAlex) |
| `fonte` | Periódico/evento/repositório (38 registros sem fonte) |
| `citacoes` | Nº de citações no OpenAlex na data da coleta |
| `acesso_aberto`, `status_oa` | Situação de acesso aberto |
| `consultas` | Consulta(s) que recuperaram o registro |
| `texto` | `titulo + ". " + resumo` (entrada dos modelos) |

**Dados pessoais:** nomes de autores e afiliações **não** foram coletados (minimização de dados).

## Condições de uso e redistribuição dos resumos

- **Metadados** (identificadores, DOI, título, ano, idioma, tipo, fonte, palavras-chave,
  tópicos, citações): obtidos do OpenAlex sob licença **CC0** (domínio público).
- **Resumos:** a licença CC0 do OpenAlex **não** se estende ao texto dos resumos, cujos
  direitos pertencem aos autores e editoras. O OpenAlex distribui os resumos como índice
  invertido; este repositório os reconstrói (`src/preparacao.py`). Situação das 208
  publicações (`processed/licencas.csv`): **131 (63%) sob licenças Creative Commons**
  (75 CC BY, 10 CC BY-SA, 2 CC BY-ND, 13 CC BY-NC, 11 CC BY-NC-SA, 20 CC BY-NC-ND),
  3 com outra licença aberta e **74 sem licença informada**.
- **Como os resumos são usados e redistribuídos aqui:** exclusivamente para fins
  acadêmicos, não comerciais e de reprodutibilidade desta pesquisa, sempre com o DOI da obra
  original, sem alteração do texto e sem uso para treinar modelos. Para as publicações sob
  licença CC, a redistribuição segue os termos de cada licença (atribuição pelo DOI; as
  cláusulas NC e ND são respeitadas, pois não há uso comercial nem obra derivada do texto).
  Para as publicações sem licença informada, os resumos são mantidos apenas como trechos
  necessários à verificação dos resultados, com base no uso para fins de estudo e pesquisa
  com citação da fonte (Lei nº 9.610/1998, art. 46).
- **Remoção:** titulares de direitos podem solicitar a retirada de um resumo abrindo uma
  *issue* no repositório; o texto será removido e poderá ser reconstruído localmente pela API
  do OpenAlex com `src/coleta_openalex.py` e `src/preparacao.py`.
