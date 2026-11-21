# =============================================================================
# Projeto: Análise de Recomendações Pedagógicas para o Uso de Inteligência
#          Artificial Generativa na Educação a Distância por meio de PLN e LLMs
# Disciplina: Inteligência Artificial - 7º N - Ciência da Computação
# Universidade Presbiteriana Mackenzie - Prof. Dr. Ivan Carlos Alcântara de Oliveira
# Integrante: Daniel Ribeiro Pauleti - RA 10723162
#
# Arquivo: src/classificacao_llm.py
# Síntese: classificação multirrótulo dos resumos por LLMs (M3), nos modos
#          zero-shot e few-shot, com dois modelos:
#            - claude-haiku-4-5 (Anthropic, via API; chave lida do arquivo .env)
#            - llama3.1:8b (modelo aberto, local, via Ollama)
#          Os dois recebem o mesmo prompt e o mesmo esquema JSON (saída
#          estruturada). Cada categoria deve vir com um trecho LITERAL do
#          resumo como evidência; evidências que não existem no texto
#          invalidam o rótulo (controle de alucinação). As respostas brutas
#          são gravadas em data/resultados/llm/ (execução retomável).
#
# Uso:
#   python src/classificacao_llm.py --modelo claude-haiku-4-5 --modo zero-shot --particao desenvolvimento
#   python src/classificacao_llm.py --modelo llama3.1:8b --modo few-shot --particao corpus
#   (--limite N processa só os N primeiros documentos; --execucao 2 grava uma repetição)
#
# Histórico de alterações:
#   2026-11-20 - Daniel Ribeiro Pauleti - Versão inicial (prompt v1.1).
#   2026-11-21 - Daniel Ribeiro Pauleti - Prompt v1.2: regras de decisão do codebook v1.2
#                e exemplos few-shot do desenvolvimento (prompts/exemplos_fewshot.json);
#                validação por cobertura literal (n-gramas >= 5, >= 80%) e --revalidar.
#   2026-11-21 - Daniel Ribeiro Pauleti - Prompt v1.3: esclarecimento APR_ATIVA x LETRAMENTO
#                (análise de erros do desenvolvimento). Versão congelada para o teste.
# =============================================================================
import argparse
import json
import re
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

from categorias import CATEGORIAS, CODIGOS, CRITERIOS, REGRAS, VERSAO_CODEBOOK

RAIZ = Path(__file__).resolve().parents[1]
DIR_SAIDA = RAIZ / "data/resultados/llm"
VERSAO_PROMPT = "1.3"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODELOS = {"claude-haiku-4-5": "anthropic", "llama3.1:8b": "ollama"}
MAX_TENTATIVAS = 3

# ---------------------------------------------------------------- prompt
SISTEMA = """Você é um assistente de pesquisa em Educação. Sua tarefa é identificar, no título e no resumo de uma publicação científica, RECOMENDAÇÕES PEDAGÓGICAS sobre o uso de IA generativa (por exemplo, ChatGPT) no ensino, com foco em educação a distância/online.

Regras:
1. Use apenas o texto fornecido; não use conhecimento externo sobre a publicação.
2. Marque uma categoria somente quando o texto RECOMENDA, PROPÕE, ORIENTA ou CONCLUI algo sobre ela. A simples menção ao tema não basta.
3. Zero, uma ou várias categorias podem se aplicar.
4. Para cada categoria marcada, copie em "evidencia" um trecho LITERAL e contínuo do título ou do resumo (no idioma original, sem traduzir nem resumir), de no máximo 40 palavras, que justifique a decisão.
5. "confianca" é um número entre 0 e 1.
6. "tem_recomendacao" é true se houver ao menos uma recomendação pedagógica explícita, mesmo fora das categorias.
7. "recomendacao_resumida": a principal recomendação em até 30 palavras, em português ("" se não houver).

Regras de decisão do livro de códigos:
{regras}

Esclarecimento de fronteira:
- Propor ou avaliar positivamente o uso da IA como tutor, assistente de estudo, fonte de feedback ou meio de personalizar a aprendizagem é APR_ATIVA, não LETRAMENTO. LETRAMENTO exige que o texto recomende desenvolver competências para compreender ou usar a IA (formação, letramento, engenharia de prompts).

Categorias:
{categorias}"""


def texto_regras() -> str:
    return "\n".join(f"- {i} ({titulo}): {texto}" for i, titulo, texto in REGRAS
                     if i != "R6")  # R6 (evidência) já está na regra 4 acima


def sistema() -> str:
    return SISTEMA.format(regras=texto_regras(), categorias=texto_categorias())


