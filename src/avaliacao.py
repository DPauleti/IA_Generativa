# =============================================================================
# Projeto: Análise de Recomendações Pedagógicas para o Uso de Inteligência
#          Artificial Generativa na Educação a Distância por meio de PLN e LLMs
# Disciplina: Inteligência Artificial - 7º N - Ciência da Computação
# Universidade Presbiteriana Mackenzie - Prof. Dr. Ivan Carlos Alcântara de Oliveira
# Integrante: Daniel Ribeiro Pauleti - RA 10723162
#
# Arquivo: src/avaliacao.py
# Síntese: avaliação comparável de todos os métodos contra o padrão-ouro.
#          - Todos os métodos produzem a MESMA saída: vetor multirrótulo de 8
#            categorias + "há recomendação" por documento.
#          - M1 léxico: rótulos de data/processed/rotulos_lexico.csv.
#          - M2 K-means: cada grupo (k = 8, notebook 04) herda as categorias
#            presentes em >= 50% dos documentos de DESENVOLVIMENTO do grupo
#            (cluster-then-label); grupos sem documento de desenvolvimento não
#            recebem categoria. Só cobre resumos em inglês.
#          - M3 LLMs: arquivos data/resultados/llm/*.jsonl.
#          A comparação principal usa o subconjunto comum a todos os métodos
#          (teste, inglês); a complementar, todo o teste sem o K-means.
#
# Histórico de alterações:
#   2026-11-21 - Daniel Ribeiro Pauleti - Versão inicial.
# =============================================================================
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score, precision_recall_fscore_support

from categorias import CODIGOS, NOMES

RAIZ = Path(__file__).resolve().parents[1]
DIR_LLM = RAIZ / "data/resultados/llm"
LIMIAR_KMEANS = 0.5


# ---------------------------------------------------------------- carga
def padrao_ouro(particao: str) -> pd.DataFrame:
    return pd.read_csv(RAIZ / f"anotacao/padrao_ouro_{particao}.csv", encoding="utf-8-sig") \
        .set_index("openalex_id")[CODIGOS + ["tem_recomendacao"]].astype(int)


def pred_lexico() -> pd.DataFrame:
    d = pd.read_csv(RAIZ / "data/processed/rotulos_lexico.csv").set_index("openalex_id")[CODIGOS].astype(int)
    d["tem_recomendacao"] = d.max(axis=1)
    return d


def mapa_kmeans(limiar: float = LIMIAR_KMEANS) -> pd.DataFrame:
    """Categorias herdadas por grupo, a partir do padrão-ouro de desenvolvimento."""
    grupos = pd.read_csv(RAIZ / "data/processed/grupos_kmeans.csv").set_index("openalex_id")["grupo"]
    dev = padrao_ouro("desenvolvimento").join(grupos, how="inner")
    prev = dev.groupby("grupo")[CODIGOS + ["tem_recomendacao"]].mean()
    mapa = (prev >= limiar).astype(int).reindex(range(grupos.max() + 1), fill_value=0)
    mapa["docs_dev"] = dev.groupby("grupo").size().reindex(mapa.index, fill_value=0)
    return mapa


def pred_kmeans() -> pd.DataFrame:
    grupos = pd.read_csv(RAIZ / "data/processed/grupos_kmeans.csv").set_index("openalex_id")["grupo"]
    mapa = mapa_kmeans()
    d = mapa.loc[grupos.values, CODIGOS + ["tem_recomendacao"]]
    d.index = grupos.index
    return d


def pred_llm(arquivo: Path) -> pd.DataFrame:
    linhas = []
    for l in arquivo.open(encoding="utf-8"):
        r = json.loads(l)
        if r.get("erro"):
            continue  # documento sem resposta válida: tratado como ausente
        linhas.append({"openalex_id": r["openalex_id"], **r["rotulos"],
                       "tem_recomendacao": r["tem_recomendacao"]})
    return pd.DataFrame(linhas).drop_duplicates("openalex_id", keep="last").set_index("openalex_id")


def metodos_llm(particao_arquivo: str) -> dict[str, pd.DataFrame]:
    """Uma entrada por modelo × modo (execução 1) cujo arquivo cobre a partição."""
    saida = {}
    for f in sorted(DIR_LLM.glob(f"*_{particao_arquivo}.jsonl")):
        modelo, modo = f.stem.split("_")[:2]
        saida[f"M3 {modelo} {modo}"] = pred_llm(f)
    return saida


