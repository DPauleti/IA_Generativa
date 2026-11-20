# =============================================================================
# Projeto: Análise de Recomendações Pedagógicas para o Uso de Inteligência
#          Artificial Generativa na Educação a Distância por meio de PLN e LLMs
# Disciplina: Inteligência Artificial - 7º N - Ciência da Computação
# Universidade Presbiteriana Mackenzie - Prof. Dr. Ivan Carlos Alcântara de Oliveira
# Integrante: Daniel Ribeiro Pauleti - RA 10723162
#
# Arquivo: src/preparacao.py
# Síntese: funções de preparação do corpus: reconstrução dos resumos a partir do
#          índice invertido do OpenAlex, normalização de campos, remoção de
#          duplicatas e aplicação dos critérios de inclusão/exclusão.
#
# Histórico de alterações:
#   2026-09-25 - Daniel Ribeiro Pauleti - Versão inicial.
#   2026-09-25 - Daniel Ribeiro Pauleti - Detecção de idioma (langdetect), limite
#                máximo do resumo e critério de centralidade do tema.
# =============================================================================
import html
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd
from langdetect import DetectorFactory, detect

DetectorFactory.seed = 0  # torna a detecção de idioma determinística

RAIZ = Path(__file__).resolve().parents[1]

TIPOS_INCLUIDOS = {"article", "review", "conference-paper", "book-chapter", "preprint"}
IDIOMAS_INCLUIDOS = {"en", "pt", "es"}
MIN_PALAVRAS_RESUMO = 50
MAX_PALAVRAS_RESUMO = 1000  # acima disso o campo costuma conter texto integral/editorial

# Critério de relevância: o título/resumo deve citar IA generativa E um contexto
# pedagógico (ensino, aprendizagem, estudantes, avaliação etc.).
RE_GENAI = re.compile(
    r"generative (?:artificial intelligence|ai)|\bgen ?ai\b|chat ?gpt|\bgpt[- ]?[34o]|"
    r"large language model|\bllms?\b|chatbot|gemini|copilot|claude|"
    r"intelig[eê]ncia artificial generativa|\bia generativa|\biag\b", re.I)
RE_PEDAGOGIA = re.compile(
    r"learn|teach|student|pedagog|educat|course|assessment|curricul|tutor|"
    r"aprendiz|ensin|estudant|alun|pedag[oó]g|educa|docen|avalia|"
    r"aprendizaje|enseñanza|estudiante", re.I)


def reconstruir_resumo(indice_invertido: dict | None) -> str:
    """Reconstrói o texto do resumo a partir do índice invertido do OpenAlex
    ({palavra: [posições]}), ordenando as palavras pela posição."""
    if not indice_invertido:
        return ""
    posicoes = [(p, palavra) for palavra, lista in indice_invertido.items() for p in lista]
    texto = " ".join(palavra for _, palavra in sorted(posicoes))
    texto = html.unescape(re.sub(r"<[^>]+>", " ", texto))       # remove tags JATS/HTML
    return re.sub(r"\s+", " ", texto).strip()


def normalizar_titulo(titulo: str) -> str:
    t = unicodedata.normalize("NFKD", str(titulo or "")).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def carregar_bruto(caminho: Path = RAIZ / "data/raw/openalex_bruto.jsonl") -> pd.DataFrame:
    registros = [json.loads(l) for l in caminho.open(encoding="utf-8")]
    df = pd.DataFrame(registros)
    # consultas que recuperaram cada registro (antes de remover duplicatas)
    consultas = df.groupby("id")["_consulta"].apply(lambda s: "+".join(sorted(set(s))))
    df = df.drop_duplicates("id").copy()
    df["consultas"] = df["id"].map(consultas)
    return df