def texto_categorias() -> str:
    linhas = []
    for c, (nome, definicao, _) in CATEGORIAS.items():
        inclui, nao_inclui = CRITERIOS[c]
        linhas.append(f"- {c} ({nome}): {definicao} Inclui: {inclui} Não inclui: {nao_inclui}")
    return "\n".join(linhas)


def esquema() -> dict:
    return {
        "type": "object",
        "properties": {
            "tem_recomendacao": {"type": "boolean"},
            "categorias": {"type": "array", "items": {
                "type": "object",
                "properties": {"codigo": {"type": "string", "enum": CODIGOS},
                               "evidencia": {"type": "string"},
                               "confianca": {"type": "number"}},
                "required": ["codigo", "evidencia", "confianca"],
                "additionalProperties": False}},
            "recomendacao_resumida": {"type": "string"},
        },
        "required": ["tem_recomendacao", "categorias", "recomendacao_resumida"],
        "additionalProperties": False,
    }


def mensagem_usuario(titulo: str, resumo: str) -> str:
    return f"Título: {titulo}\n\nResumo: {resumo}"


def exemplos_fewshot() -> list[dict]:
    """Pares (usuário, assistente) a partir do padrão-ouro de DESENVOLVIMENTO.
    Os IDs e as evidências são escolhidos em prompts/exemplos_fewshot.json."""
    arq = RAIZ / "prompts/exemplos_fewshot.json"
    if not arq.exists():
        raise FileNotFoundError("prompts/exemplos_fewshot.json ainda não existe (é criado após o "
                                "consenso da partição de desenvolvimento).")
    cfg = json.loads(arq.read_text(encoding="utf-8"))
    amostra = pd.read_csv(RAIZ / "anotacao/amostra_anotacao.csv", encoding="utf-8-sig").set_index("openalex_id")
    msgs = []
    for ex in cfg["exemplos"]:
        doc = amostra.loc[ex["openalex_id"]]
        assert doc["particao"] == "desenvolvimento", "exemplo few-shot fora da partição de desenvolvimento"
        msgs.append({"role": "user", "content": mensagem_usuario(doc["titulo"], doc["resumo"])})
        msgs.append({"role": "assistant", "content": json.dumps(ex["resposta"], ensure_ascii=False)})
    return msgs


# ---------------------------------------------------------------- chamadas
def chamar_claude(cliente, modelo, sistema, mensagens) -> tuple[str, dict]:
    import anthropic
    r = cliente.messages.create(
        model=modelo, max_tokens=2048, system=sistema, messages=mensagens,
        output_config={"format": {"type": "json_schema", "schema": esquema()}},
    )
    if r.stop_reason == "refusal":
        raise RuntimeError(f"recusa: {getattr(r.stop_details, 'category', None)}")
    if r.stop_reason == "max_tokens":
        raise RuntimeError("resposta truncada (max_tokens)")
    texto = next(b.text for b in r.content if b.type == "text")
    uso = {"tokens_entrada": r.usage.input_tokens, "tokens_saida": r.usage.output_tokens,
           "modelo_resposta": r.model, "request_id": r._request_id}
    return texto, uso


def chamar_ollama(modelo, sistema, mensagens) -> tuple[str, dict]:
    corpo = {"model": modelo, "stream": False, "format": esquema(),
             "messages": [{"role": "system", "content": sistema}] + mensagens,
             "options": {"temperature": 0, "seed": 42, "num_ctx": 8192}}
    r = requests.post(OLLAMA_URL, json=corpo, timeout=600)
    r.raise_for_status()
    d = r.json()
    uso = {"tokens_entrada": d.get("prompt_eval_count"), "tokens_saida": d.get("eval_count"),
           "modelo_resposta": d.get("model")}
    return d["message"]["content"], uso


# ---------------------------------------------------------------- validação
def normalizar(t: str) -> str:
    t = unicodedata.normalize("NFKC", t or "").lower()
    t = re.sub(r"[“”\"'‘’`]", "", t)
    return re.sub(r"\s+", " ", t).strip(" .;,:…")


N_GRAMA = 5            # tamanho mínimo de uma sequência literal
COBERTURA_MINIMA = 0.8  # fração das palavras da evidência cobertas por sequências literais


def cobertura_literal(evidencia: str, fonte: str, n: int = N_GRAMA) -> float:
    """Fração das palavras da evidência que pertencem a alguma sequência de >= n
    palavras idêntica ao texto-fonte. Aceita a junção de trechos literais e a
    correção de um erro de digitação do resumo; rejeita paráfrases e invenções."""
    ev, fo = re.findall(r"\w+", evidencia), re.findall(r"\w+", fonte)
    if not ev:
        return 0.0
    if len(ev) < n:
        return 1.0 if " ".join(ev) in " ".join(fo) else 0.0
    ngramas = {tuple(fo[i:i + n]) for i in range(len(fo) - n + 1)}
    coberto = [False] * len(ev)
    for i in range(len(ev) - n + 1):
        if tuple(ev[i:i + n]) in ngramas:
            coberto[i:i + n] = [True] * n
    return sum(coberto) / len(ev)


