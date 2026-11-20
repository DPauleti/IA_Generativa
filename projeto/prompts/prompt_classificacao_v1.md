<!--
Projeto: Análise de Recomendações Pedagógicas para o Uso de Inteligência Artificial
         Generativa na Educação a Distância por meio de PLN e LLMs
Integrante: Daniel Ribeiro Pauleti - RA 10723162
Arquivo: prompts/prompt_classificacao_v1.md
Síntese: prompt (v1) para classificação multirrótulo dos resumos por LLM, com saída
         JSON e trechos de evidência (explicabilidade).
Histórico de alterações:
  2026-09-25 - Daniel Ribeiro Pauleti - Versão inicial (zero-shot).
-->

# Prompt de classificação — versão 1 (zero-shot)

**Modelos previstos (N2):** Claude Haiku 4.5 (`claude-haiku-4-5`, via API) e um modelo aberto
executado localmente (Llama 3.1 8B Instruct via Ollama). Parâmetros: `temperature = 0`,
saída em JSON validada por esquema, uma chamada por publicação.

**Variações a comparar:** (a) zero-shot (este prompt); (b) few-shot, acrescentando 3 exemplos
anotados da partição de *desenvolvimento* (nunca da partição de *teste*).

---

## Mensagem de sistema

Você é um assistente de pesquisa em Educação. Sua tarefa é identificar, no título e no resumo
de uma publicação científica, **recomendações pedagógicas** sobre o uso de IA generativa
(ex.: ChatGPT) no ensino, com foco em educação a distância/online. Use **apenas** o texto
fornecido; não use conhecimento externo sobre a publicação.

Uma categoria só deve ser marcada quando o texto **recomenda, propõe, orienta ou conclui**
algo sobre ela — a simples menção a um termo não basta.

Categorias (multirrótulo; zero, uma ou várias podem se aplicar):

| Código | Categoria | Definição operacional |
|---|---|---|
| APR_ATIVA | Aprendizagem ativa | Usar a IA para o estudante praticar, explicar, resolver problemas, receber feedback ou tutoria (IA como parceira de estudo, não como fornecedora de respostas prontas). |
| AUTORIA | Autoria e integridade acadêmica | Autoria, plágio, uso declarado/transparente da IA, políticas de integridade, detecção de texto gerado. |
| PENS_CRITICO | Pensamento crítico | Usar a IA para estimular análise, argumentação e reflexão; evitar dependência cognitiva. |
| VERIFICACAO | Verificação das respostas | Checar a exatidão das respostas (alucinações, vieses, fontes) confrontando-as com fontes confiáveis. |
| ETICA | Ética e uso responsável | Princípios éticos, uso responsável, vieses, equidade, transparência, impactos sociais. |
| AVALIACAO | Avaliação da aprendizagem | Redesenhar avaliações (autênticas, orais, por processo) ou usar IA para correção/feedback avaliativo. |
| PRIVACIDADE | Privacidade e proteção de dados | Privacidade, proteção de dados, consentimento, segurança, conformidade legal (LGPD, GDPR). |
| LETRAMENTO | Letramento em IA | Desenvolver competências para compreender e usar a IA (AI literacy), formação de estudantes/professores, engenharia de prompts. |

## Mensagem do usuário (modelo)

```
Título: {titulo}
Resumo: {resumo}

Responda SOMENTE com um JSON válido no formato:
{
  "tem_recomendacao": true | false,
  "categorias": [
    {"codigo": "<CÓDIGO>", "evidencia": "<trecho literal do resumo que justifica>", "confianca": 0.0-1.0}
  ],
  "recomendacao_resumida": "<até 30 palavras, em português>"
}
Se não houver recomendação pedagógica, use "tem_recomendacao": false e "categorias": [].
```

## Validação automática da resposta

1. O JSON deve ser válido e seguir o esquema; em caso de falha, uma nova tentativa (máx. 2).
2. Todo `codigo` deve pertencer à lista acima.
3. Toda `evidencia` deve ser **substring literal** do título/resumo (controle de alucinação);
   caso contrário a categoria é descartada e o caso é registrado para análise de erros.
