# Análise de Recomendações Pedagógicas para o Uso de Inteligência Artificial Generativa na Educação a Distância por meio de PLN e LLMs

Projeto da disciplina **Inteligência Artificial** — 7º semestre N, Ciência da Computação,
Universidade Presbiteriana Mackenzie. Prof. Dr. Ivan Carlos Alcântara de Oliveira.
ODS 4 — Educação de Qualidade.

| Integrante | RA | E-mail |
|---|---|---|
| Daniel Ribeiro Pauleti | 10723162 | 10723162@mackenzista.com.br |

## Objetivo
Identificar e categorizar, com PLN e LLMs, as **recomendações pedagógicas** sobre o uso de IA
generativa presentes em publicações científicas (2023–2026) sobre educação a distância/online,
comparando um baseline léxico, TF-IDF + agrupamento (K-means) e a classificação por LLMs,
validados por anotação manual.

## Estrutura
```
artigo/        Artigo parcial (N1) em .docx e .pdf
data/          Dataset (bruto e processado) + descrição (data/README.md)
notebooks/     01 coleta · 02 preparação · 03 análise exploratória · 04 resultados parciais
src/           coleta_openalex.py · preparacao.py · categorias.py (livro de códigos + baseline léxico)
anotacao/      Protocolo de anotação e amostra estratificada (60 publicações) a anotar
prompts/       Prompt de classificação por LLM (v1)
figuras/       Figuras geradas pelos notebooks
```

## Como reproduzir
```bash
python -m venv .venv && .venv\Scripts\activate      # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
jupyter nbconvert --to notebook --execute --inplace notebooks/*.ipynb
```
O notebook 01 usa, por padrão, o arquivo bruto versionado (`COLETAR = False`); com
`COLETAR = True` a coleta no OpenAlex é refeita (os resultados podem variar com a
atualização contínua do catálogo).

## Estado atual (N1)
- [x] Coleta (471 registros únicos) e preparação do corpus (208 publicações)
- [x] Análise exploratória
- [x] Livro de códigos (8 categorias) e baseline léxico explicável
- [x] TF-IDF + K-means (baseline não supervisionado)
- [x] Amostra estratificada para anotação e prompt v1
- [ ] Anotação manual (padrão-ouro) e confiabilidade (kappa)
- [ ] Classificação por 2 LLMs (zero-shot e few-shot) — N2
- [ ] Comparação dos métodos, métricas e análise de erros — N2

## Histórico de alterações
| Data | Autor | Descrição |
|---|---|---|
| 2026-09-25 | Daniel Ribeiro Pauleti | Criação do repositório: coleta, preparação, EDA, baselines e artigo parcial (N1). |

## Licença e uso de dados
Metadados do OpenAlex sob CC0. Os resumos pertencem aos autores/editoras e são usados para
fins acadêmicos, com citação via DOI. Nenhum dado pessoal de participantes é coletado.