def validar(bruto: str, titulo: str, resumo: str) -> dict:
    """Valida o JSON e verifica se cada evidência é (quase) literal do texto."""
    dados = json.loads(bruto)
    fonte = normalizar(f"{titulo} {resumo}")
    aceitas, rejeitadas = {}, []
    for cat in dados.get("categorias", []):
        c = cat.get("codigo")
        ev = normalizar(cat.get("evidencia", ""))
        cob = cobertura_literal(ev, fonte) if len(ev) >= 10 else 0.0
        if c not in CODIGOS:
            rejeitadas.append({**cat, "motivo": "codigo_invalido"})
        elif cob < COBERTURA_MINIMA:
            rejeitadas.append({**cat, "motivo": "evidencia_nao_literal", "cobertura": round(cob, 2)})
        elif c not in aceitas:  # mantém a primeira evidência de cada categoria
            aceitas[c] = {"evidencia": cat["evidencia"], "cobertura": round(cob, 2),
                          "confianca": max(0.0, min(1.0, float(cat.get("confianca", 0))))}
    rotulos = {c: int(c in aceitas) for c in CODIGOS}
    tem = int(bool(dados.get("tem_recomendacao")) or any(rotulos.values()))
    return {"rotulos": rotulos, "tem_recomendacao": tem, "aceitas": aceitas,
            "rejeitadas": rejeitadas, "recomendacao_resumida": dados.get("recomendacao_resumida", "")}


# ---------------------------------------------------------------- execução
def documentos(particao: str) -> pd.DataFrame:
    if particao == "corpus":
        df = pd.read_csv(RAIZ / "data/processed/corpus.csv")
    else:
        df = pd.read_csv(RAIZ / "anotacao/amostra_anotacao.csv", encoding="utf-8-sig")
        df = df[df["particao"] == particao]
    return df[["openalex_id", "titulo", "resumo"]].reset_index(drop=True)


def arquivo_saida(modelo, modo, particao, execucao) -> Path:
    nome = re.sub(r"[^a-z0-9.]+", "-", modelo.lower())
    sufixo = "" if execucao == 1 else f"_exec{execucao}"
    return DIR_SAIDA / f"{nome}_{modo}_{particao}{sufixo}.jsonl"


def executar(modelo, modo, particao, limite=None, execucao=1) -> Path:
    load_dotenv(RAIZ / ".env")  # ANTHROPIC_API_KEY (o arquivo .env não é versionado)
    provedor = MODELOS[modelo]
    cliente = None
    if provedor == "anthropic":
        import anthropic
        cliente = anthropic.Anthropic(max_retries=4)
    msg_sistema = sistema()
    prefixo = exemplos_fewshot() if modo == "few-shot" else []

    saida = arquivo_saida(modelo, modo, particao, execucao)
    saida.parent.mkdir(parents=True, exist_ok=True)
    feitos = set()
    if saida.exists():
        feitos = {json.loads(l)["openalex_id"] for l in saida.open(encoding="utf-8") if l.strip()}
    docs = documentos(particao)
    if limite:
        docs = docs.head(limite)
    pendentes = docs[~docs["openalex_id"].isin(feitos)]
    print(f"{modelo} | {modo} | {particao}: {len(pendentes)} pendentes de {len(docs)}")

    with saida.open("a", encoding="utf-8") as f:
        for i, d in enumerate(pendentes.itertuples(), 1):
            msgs = prefixo + [{"role": "user", "content": mensagem_usuario(d.titulo, d.resumo)}]
            reg = {"openalex_id": d.openalex_id, "modelo": modelo, "modo": modo, "particao": particao,
                   "execucao": execucao, "versao_prompt": VERSAO_PROMPT, "versao_codebook": VERSAO_CODEBOOK}
            inicio = time.time()
            for tentativa in range(1, MAX_TENTATIVAS + 1):
                bruto = None
                try:
                    if provedor == "anthropic":
                        bruto, uso = chamar_claude(cliente, modelo, msg_sistema, msgs)
                    else:
                        bruto, uso = chamar_ollama(modelo, msg_sistema, msgs)
                    reg.update(validar(bruto, d.titulo, d.resumo), resposta_bruta=bruto, **uso, erro=None)
                    break
                except (json.JSONDecodeError, RuntimeError, KeyError, ValueError,
                        requests.RequestException) as e:
                    reg.update(erro=f"{type(e).__name__}: {e}", resposta_bruta=bruto)
                except Exception as e:  # erros da API Anthropic (o SDK já fez as retentativas)
                    if type(e).__module__.startswith("anthropic"):
                        reg.update(erro=f"{type(e).__name__}: {e}", resposta_bruta=bruto)
                        break
                    raise
            reg.update(tentativas=tentativa, segundos=round(time.time() - inicio, 2),
                       data=datetime.now(timezone.utc).isoformat())
            f.write(json.dumps(reg, ensure_ascii=False) + "\n")
            f.flush()
            status = "ERRO " + reg["erro"] if reg.get("erro") else \
                ",".join(c for c, v in reg["rotulos"].items() if v) or "(nenhuma)"
            print(f"  [{i}/{len(pendentes)}] {d.openalex_id} {reg['segundos']}s -> {status}")
    return saida