def estruturar(df: pd.DataFrame) -> pd.DataFrame:
    """Converte os campos aninhados do OpenAlex em colunas tabulares."""
    out = pd.DataFrame({
        "openalex_id": df["id"].str.replace("https://openalex.org/", "", regex=False),
        "doi": df["doi"].str.replace("https://doi.org/", "", regex=False).str.lower(),
        "titulo": df["title"].fillna("").map(lambda t: re.sub(r"\s+", " ", html.unescape(t)).strip()),
        "ano": df["publication_year"].astype(int),
        "data_publicacao": df["publication_date"],
        "idioma": df["language"],
        "tipo": df["type"],
        "resumo": df["abstract_inverted_index"].map(reconstruir_resumo),
        "palavras_chave": df["keywords"].map(
            lambda ks: "; ".join(k["display_name"] for k in (ks or []))),
        "topico_principal": df["primary_topic"].map(lambda t: (t or {}).get("display_name")),
        "area": df["primary_topic"].map(lambda t: ((t or {}).get("field") or {}).get("display_name")),
        "fonte": df["primary_location"].map(
            lambda l: (((l or {}).get("source")) or {}).get("display_name")),
        "citacoes": df["cited_by_count"].astype(int),
        "acesso_aberto": df["open_access"].map(lambda o: (o or {}).get("is_oa")),
        "status_oa": df["open_access"].map(lambda o: (o or {}).get("oa_status")),
        "consultas": df["consultas"],
    })
    # idioma ausente no OpenAlex: inferido com langdetect sobre título + resumo
    faltante = out["idioma"].isna() & (out["resumo"].str.len() > 0)
    out["idioma_origem"] = out["idioma"].notna().map({True: "openalex", False: "ausente"})
    out.loc[faltante, "idioma"] = (out.loc[faltante, "titulo"] + ". " + out.loc[faltante, "resumo"]).map(detect)
    out.loc[faltante, "idioma_origem"] = "langdetect"
    out["n_palavras_resumo"] = out["resumo"].str.split().str.len().fillna(0).astype(int)
    out["titulo_norm"] = out["titulo"].map(normalizar_titulo)
    return out.reset_index(drop=True)


def aplicar_criterios(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aplica, em sequência, os critérios de exclusão. Retorna o corpus final e
    um quadro (funil) com a quantidade de registros removida em cada etapa."""
    funil = [("Registros únicos (ID OpenAlex)", len(df))]

    def etapa(nome, mascara):
        nonlocal df
        df = df[mascara].copy()
        funil.append((nome, len(df)))

    # duplicatas por DOI e por título normalizado (mantém o mais citado)
    df = df.sort_values("citacoes", ascending=False)
    etapa("Remoção de duplicatas por DOI", df["doi"].isna() | ~df.duplicated("doi"))
    etapa("Remoção de duplicatas por título", ~df.duplicated("titulo_norm"))
    etapa("Tipo documental (artigo, revisão, evento, capítulo, preprint)", df["tipo"].isin(TIPOS_INCLUIDOS))
    etapa("Idioma (en, pt, es)", df["idioma"].isin(IDIOMAS_INCLUIDOS))
    etapa(f"Resumo válido ({MIN_PALAVRAS_RESUMO} a {MAX_PALAVRAS_RESUMO} palavras)",
          df["n_palavras_resumo"].between(MIN_PALAVRAS_RESUMO, MAX_PALAVRAS_RESUMO))
    texto = df["titulo"] + " " + df["resumo"]
    etapa("Relevância: menciona IA generativa e contexto pedagógico",
          texto.str.contains(RE_GENAI) & texto.str.contains(RE_PEDAGOGIA))
    # centralidade: IA generativa no título ou citada ao menos 2 vezes no resumo,
    # para descartar trabalhos em que o tema aparece apenas de passagem
    etapa("Centralidade: IA generativa no título ou >= 2 menções no resumo",
          df["titulo"].str.contains(RE_GENAI) | (df["resumo"].str.count(RE_GENAI) >= 2))
    df = df.sort_values(["ano", "openalex_id"]).drop(columns="titulo_norm").reset_index(drop=True)
    funil = pd.DataFrame(funil, columns=["etapa", "registros"])
    funil["removidos"] = (-funil["registros"].diff()).fillna(0).astype(int)
    return df, funil