# ---------------------------------------------------------------- métricas
def metricas(ouro: pd.DataFrame, pred: pd.DataFrame) -> dict:
    y, p = ouro[CODIGOS].values, pred.loc[ouro.index, CODIGOS].values
    presentes = ouro[CODIGOS].sum().values > 0  # macro só sobre categorias com suporte
    pr, rc, f1, _ = precision_recall_fscore_support(y, p, average=None, zero_division=0)
    mi = precision_recall_fscore_support(y, p, average="micro", zero_division=0)
    tem_y, tem_p = ouro["tem_recomendacao"].values, pred.loc[ouro.index, "tem_recomendacao"].values
    return {
        "n": len(ouro),
        "P_micro": mi[0], "R_micro": mi[1], "F1_micro": mi[2],
        "F1_macro": f1[presentes].mean() if presentes.any() else np.nan,
        "hamming": (y != p).mean(),
        "acordo_exato": (y == p).all(axis=1).mean(),
        "F1_tem_rec": precision_recall_fscore_support(tem_y, tem_p, average="binary", zero_division=0)[2],
        "kappa_tem_rec": cohen_kappa_score(tem_y, tem_p) if len(set(tem_y) | set(tem_p)) > 1 else np.nan,
        "_por_categoria": pd.DataFrame({"P": pr, "R": rc, "F1": f1, "suporte": y.sum(axis=0),
                                        "preditos": p.sum(axis=0)}, index=CODIGOS),
    }


def ic_bootstrap(ouro, pred, chave="F1_micro", n=2000, semente=42) -> tuple[float, float]:
    rng = np.random.default_rng(semente)
    ids = ouro.index.values
    vals = []
    for _ in range(n):
        amostra = rng.choice(ids, size=len(ids), replace=True)
        o = ouro.loc[amostra].reset_index(drop=True)
        p = pred.loc[amostra].reset_index(drop=True)
        vals.append(metricas(o, p)[chave])
    return tuple(np.percentile(vals, [2.5, 97.5]))


def comparar(ouro: pd.DataFrame, metodos: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    linhas, por_cat = [], []
    for nome, pred in metodos.items():
        faltam = ouro.index.difference(pred.index)
        if len(faltam):
            raise ValueError(f"{nome}: sem predição para {len(faltam)} documentos")
        m = metricas(ouro, pred)
        lo, hi = ic_bootstrap(ouro, pred)
        cat = m.pop("_por_categoria")
        linhas.append({"metodo": nome, **m, "F1_micro_IC95": f"[{lo:.2f}; {hi:.2f}]"})
        por_cat.append(cat.assign(metodo=nome).reset_index(names="categoria"))
    return pd.DataFrame(linhas).set_index("metodo"), pd.concat(por_cat)


def estabilidade(a: pd.DataFrame, b: pd.DataFrame) -> dict:
    """Concordância entre duas execuções do mesmo modelo (não é avaliação contra o ouro)."""
    ids = a.index.intersection(b.index)
    x, y = a.loc[ids, CODIGOS].values, b.loc[ids, CODIGOS].values
    return {"n": len(ids), "acordo_exato_docs": (x == y).all(axis=1).mean(),
            "acordo_rotulos": (x == y).mean(),
            "acordo_tem_rec": (a.loc[ids, "tem_recomendacao"] == b.loc[ids, "tem_recomendacao"]).mean()}


def erros(ouro: pd.DataFrame, pred: pd.DataFrame, nome: str) -> pd.DataFrame:
    """Falsos positivos e negativos por documento e categoria (para análise de erros)."""
    linhas = []
    for i in ouro.index:
        for c in CODIGOS + ["tem_recomendacao"]:
            o, p = int(ouro.at[i, c]), int(pred.at[i, c])
            if o != p:
                linhas.append({"metodo": nome, "openalex_id": i, "rotulo": c,
                               "tipo": "FP" if p else "FN"})
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------- referência humana
def rotulos_anotador(anotador: str, particao: str) -> pd.DataFrame:
    """Rótulos independentes (antes do consenso) de um anotador."""
    f = RAIZ / f"anotacao/rotulos/independente/{particao}/rotulos_{anotador}.csv"
    return pd.read_csv(f, encoding="utf-8-sig").set_index("openalex_id")[CODIGOS + ["tem_recomendacao"]].astype(int)


def kappa_medio(a: pd.DataFrame, b: pd.DataFrame) -> float:
    ks = [cohen_kappa_score(a[c], b[c]) for c in CODIGOS if len(set(a[c]) | set(b[c])) > 1]
    return float(np.mean(ks)) if ks else np.nan


def contra_anotadores(particao: str, metodos: dict[str, pd.DataFrame], ids=None) -> pd.DataFrame:
    """Concordância de cada método com A1 e com A2, ao lado da concordância A1 × A2
    (teto humano). Métrica simétrica: F1 micro e kappa médio por categoria."""
    a1, a2 = rotulos_anotador("A1", particao), rotulos_anotador("A2", particao)
    ids = a1.index.intersection(a2.index) if ids is None else ids
    linhas = [{"comparacao": "A1 × A2 (humano × humano)",
               "F1_micro": metricas(a1.loc[ids], a2.loc[ids])["F1_micro"],
               "kappa_medio": kappa_medio(a1.loc[ids], a2.loc[ids])}]
    for nome, pred in metodos.items():
        for an, ref in [("A1", a1), ("A2", a2)]:
            linhas.append({"comparacao": f"{nome} × {an}",
                           "F1_micro": metricas(ref.loc[ids], pred.loc[ids])["F1_micro"],
                           "kappa_medio": kappa_medio(ref.loc[ids], pred.loc[ids])})
    return pd.DataFrame(linhas).set_index("comparacao")
