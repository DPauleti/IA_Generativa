# =============================================================================
# Projeto: Análise de Recomendações Pedagógicas para o Uso de Inteligência
#          Artificial Generativa na Educação a Distância por meio de PLN e LLMs
# Disciplina: Inteligência Artificial - 7º N - Ciência da Computação
# Universidade Presbiteriana Mackenzie - Prof. Dr. Ivan Carlos Alcântara de Oliveira
# Integrante: Daniel Ribeiro Pauleti - RA 10723162
#
# Arquivo: src/figura_fluxo.py
# Síntese: desenha a figura com o fluxo (arquitetura) da solução usada no artigo
#          (figuras/fig0_fluxo_solucao.png).
#
# Histórico de alterações:
#   2026-11-21 - Daniel Ribeiro Pauleti - Versão inicial.
# =============================================================================
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

RAIZ = Path(__file__).resolve().parents[1]
INK, INK2, LINHA = "#0b0b0b", "#52514e", "#898781"
CORES = {"dados": "#e6eefa", "humano": "#fdebe2", "ia": "#e3f4ec", "aval": "#f4f3ef"}


def caixa(ax, x, y, w, h, titulo, texto, cor):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor=CORES[cor], edgecolor=LINHA, linewidth=0.8))
    ax.text(x + w / 2, y + h - 0.17, titulo, ha="center", va="top", fontsize=8.6,
            fontweight="bold", color=INK)
    ax.text(x + w / 2, y + h - 0.47, texto, ha="center", va="top", fontsize=7.2,
            color=INK2, linespacing=1.35)


def seta(ax, a, b):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=9, color=LINHA, lw=0.9))


def main() -> None:
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.set_xlim(0, 10); ax.set_ylim(0, 4.6); ax.axis("off")
    w, h = 2.15, 1.25
    # linha 1: dados
    caixa(ax, 0.1, 3.2, w, h, "1. Coleta", "API OpenAlex, 2023–2026\n3 consultas (en/pt/es)\n471 registros únicos", "dados")
    caixa(ax, 2.6, 3.2, w, h, "2. Preparação", "resumo do índice invertido\nduplicatas, idioma, tamanho\ncentralidade → 208", "dados")
    caixa(ax, 5.1, 3.2, w, h, "3. Análise exploratória", "anos, idiomas, tipos, fontes\ntermos e palavras-chave\n(notebooks 01–03)", "dados")
    caixa(ax, 7.6, 3.2, w, h, "4. Amostra e anotação", "60 resumos estratificados\n20 desenvolvimento + 40 teste\nA1 e A2 independentes", "humano")
    # linha 2: métodos
    caixa(ax, 0.1, 1.55, w, h, "M1 Léxico", "padrões en/pt/es por\ncategoria (codebook)\ntermos como evidência", "ia")
    caixa(ax, 2.6, 1.55, w, h, "M2 TF-IDF + K-means", "LSA 100 comp., k = 8\ngrupo herda categorias\ndo desenvolvimento", "ia")
    caixa(ax, 5.1, 1.55, w, h, "M3 LLMs", "Claude Haiku 4.5 (API)\nLlama 3.1 8B (local)\nzero-shot e few-shot", "ia")
    caixa(ax, 7.6, 1.55, w, h, "Consenso", "kappa A1 × A2\ndivergências resolvidas\n→ padrão-ouro", "humano")
    # linha 3: avaliação
    caixa(ax, 2.6, 0.05, 4.65, 1.2, "5. Avaliação no teste (métodos congelados antes)",
          "mesma saída multirrótulo · mesmo subconjunto de documentos\n"
          "P, R, F1, kappa, IC por bootstrap · comparação com cada anotador\n"
          "estabilidade · controle de evidências · análise de erros", "aval")
    caixa(ax, 7.6, 0.05, w, 1.2, "6. Panorama (QP1)", "melhor LLM aplicado\nàs 208 publicações\ntaxonomia + ressalvas", "aval")
    for x in (2.25, 4.75, 7.25):
        seta(ax, (x, 3.82), (x + 0.35, 3.82))
    seta(ax, (6.17, 3.2), (6.17, 2.8))            # EDA -> M3 (entrada: corpus)
    seta(ax, (1.17, 3.2), (1.17, 2.8))
    seta(ax, (3.67, 3.2), (3.67, 2.8))
    seta(ax, (8.67, 3.2), (8.67, 2.8))            # anotação -> consenso
    for x0, x1 in ((1.17, 2.9), (3.67, 3.67), (6.17, 6.17)):
        seta(ax, (x0, 1.55), (x1, 1.25))
    seta(ax, (8.67, 1.55), (7.05, 1.25))          # padrão-ouro -> avaliação
    seta(ax, (7.25, 1.05), (7.6, 1.05))
    fig.savefig(RAIZ / "figuras/fig0_fluxo_solucao.png", dpi=200, bbox_inches="tight")


if __name__ == "__main__":
    main()