def revalidar(arquivo: Path) -> None:
    """Reaplica validar() às respostas brutas já gravadas (sem chamar os modelos)."""
    textos = pd.read_csv(RAIZ / "data/processed/corpus.csv").set_index("openalex_id")
    regs = [json.loads(l) for l in arquivo.open(encoding="utf-8") if l.strip()]
    for r in regs:
        if r.get("resposta_bruta") and not r.get("erro"):
            d = textos.loc[r["openalex_id"]]
            r.update(validar(r["resposta_bruta"], d["titulo"], d["resumo"]))
    arquivo.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in regs), encoding="utf-8")


def exportar_prompt() -> Path:
    """Grava o prompt exato e o esquema JSON em prompts/ (documentação versionada)."""
    saida = RAIZ / f"prompts/prompt_classificacao_v{VERSAO_PROMPT}.md"
    partes = [
        "<!-- Gerado por src/classificacao_llm.py --exportar-prompt. Não editar à mão. -->",
        f"# Prompt de classificação v{VERSAO_PROMPT} (livro de códigos v{VERSAO_CODEBOOK})",
        f"Modelos: {', '.join(MODELOS)}. Mesma mensagem de sistema, mesma mensagem de usuário e "
        "mesmo esquema JSON (saída estruturada) para os dois. Llama: temperature 0, seed 42 "
        "(Ollama). Claude: amostragem padrão da API (a API não aceita mais temperature); a "
        "estabilidade é medida repetindo a execução.",
        "## Mensagem de sistema",
        "```text\n" + sistema() + "\n```",
        "## Mensagem de usuário",
        "```text\n" + mensagem_usuario("{titulo}", "{resumo}") + "\n```",
        "No modo few-shot, antes da mensagem do usuário entram 3 pares (exemplo, resposta) da "
        "partição de desenvolvimento, definidos em `prompts/exemplos_fewshot.json`.",
        "## Esquema JSON da resposta",
        "```json\n" + json.dumps(esquema(), ensure_ascii=False, indent=2) + "\n```",
        "## Validação",
        f"1. JSON inválido ou recusa: nova tentativa (até {MAX_TENTATIVAS}).\n"
        f"2. Cada `evidencia` deve ser (quase) literal: ao menos {COBERTURA_MINIMA:.0%} de suas "
        f"palavras precisam pertencer a sequências de {N_GRAMA} ou mais palavras idênticas ao "
        "título/resumo (sem diferenciar maiúsculas, aspas e pontuação). Isso aceita a junção de "
        "trechos literais e a correção de erro de digitação do resumo, e rejeita paráfrases e "
        "invenções; o rótulo rejeitado é registrado em `rejeitadas` com sua cobertura.\n"
        "3. `tem_recomendacao` passa a 1 se houver ao menos uma categoria aceita.",
    ]
    saida.write_text("\n\n".join(partes) + "\n", encoding="utf-8")
    return saida


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exportar-prompt", action="store_true")
    ap.add_argument("--modelo", choices=list(MODELOS))
    ap.add_argument("--modo", choices=["zero-shot", "few-shot"], default="zero-shot")
    ap.add_argument("--particao", choices=["desenvolvimento", "teste", "corpus"])
    ap.add_argument("--limite", type=int)
    ap.add_argument("--execucao", type=int, default=1)
    ap.add_argument("--revalidar", action="store_true",
                    help="reaplica a validação de evidências a todos os resultados gravados")
    a = ap.parse_args()
    if a.exportar_prompt:
        print("Gerado:", exportar_prompt())
        return
    if a.revalidar:
        for f in sorted(DIR_SAIDA.glob("*.jsonl")):
            revalidar(f)
            print("Revalidado:", f.name)
        return
    if not (a.modelo and a.particao):
        ap.error("--modelo e --particao são obrigatórios")
    executar(a.modelo, a.modo, a.particao, a.limite, a.execucao)


if __name__ == "__main__":
    main()
