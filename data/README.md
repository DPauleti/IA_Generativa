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
