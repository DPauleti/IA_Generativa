# =============================================================================
# Projeto: Análise de Recomendações Pedagógicas para o Uso de Inteligência
#          Artificial Generativa na Educação a Distância por meio de PLN e LLMs
# Disciplina: Inteligência Artificial - 7º N - Ciência da Computação
# Universidade Presbiteriana Mackenzie - Prof. Dr. Ivan Carlos Alcântara de Oliveira
# Integrante: Daniel Ribeiro Pauleti - RA 10723162
#
# Arquivo: src/coleta_openalex.py
# Síntese: coleta, via API pública do OpenAlex, os metadados (título, resumo em
#          índice invertido, palavras-chave, ano, idioma, tipo, DOI, fonte) das
#          publicações de 2023 a 2026 que tratam de IA generativa na educação a
#          distância / online. Salva os registros brutos em data/raw/.
#
# Histórico de alterações:
#   2026-09-25 - Daniel Ribeiro Pauleti - Versão inicial (consultas Q1, Q2, Q3).
#   2026-11-21 - Daniel Ribeiro Pauleti - coletar_licencas(): licença de cada publicação.
# =============================================================================
import json
import time
from datetime import date
from pathlib import Path

import requests

API = "https://api.openalex.org/works"
ANOS = "2023-2026"

# Termos de IA generativa (inglês)
GENAI_EN = ('("generative artificial intelligence" OR "generative AI" OR ChatGPT OR '
            '"large language model" OR "large language models" OR GPT-4)')

CONSULTAS = {
    # Q1: IA generativa + educação a distância (foco principal do projeto)
    "Q1": GENAI_EN + ' AND ("distance education" OR "distance learning" OR '
                     '"open and distance learning")',
    # Q2: IA generativa + aprendizagem online no ensino superior
    "Q2": GENAI_EN + ' AND ("online learning" OR "online education") AND "higher education"',
    # Q3: termos em português e espanhol
    "Q3": ('("inteligência artificial generativa" OR "IA generativa" OR ChatGPT OR '
           '"inteligencia artificial generativa") AND ("educação a distância" OR '
           '"ensino a distância" OR "educación a distancia" OR EaD)'),
}

# Minimização de dados: apenas os campos necessários à análise (sem autores).
CAMPOS = ",".join([
    "id", "doi", "title", "publication_year", "publication_date", "language",
    "type", "abstract_inverted_index", "keywords", "primary_topic",
    "primary_location", "cited_by_count", "open_access",
])


def coletar(consulta: str, por_pagina: int = 200) -> list[dict]:
    """Percorre todas as páginas da consulta usando paginação por cursor."""
    registros, cursor = [], "*"
    while cursor:
        params = {
            "filter": f"title_and_abstract.search:{consulta},publication_year:{ANOS}",
            "select": CAMPOS, "per_page": por_pagina, "cursor": cursor,
        }
        for tentativa in range(5):
            r = requests.get(API, params=params, timeout=60)
            if r.status_code == 200 and "results" in r.json():
                break
            time.sleep(2 ** tentativa)
        else:
            raise RuntimeError(f"Falha na API: {r.status_code} {r.text[:200]}")
        dados = r.json()
        registros.extend(dados["results"])
        cursor = dados["meta"].get("next_cursor") if dados["results"] else None
        time.sleep(0.2)
    return registros


def main(saida: Path = Path(__file__).resolve().parents[1] / "data" / "raw") -> None:
    saida.mkdir(parents=True, exist_ok=True)
    arquivo = saida / "openalex_bruto.jsonl"
    total = 0
    with arquivo.open("w", encoding="utf-8") as f:
        for nome, consulta in CONSULTAS.items():
            regs = coletar(consulta)
            print(f"{nome}: {len(regs)} registros")
            for reg in regs:
                reg["_consulta"] = nome
                reg["_data_coleta"] = date.today().isoformat()
                f.write(json.dumps(reg, ensure_ascii=False) + "\n")
            total += len(regs)
    (saida / "consultas.json").write_text(
        json.dumps({"anos": ANOS, "consultas": CONSULTAS, "data_coleta": date.today().isoformat()},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Total bruto (com duplicatas entre consultas): {total}")


if __name__ == "__main__":
    main()


def coletar_licencas(corpus_csv: Path = Path(__file__).resolve().parents[1] / "data/processed/corpus.csv") -> None:
    """Licença de cada publicação do corpus (melhor local de acesso aberto ou local
    primário), usada para documentar as condições de redistribuição dos resumos."""
    import pandas as pd
    ids = pd.read_csv(corpus_csv)["openalex_id"].tolist()
    linhas = []
    for i in range(0, len(ids), 50):
        r = requests.get(API, params={"filter": "openalex_id:" + "|".join(ids[i:i + 50]), "per_page": 50,
                                      "select": "id,primary_location,best_oa_location"}, timeout=60)
        for w in r.json()["results"]:
            pl, bo = w.get("primary_location") or {}, w.get("best_oa_location") or {}
            linhas.append({"openalex_id": w["id"].rsplit("/", 1)[-1],
                           "licenca": bo.get("license") or pl.get("license")})
        time.sleep(0.3)
    d = pd.DataFrame({"openalex_id": ids}).merge(pd.DataFrame(linhas), how="left")
    d["licenca"] = d["licenca"].fillna("nao_informada")
    d["licenca_cc"] = d["licenca"].str.startswith("cc")
    d.to_csv(corpus_csv.parent / "licencas.csv", index=False)
    print(d["licenca"].value_counts().to_string())
