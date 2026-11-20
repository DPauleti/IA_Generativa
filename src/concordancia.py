# =============================================================================
# Projeto: Análise de Recomendações Pedagógicas para o Uso de Inteligência
#          Artificial Generativa na Educação a Distância por meio de PLN e LLMs
# Disciplina: Inteligência Artificial - 7º N - Ciência da Computação
# Universidade Presbiteriana Mackenzie - Prof. Dr. Ivan Carlos Alcântara de Oliveira
# Integrante: Daniel Ribeiro Pauleti - RA 10723162
#
# Arquivo: src/concordancia.py
# Síntese: lê os CSVs exportados pela página de anotação (anotacao/rotulos/),
#          calcula a concordância ENTRE anotadores (kappa de Cohen e % de acordo
#          por categoria), gera a planilha de divergências para a reunião de
#          consenso e monta o padrão-ouro a partir dos acordos + consenso.
#
# Uso:
#   python src/concordancia.py desenvolvimento A1 A2   # relatório + divergências
#   python src/concordancia.py teste A1 A2
#   python src/concordancia.py teste A1 A2 --padrao-ouro   # após preencher o consenso
#
# Histórico de alterações:
#   2026-11-20 - Daniel Ribeiro Pauleti - Versão inicial.
# =============================================================================
import argparse
from pathlib import Path

import pandas as pd
from sklearn.metrics import cohen_kappa_score

from categorias import CODIGOS, NOMES

RAIZ = Path(__file__).resolve().parents[1]
DIR_ROTULOS = RAIZ / "anotacao/rotulos"
DIR_CONSENSO = RAIZ / "anotacao/consenso"
ROTULOS = CODIGOS + ["tem_recomendacao"]


def carregar(anotador: str, particao: str) -> pd.DataFrame:
    """Última versão concluída de cada documento do anotador na partição."""
    arquivos = sorted(DIR_ROTULOS.glob(f"rotulos_{anotador}_*.csv"))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum CSV de {anotador} em {DIR_ROTULOS}")
    df = pd.concat([pd.read_csv(a, encoding="utf-8-sig", dtype={"observacoes": str}) for a in arquivos])
    df = df[(df["particao"] == particao) & (df["concluido"] == 1)]
    df = df.sort_values("atualizado_em").drop_duplicates("openalex_id", keep="last")
    return df.set_index("openalex_id")


def kappa(a: pd.Series, b: pd.Series) -> float:
    # kappa é indefinido quando os dois anotadores usam um único valor
    if a.nunique() == 1 and b.nunique() == 1:
        return float("nan")
    return cohen_kappa_score(a, b)


def relatorio(a: pd.DataFrame, b: pd.DataFrame, nome_a: str, nome_b: str) -> pd.DataFrame:
    ids = a.index.intersection(b.index)
    linhas = []
    for c in ROTULOS:
        x, y = a.loc[ids, c].astype(int), b.loc[ids, c].astype(int)
        linhas.append({"rotulo": c, "categoria": NOMES.get(c, "Há recomendação"), "n": len(ids),
                       "acordo_%": round(100 * (x == y).mean(), 1), "kappa": round(kappa(x, y), 3),
                       f"prev_{nome_a}_%": round(100 * x.mean(), 1), f"prev_{nome_b}_%": round(100 * y.mean(), 1)})
    rel = pd.DataFrame(linhas)
    exato = (a.loc[ids, CODIGOS].astype(int) == b.loc[ids, CODIGOS].astype(int)).all(axis=1).mean()
    print(f"Documentos anotados por ambos: {len(ids)} | acordo exato nas 8 categorias: {100 * exato:.1f}%")
    print(f"Kappa médio (8 categorias, ignorando indefinidos): {rel.iloc[:8]['kappa'].mean():.3f}")
    return rel


def divergencias(a, b, nome_a, nome_b) -> pd.DataFrame:
    ids = a.index.intersection(b.index)
    titulos = pd.read_csv(RAIZ / "anotacao/amostra_anotacao.csv", encoding="utf-8-sig").set_index("openalex_id")["titulo"]
    linhas = []
    for i in ids:
        for c in ROTULOS:
            if int(a.at[i, c]) != int(b.at[i, c]):
                linhas.append({"openalex_id": i, "titulo": titulos.get(i, ""), "rotulo": c,
                               nome_a: int(a.at[i, c]), nome_b: int(b.at[i, c]),
                               f"obs_{nome_a}": a.at[i, "observacoes"], f"obs_{nome_b}": b.at[i, "observacoes"],
                               "consenso": "", "justificativa": ""})
    return pd.DataFrame(linhas)


def padrao_ouro(a, b, particao, nome_a, nome_b) -> pd.DataFrame:
    """Acordos entre os anotadores + decisões de consenso preenchidas."""
    ids = a.index.intersection(b.index)
    ouro = a.loc[ids, ROTULOS].astype(int).copy()
    arq = DIR_CONSENSO / f"divergencias_{particao}.csv"
    cons = pd.read_csv(arq, encoding="utf-8-sig")
    faltam = cons["consenso"].isna().sum()
    if faltam:
        raise ValueError(f"{faltam} divergências sem consenso em {arq}")
    for _, r in cons.iterrows():
        ouro.at[r["openalex_id"], r["rotulo"]] = int(r["consenso"])
    ouro["tem_recomendacao"] = ouro[["tem_recomendacao"]].join(ouro[CODIGOS].max(axis=1).rename("m")).max(axis=1)
    ouro.insert(0, "particao", particao)
    return ouro.reset_index()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("particao", choices=["desenvolvimento", "teste"])
    ap.add_argument("anotador_a"); ap.add_argument("anotador_b")
    ap.add_argument("--padrao-ouro", action="store_true")
    args = ap.parse_args()
    a, b = carregar(args.anotador_a, args.particao), carregar(args.anotador_b, args.particao)
    DIR_CONSENSO.mkdir(parents=True, exist_ok=True)
    if args.padrao_ouro:
        ouro = padrao_ouro(a, b, args.particao, args.anotador_a, args.anotador_b)
        saida = RAIZ / f"anotacao/padrao_ouro_{args.particao}.csv"
        ouro.to_csv(saida, index=False, encoding="utf-8-sig")
        print(f"Padrão-ouro salvo em {saida} ({len(ouro)} documentos)")
        return
    rel = relatorio(a, b, args.anotador_a, args.anotador_b)
    print(rel.to_string(index=False))
    rel.to_csv(DIR_CONSENSO / f"concordancia_{args.particao}.csv", index=False, encoding="utf-8-sig")
    div = divergencias(a, b, args.anotador_a, args.anotador_b)
    arq = DIR_CONSENSO / f"divergencias_{args.particao}.csv"
    div.to_csv(arq, index=False, encoding="utf-8-sig")
    print(f"\n{len(div)} divergências salvas em {arq} (preencha 'consenso' com 0/1 e a justificativa).")


if __name__ == "__main__":
    main()
