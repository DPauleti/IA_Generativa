# Análise de Recomendações Pedagógicas para o Uso de Inteligência Artificial Generativa na Educação a Distância por meio de PLN e LLMs

Projeto da disciplina **Inteligência Artificial** — 7º semestre N, Ciência da Computação,
Universidade Presbiteriana Mackenzie. Prof. Dr. Ivan Carlos Alcântara de Oliveira.
ODS 4 — Educação de Qualidade.

| Integrante | RA | E-mail |
|---|---|---|
| Daniel Ribeiro Pauleti | 10723162 | 10723162@mackenzista.com.br |

- **Artigo final (N2):** [`artigo/Artigo_Final_N2_IA.pdf`](artigo/Artigo_Final_N2_IA.pdf)
- **Vídeo de apresentação:** [inserir o endereço do vídeo no YouTube]

## Objetivo
Identificar e categorizar, com PLN e LLMs, as **recomendações pedagógicas** sobre o uso de IA
generativa presentes em publicações científicas (2023–2026) sobre educação a distância e online,
comparando um baseline léxico, TF-IDF + K-means e dois LLMs (Claude Haiku 4.5 e Llama 3.1 8B,
zero-shot e few-shot), validados por dois anotadores humanos.

## Principais resultados
| Método (teste, inglês, n = 36) | F1 micro | IC 95% |
|---|---|---|
| Llama 3.1 8B few-shot | **0,47** | [0,38; 0,56] |
| Claude Haiku 4.5 few-shot | 0,40 | [0,30; 0,50] |
| TF-IDF + K-means | 0,38 | [0,19; 0,55] |
| Claude Haiku 4.5 zero-shot | 0,36 | [0,26; 0,45] |
| Léxico | 0,33 | [0,24; 0,42] |
| Llama 3.1 8B zero-shot | 0,00 | — |

- Concordância entre os anotadores muito baixa (kappa médio 0,06): o limite principal do estudo.
- Os LLMs few-shot concordaram com cada anotador mais do que os anotadores entre si.
- Todos os métodos superestimam categorias minoritárias (alta revocação, baixa precisão).
- Aprendizagem ativa é a recomendação predominante (45% no padrão-ouro), seguida de ética.
- 832 respostas de LLM válidas; 1,4–2,8% das categorias descartadas por evidência inventada;
  custo total do Claude ≈ US$ 2.

## Estrutura
```
artigo/        Artigo parcial (N1) e artigo final (N2), em .docx e .pdf
data/          raw/ (OpenAlex bruto) · processed/ (corpus, funil, licenças, léxico, K-means)
               resultados/llm/ (respostas dos LLMs) · resultados/avaliacao/ (tabelas finais)
               README.md: dicionário de dados, licenças e condições de uso dos resumos
notebooks/     01 coleta · 02 preparação · 03 análise exploratória · 04 baselines · 05 avaliação
src/           coleta_openalex.py   coleta e licenças (API OpenAlex)
               preparacao.py        reconstrução dos resumos e critérios de seleção
               categorias.py        livro de códigos v1.2 (regras, critérios) + baseline léxico
               gerar_pagina_anotacao.py · concordancia.py (kappa, divergências, padrão-ouro)
               classificacao_llm.py (M3: prompt, saída estruturada, validação de evidências)
               avaliacao.py         métricas comparáveis, bootstrap, comparação com anotadores
               figura_fluxo.py      figura do fluxo da solução
anotacao/      protocolo, amostra (60), pagina_anotacao.html, rotulos/ (exportações e cópias
               independentes congeladas), consenso/ (divergências, pauta), padrao_ouro_*.csv
prompts/       prompt v1 (N1) e v1.3 (final), exemplos few-shot, CONGELAMENTO_TESTE.md (hashes)
figuras/       figuras geradas pelos notebooks e scripts
```

## Como reproduzir
Requisitos: Python 3.11+, [Ollama](https://ollama.com) (para o Llama) e uma chave da API da
Anthropic (para o Claude).

```bash
python -m venv .venv && .venv\Scripts\activate      # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

1. **Análises sem LLM** (dados, EDA, baselines e avaliação a partir dos resultados versionados):
   ```bash
   jupyter nbconvert --to notebook --execute --inplace notebooks/*.ipynb
   ```
   O notebook 01 usa o arquivo bruto versionado (`COLETAR = False`); com `COLETAR = True` a
   coleta é refeita (o catálogo muda com o tempo).
2. **Refazer as execuções dos LLMs** (opcional; os resultados já estão em `data/resultados/llm`):
   ```bash
   ollama pull llama3.1:8b
   echo ANTHROPIC_API_KEY=sua-chave > .env           # o .env não é versionado
   python src/classificacao_llm.py --modelo llama3.1:8b --modo few-shot --particao corpus
   python src/classificacao_llm.py --modelo claude-haiku-4-5 --modo few-shot --particao corpus
   ```
   As execuções são retomáveis (documentos já processados são pulados). O Claude não é
   determinístico: os rótulos podem variar levemente (98% de concordância entre execuções).
3. **Anotação e concordância:** abrir `anotacao/pagina_anotacao.html` no navegador; depois
   `python src/concordancia.py teste A1 A2` (kappa e divergências) e
   `python src/concordancia.py teste A1 A2 --padrao-ouro` (após o consenso).

## Histórico de alterações
| Data | Autor | Descrição |
|---|---|---|
| 2026-09-25 | Daniel Ribeiro Pauleti | Criação do repositório: coleta, preparação, EDA, baselines e artigo parcial (N1). |
| 2026-11-20 | Daniel Ribeiro Pauleti | Codebook v1.1 (critérios de inclusão/exclusão), página de anotação, protocolo com dois anotadores e script de concordância. |
| 2026-11-20 | Daniel Ribeiro Pauleti | Pipeline de classificação por LLMs (prompt v1.1, saída estruturada, validação de evidências). |
| 2026-11-21 | Daniel Ribeiro Pauleti | Consenso do desenvolvimento e codebook v1.2; prompt v1.3 e exemplos few-shot; congelamento antes do teste. |
| 2026-11-21 | Daniel Ribeiro Pauleti | Anotação e consenso do teste; execuções no corpus; avaliação final (notebook 05); licenças; artigo final (N2). |

## Licença e uso de dados
Metadados do OpenAlex sob CC0. Os resumos pertencem aos autores e editoras: 63% das publicações
estão sob licenças Creative Commons e as demais são usadas apenas para fins acadêmicos e de
reprodutibilidade, com citação via DOI e possibilidade de remoção a pedido. Detalhes em
[`data/README.md`](data/README.md). Nenhum dado pessoal de participantes é coletado.
