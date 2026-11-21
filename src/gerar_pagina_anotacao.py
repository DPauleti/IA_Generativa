# =============================================================================
# Projeto: Análise de Recomendações Pedagógicas para o Uso de Inteligência
#          Artificial Generativa na Educação a Distância por meio de PLN e LLMs
# Disciplina: Inteligência Artificial - 7º N - Ciência da Computação
# Universidade Presbiteriana Mackenzie - Prof. Dr. Ivan Carlos Alcântara de Oliveira
# Integrante: Daniel Ribeiro Pauleti - RA 10723162
#
# Arquivo: src/gerar_pagina_anotacao.py
# Síntese: gera anotacao/pagina_anotacao.html (arquivo único, funciona offline)
#          a partir da amostra estratificada e do livro de códigos. A página não
#          exibe nenhuma saída automática (léxico, K-means ou LLM), para que a
#          anotação seja cega.
#
# Histórico de alterações:
#   2026-11-20 - Daniel Ribeiro Pauleti - Versão inicial.
#   2026-11-21 - Daniel Ribeiro Pauleti - Inclui as regras de decisão (codebook v1.2).
# =============================================================================
import html
import json
from pathlib import Path

import pandas as pd

from categorias import CATEGORIAS, CRITERIOS, REGRAS, VERSAO_CODEBOOK

RAIZ = Path(__file__).resolve().parents[1]


def main() -> None:
    amostra = pd.read_csv(RAIZ / "anotacao/amostra_anotacao.csv", encoding="utf-8-sig", dtype=str)
    # desenvolvimento primeiro, mantendo a ordem sorteada dentro de cada partição
    amostra["ordem_p"] = amostra["particao"].map({"desenvolvimento": 0, "teste": 1})
    amostra = amostra.sort_values("ordem_p", kind="stable")
    dados = amostra[["openalex_id", "doi", "ano", "idioma", "particao", "titulo", "resumo"]] \
        .fillna("").to_dict("records")
    codebook = [{"codigo": c, "nome": html.escape(nome), "definicao": html.escape(defin),
                 "inclui": html.escape(CRITERIOS[c][0]), "nao_inclui": html.escape(CRITERIOS[c][1])}
                for c, (nome, defin, _) in CATEGORIAS.items()]

    regras = [{"id": i, "titulo": html.escape(t), "texto": html.escape(x)} for i, t, x in REGRAS]

    def js(obj):  # JSON seguro dentro de <script>
        return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")

    modelo = (RAIZ / "anotacao/ferramenta/template.html").read_text(encoding="utf-8")
    pagina = (modelo.replace("/*__DADOS__*/[]", js(dados))
                    .replace("/*__CODEBOOK__*/[]", js(codebook))
                    .replace("/*__REGRAS__*/[]", js(regras))
                    .replace("/*__VERSAO__*/", VERSAO_CODEBOOK))
    saida = RAIZ / "anotacao/pagina_anotacao.html"
    saida.write_text(pagina, encoding="utf-8")
    print(f"Gerado: {saida} ({len(dados)} documentos, codebook v{VERSAO_CODEBOOK})")


if __name__ == "__main__":
    main()
