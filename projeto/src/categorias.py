# =============================================================================
# Projeto: Análise de Recomendações Pedagógicas para o Uso de Inteligência
#          Artificial Generativa na Educação a Distância por meio de PLN e LLMs
# Disciplina: Inteligência Artificial - 7º N - Ciência da Computação
# Universidade Presbiteriana Mackenzie - Prof. Dr. Ivan Carlos Alcântara de Oliveira
# Integrante: Daniel Ribeiro Pauleti - RA 10723162
#
# Arquivo: src/categorias.py
# Síntese: livro de códigos (codebook) com as 8 categorias de recomendações
#          pedagógicas e o classificador léxico (baseline de regras), com termos
#          em inglês, português e espanhol. O classificador devolve, para cada
#          categoria, os termos encontrados (evidência explicável da decisão).
#
# Histórico de alterações:
#   2026-09-25 - Daniel Ribeiro Pauleti - Versão inicial do codebook (v1).
#   2026-09-25 - Daniel Ribeiro Pauleti - Padrões mais restritos para reduzir falsos
#                positivos (ex.: "exam" x "examines", "etic" x "theoretical").
# =============================================================================
import re

import pandas as pd

# código -> (nome, definição operacional, padrões léxicos EN/PT/ES)
CATEGORIAS = {
    "APR_ATIVA": (
        "Aprendizagem ativa",
        "Recomenda usar a IA para que o estudante pratique, explique, resolva problemas, "
        "receba feedback ou seja tutorado (IA como parceira de estudo, e não como "
        "fornecedora de respostas prontas).",
        [r"active learning", r"self[- ]regulat", r"self[- ]directed", r"scaffold", r"tutor",
         r"feedback", r"retrieval practice", r"practice (tests?|questions|exercises)", r"personali[sz]", r"engagement", r"metacogn",
         r"aprendizagem ativa", r"autorregula", r"aprendizaje activo", r"retroaliment"]),
    "AUTORIA": (
        "Autoria e integridade acadêmica",
        "Trata de autoria dos trabalhos, plágio, uso declarado/transparente da IA, "
        "políticas institucionais de integridade e detecção de texto gerado.",
        [r"academic (integrity|dishonesty|misconduct)", r"plagiar", r"cheat", r"authorship",
         r"ghostwrit", r"ai[- ]generated text", r"detect(or|ion) tool", r"disclos",
         r"integridade acad", r"pl[aá]gio", r"autoria", r"integridad acad", r"deshonestidad"]),
    "PENS_CRITICO": (
        "Pensamento crítico",
        "Recomenda que a IA seja usada para estimular análise, argumentação, reflexão e "
        "pensamento de ordem superior, evitando dependência cognitiva.",
        [r"critical thinking", r"higher[- ]order", r"reflective", r"reflection", r"overreliance",
         r"over-reliance", r"over-?dependen", r"\bdependen(ce|cy) on", r"cognitive offload",
         r"problem[- ]solving", r"creativ", r"pensamento cr[ií]tico", r"reflex[aã]o", r"reflexiv",
         r"pensamiento cr[ií]tico"]),
    "VERIFICACAO": (
        "Verificação das respostas",
        "Recomenda checar a exatidão das respostas da IA (alucinações, vieses, fontes), "
        "confrontando-as com fontes confiáveis.",
        [r"hallucinat", r"accura(cy|te)", r"fact[- ]check", r"verif(y|ying|ication|icar|ica[çc][aã]o)", r"reliab", r"misinformation",
         r"inaccura", r"fabricat", r"alucina", r"precis[aã]o", r"confiabilidade", r"veracidad"]),
    "ETICA": (
        "Ética e uso responsável",
        "Aborda princípios éticos, uso responsável, vieses, equidade, transparência e "
        "impactos sociais do uso da IA generativa na educação.",
        [r"ethic", r"responsib", r"\bbias", r"fairness", r"equit", r"transparen", r"trustworth",
         r"\b[ée]tic[ao]s?\b", r"respons[aá]ve", r"sesgo", r"equidad"]),
    "AVALIACAO": (
        "Avaliação da aprendizagem",
        "Recomenda redesenhar avaliações (autênticas, orais, por processo, com IA "
        "permitida ou não) ou usar IA para correção e feedback avaliativo.",
        [r"assessment", r"\bexams?\b", r"\bexamination", r"grading", r"\bassignment",
         r"evaluation of (student|learning)", r"authentic (assessment|task)", r"avalia[çc]",
         r"\bprovas?\b", r"evaluaci[oó]n"]),
    "PRIVACIDADE": (
        "Privacidade e proteção de dados",
        "Trata de privacidade, proteção de dados dos estudantes, consentimento, segurança "
        "da informação e conformidade legal (LGPD, GDPR).",
        [r"privacy", r"data protection", r"personal data", r"\bgdpr", r"\blgpd", r"security",
         r"surveillance", r"consent", r"privacidade", r"prote[çc][aã]o de dados",
         r"privacidad", r"datos personales"]),
    "LETRAMENTO": (
        "Letramento em IA",
        "Recomenda desenvolver competências para compreender e usar a IA (AI literacy), "
        "incluindo formação de estudantes e professores e engenharia de prompts.",
        [r"\bai literacy", r"literac", r"digital competenc", r"prompt(ing| engineering)",
         r"training (for|of) (teachers|students|faculty)", r"professional development",
         r"letramento", r"alfabetiza[çc][aã]o", r"compet[eê]ncia digital", r"formaci[oó]n docente",
         r"forma[çc][aã]o (docente|de professores)", r"alfabetizaci[oó]n"]),
}

CODIGOS = list(CATEGORIAS)
NOMES = {c: v[0] for c, v in CATEGORIAS.items()}
_REGEX = {c: re.compile("|".join(v[2]), re.I) for c, v in CATEGORIAS.items()}


def classificar_lexico(texto: str) -> dict:
    """Retorna {codigo: [termos encontrados]} para as categorias presentes."""
    achados = {}
    for codigo, rx in _REGEX.items():
        termos = sorted({m.group(0).lower() for m in rx.finditer(texto or "")})
        if termos:
            achados[codigo] = termos
    return achados


def matriz_lexica(df: pd.DataFrame, coluna: str = "texto") -> tuple[pd.DataFrame, pd.Series]:
    """Matriz binária documento x categoria e a série de evidências (termos)."""
    evid = df[coluna].map(classificar_lexico)
    matriz = pd.DataFrame({c: evid.map(lambda e: int(c in e)) for c in CODIGOS}, index=df.index)
    return matriz, evid
