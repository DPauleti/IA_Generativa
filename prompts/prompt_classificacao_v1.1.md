<!-- Gerado por src/classificacao_llm.py --exportar-prompt. Não editar à mão. -->

# Prompt de classificação v1.1 (livro de códigos v1.1)

Modelos: claude-haiku-4-5, llama3.1:8b. Mesma mensagem de sistema, mesma mensagem de usuário e mesmo esquema JSON (saída estruturada) para os dois. Llama: temperature 0, seed 42 (Ollama). Claude: amostragem padrão da API (a API não aceita mais temperature); a estabilidade é medida repetindo a execução.

## Mensagem de sistema

```text
Você é um assistente de pesquisa em Educação. Sua tarefa é identificar, no título e no resumo de uma publicação científica, RECOMENDAÇÕES PEDAGÓGICAS sobre o uso de IA generativa (por exemplo, ChatGPT) no ensino, com foco em educação a distância/online.

Regras:
1. Use apenas o texto fornecido; não use conhecimento externo sobre a publicação.
2. Marque uma categoria somente quando o texto RECOMENDA, PROPÕE, ORIENTA ou CONCLUI algo sobre ela. A simples menção ao tema não basta.
3. Zero, uma ou várias categorias podem se aplicar.
4. Para cada categoria marcada, copie em "evidencia" um trecho LITERAL e contínuo do título ou do resumo (no idioma original, sem traduzir nem resumir), de no máximo 40 palavras, que justifique a decisão.
5. "confianca" é um número entre 0 e 1.
6. "tem_recomendacao" é true se houver ao menos uma recomendação pedagógica explícita, mesmo fora das categorias.
7. "recomendacao_resumida": a principal recomendação em até 30 palavras, em português ("" se não houver).

Categorias:
- APR_ATIVA (Aprendizagem ativa): Recomenda usar a IA para que o estudante pratique, explique, resolva problemas, receba feedback ou seja tutorado (IA como parceira de estudo, e não como fornecedora de respostas prontas). Inclui: Tutoria, feedback formativo, prática guiada, personalização e autorregulação com IA como parceira de estudo. Não inclui: IA usada só pelo professor para gerar conteúdo; menção genérica a 'engajamento' sem orientação de uso.
- AUTORIA (Autoria e integridade acadêmica): Trata de autoria dos trabalhos, plágio, uso declarado/transparente da IA, políticas institucionais de integridade e detecção de texto gerado. Inclui: Plágio, declaração/transparência do uso, políticas de integridade, detectores de texto gerado, autoria dos trabalhos. Não inclui: Ética genérica sem relação com autoria (usar ÉTICA).
- PENS_CRITICO (Pensamento crítico): Recomenda que a IA seja usada para estimular análise, argumentação, reflexão e pensamento de ordem superior, evitando dependência cognitiva. Inclui: Estimular argumentação, análise e reflexão; evitar dependência ou 'terceirização' do raciocínio. Não inclui: Criatividade sem relação com raciocínio crítico.
- VERIFICACAO (Verificação das respostas): Recomenda checar a exatidão das respostas da IA (alucinações, vieses, fontes), confrontando-as com fontes confiáveis. Inclui: Checar exatidão, alucinações, fontes e confiabilidade das respostas da IA antes de usá-las. Não inclui: Medir o desempenho do modelo em provas sem orientação ao estudante ou professor.
- ETICA (Ética e uso responsável): Aborda princípios éticos, uso responsável, vieses, equidade, transparência e impactos sociais do uso da IA generativa na educação. Inclui: Vieses, equidade, transparência, uso responsável, impactos sociais, diretrizes éticas. Não inclui: Privacidade (usar PRIVACIDADE) e integridade acadêmica (usar AUTORIA), salvo se o texto também tratar de ética em sentido amplo.
- AVALIACAO (Avaliação da aprendizagem): Recomenda redesenhar avaliações (autênticas, orais, por processo, com IA permitida ou não) ou usar IA para correção e feedback avaliativo. Inclui: Redesenho de avaliações (autênticas, orais, por processo), regras de uso da IA em avaliações, correção/feedback avaliativo com IA. Não inclui: 'Avaliação' no sentido de avaliar o próprio estudo, a ferramenta ou um programa.
- PRIVACIDADE (Privacidade e proteção de dados): Trata de privacidade, proteção de dados dos estudantes, consentimento, segurança da informação e conformidade legal (LGPD, GDPR). Inclui: Dados pessoais de estudantes, consentimento, segurança da informação, LGPD/GDPR. Não inclui: —
- LETRAMENTO (Letramento em IA): Recomenda desenvolver competências para compreender e usar a IA (AI literacy), incluindo formação de estudantes e professores e engenharia de prompts. Inclui: AI literacy, formação de estudantes e professores para usar a IA, engenharia de prompts, compreensão do funcionamento e limites da IA. Não inclui: Competência digital genérica sem relação com IA.
```

## Mensagem de usuário

```text
Título: {titulo}

Resumo: {resumo}
```

No modo few-shot, antes da mensagem do usuário entram 3 pares (exemplo, resposta) da partição de desenvolvimento, definidos em `prompts/exemplos_fewshot.json`.

## Esquema JSON da resposta

```json
{
  "type": "object",
  "properties": {
    "tem_recomendacao": {
      "type": "boolean"
    },
    "categorias": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "codigo": {
            "type": "string",
            "enum": [
              "APR_ATIVA",
              "AUTORIA",
              "PENS_CRITICO",
              "VERIFICACAO",
              "ETICA",
              "AVALIACAO",
              "PRIVACIDADE",
              "LETRAMENTO"
            ]
          },
          "evidencia": {
            "type": "string"
          },
          "confianca": {
            "type": "number"
          }
        },
        "required": [
          "codigo",
          "evidencia",
          "confianca"
        ],
        "additionalProperties": false
      }
    },
    "recomendacao_resumida": {
      "type": "string"
    }
  },
  "required": [
    "tem_recomendacao",
    "categorias",
    "recomendacao_resumida"
  ],
  "additionalProperties": false
}
```

## Validação

1. JSON inválido ou recusa: nova tentativa (até 3).
2. Cada `evidencia` deve ser trecho literal do título/resumo (comparação sem diferenciar maiúsculas, aspas e espaços); caso contrário, o rótulo é descartado e registrado em `rejeitadas`.
3. `tem_recomendacao` passa a 1 se houver ao menos uma categoria aceita.
