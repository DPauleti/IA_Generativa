<!--
Projeto: Análise de Recomendações Pedagógicas para o Uso de Inteligência Artificial
         Generativa na Educação a Distância por meio de PLN e LLMs
Integrante: Daniel Ribeiro Pauleti - RA 10723162
Arquivo: anotacao/consenso/pauta_consenso_desenvolvimento.md
Síntese: diagnóstico da concordância A1 × A2 na partição de desenvolvimento e
         pauta da reunião de consenso (propostas de regras para o livro de códigos v1.2).
Histórico de alterações:
  2026-11-21 - Daniel Ribeiro Pauleti - Versão inicial.
-->

# Pauta da reunião de consenso — partição de desenvolvimento

## Resultado da anotação independente (codebook v1.1, 20 publicações)

| Rótulo | Acordo | κ | Prevalência A1 | Prevalência A2 |
|---|---|---|---|---|
| Aprendizagem ativa | 70% | 0,35 | 40% | 30% |
| Autoria e integridade | 90% | −0,05 | 5% | 5% |
| Pensamento crítico | 75% | −0,09 | 5% | 20% |
| Verificação das respostas | 95% | 0,00 | 0% | 5% |
| Ética e uso responsável | 85% | 0,00 | 0% | 15% |
| Avaliação da aprendizagem | 70% | −0,15 | 10% | 20% |
| Privacidade e dados | 90% | 0,00 | 0% | 10% |
| Letramento em IA | 95% | 0,00 | 0% | 5% |
| **Há recomendação** | 65% | 0,30 | 50% | 75% |

Acordo exato nas 8 categorias: 25% dos documentos. κ médio: 0,01.

**Leitura dos números.** Com 20 documentos e prevalências de 0% a 20%, o kappa é instável:
uma única divergência numa categoria rara leva κ a zero ou a valores negativos, mesmo com
90–95% de acordo bruto (o "paradoxo do kappa"). Ainda assim, o padrão é claro e sistemático.

## Diagnóstico

1. **Recomendação × menção (principal causa).** 24 das 33 divergências são marcações só do
   A2, e em 6 das 7 divergências de "há recomendação" o A2 marcou 1 e o A1, 0. O A2 tende a
   marcar temas *citados* no resumo (por exemplo, ética e privacidade citadas como
   preocupação de contexto); o A1, só orientações explícitas.
2. **Resultados descritivos.** Estudos de percepção ou de desempenho (por exemplo,
   W4400280294, W4402988803) relatam achados sem dizer o que professores ou estudantes
   devem fazer. Falta uma regra sobre quando um achado conta como recomendação.
3. **Fronteiras entre categorias.** Aprendizagem ativa × Avaliação (feedback formativo ×
   avaliativo) e Pensamento crítico × Aprendizagem ativa geraram 17 divergências.
4. **Documentos fora do escopo.** W7126207768 trata de um algoritmo de detecção de texto
   gerado por LLM: "distance" é uma métrica de aprendizado de máquina, não educação a
   distância. W4388490750 trata de patrimônio cultural na Malásia. São falsos positivos da
   busca por palavras-chave, que o filtro de centralidade não removeu (registrar como
   limitação do corpus).
5. **Nenhuma observação registrada** pelos dois anotadores, com cerca de 50 s por
   documento. Sem o trecho decisivo anotado, a reunião de consenso depende de memória.

## Propostas de regras para o livro de códigos v1.2 (decidir na reunião)

- **R1 — O que é recomendação.** Conta apenas um enunciado prescritivo (should, recommend,
  suggest, need to, deve-se, recomenda-se, implicações para a prática) **ou** uma conclusão
  que o próprio texto transforma em orientação. Um resultado descritivo ("os estudantes
  perceberam o ChatGPT como preciso") não conta.
  *Aprovado*
- **R2 — Contexto não é recomendação.** Riscos citados na introdução ou na motivação
  ("levanta preocupações éticas") não marcam categoria.
  *Aprovado*
- **R3 — Trabalhos técnicos.** Sistemas, algoritmos e detectores só contam se o texto
  orientar como professores ou estudantes devem usá-los.
  *Rejeitado*
- **R4 — Fora do escopo.** Documento que não trata de educação com IA generativa: todas as
  categorias 0, "há recomendação" 0, e observação "fora do escopo".
  *Aprovado*
- **R5 — Aprendizagem ativa × Avaliação.** Feedback para aprender → Aprendizagem ativa;
  notas, correção, desenho de provas e regras de uso em avaliações → Avaliação.
  *Aprovado*
- **R6 — Evidência obrigatória.** Para cada categoria marcada, copiar em Observações o
  trecho decisivo (o mesmo que se exige do LLM).
  *Aprovado*

## Procedimento

1. Abrir `divergencias_desenvolvimento.csv` (inclui o resumo), discutir cada linha,
   preencher `consenso` (0/1) e `justificativa`.
2. Aprovar, alterar ou rejeitar R1–R6 e registrar a decisão neste arquivo.
3. Gerar o padrão-ouro: `python src/concordancia.py desenvolvimento A1 A2 --padrao-ouro`.
4. Atualizar o livro de códigos para v1.2, regenerar a página e congelar em commit.
5. Rodada de calibração (ver abaixo) antes do teste.
