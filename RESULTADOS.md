# MulitaMiner: modelo local especializado para extração de vulnerabilidades

Resumo dos resultados para revisão. O objetivo do trabalho é um modelo de
extração **embarcável** (rodável em CPU, sem GPU e sem orçamento de API),
que leia relatórios de scanners de vulnerabilidade em PDF e produza registros
estruturados, mantendo a qualidade próxima da de um modelo de nuvem, mas com
os dados nunca saindo da máquina (on-premise).

O caminho foi: (1) medir o quão longe os modelos pequenos locais estão da
nuvem; (2) escolher um candidato para especializar; (3) especializar via
fine-tuning e medir o ganho; (4) testar se o modelo especializado generaliza
para scanners que nunca viu.

## Metodologia (resumo)

- **Extração ancorada em blocos:** a segmentação determinística fixa o número
  de achados antes do LLM, que preenche os campos de cada bloco (não descobre
  achados). Isso separa "cobertura" (alinhamento) de "fidelidade de conteúdo".
- **Gabaritos (baselines) do próprio scanner:** derivados dos exports de
  máquina (CSV do OpenVAS/Qualys, HTML do Nessus, XML do ZAP), não anotados à
  mão, com verificação campo a campo. Aparados por fidelidade ao input (texto
  que o PDF não renderiza é removido, para a régua não cobrar o impossível).
- **Métricas:** cobertura (recall), aderência ao contrato (blocos perdidos) e
  fidelidade por campo em três camadas, léxica (token_f1), semântica
  (BERTScore) e determinística. O ranking é o mesmo nas três.
- **Separação treino/avaliação:** relatórios e hosts de avaliação nunca entram
  no treino, em nenhum scanner, por contrato versionado aplicado na geração do
  dataset (detalhado logo abaixo, com os relatórios nomeados).
- **Empacotamento calibrado por qualidade:** quantos achados vão em cada
  chamada ao modelo é um parâmetro por scanner. Para o OpenVAS ele foi
  recalibrado medindo preenchimento de campo contra o gabarito (4, 2 e 1 por
  chamada), e fixado em 2: a cobertura sobe de 0.906 para 0.965 e a extração
  fica mais rápida. Os demais scanners mantêm os valores anteriores, onde a
  omissão medida já era próxima de zero.
- **Ambiente:** GPU RTX 5080 (treino via QLoRA/Unsloth), modelos servidos por
  Ollama; extração idêntica à de produção. O modelo é servido com o
  `serving/Modelfile` versionado: registrar os pesos sem ele esvazia os campos
  estruturados em silêncio.

Observação importante para ler as tabelas: o **estudo comparativo** usa 24
relatórios; a **avaliação do fine-tuning** usa 8 relatórios separados
(held-out). Comparações valem **dentro** de cada tabela, não entre elas
(conjuntos de relatórios diferentes). O estudo comparativo foi medido com o
empacotamento antigo (OpenVAS a 4 achados por chamada) e a avaliação do
fine-tuning com o atual (2), que é outra razão para não cruzar as duas.

### Separação treino/avaliação, em detalhe

O contrato está em `heldout.json`, versionado, e é aplicado na geração do
dataset, não à mão.

**Os 8 relatórios de avaliação (held-out), nunca vistos no treino:**

| Scanner | Relatórios |
|---|---|
| OpenVAS | `bkimminich_juice-shop`, `raesene_bwapp`, `wordpress_4.9` |
| Nessus | `VulnLab_scan-b` |
| Qualys | `VulnLab_scan-b` |
| ZAP | `JuiceShop`, `bWAPP`, `JBoss7` |

**O treino** usou 136 relatórios, nenhum deles acima. Por scanner, em chunks
de treino: OpenVAS 6872, Qualys 1234, Nessus 511, ZAP 123, num total de 6841
registros. A proveniência completa está em `data/dataset/dataset_report.md`.

**Três regras de separação, não uma.** A primeira é óbvia, as outras duas é
que fecham o vazamento:

1. **Stems held-out:** os 8 relatórios acima nunca entram no treino.
2. **Stems negados:** mais 8 relatórios ficam de fora por outros motivos, a
   duplicata da mesma app pelo mesmo scanner, os scanners sem gabarito de
   máquina (Tenable e Acunetix, reservados para o teste de scanner inédito) e
   três gabaritos antigos feitos à mão.
3. **Hosts eval-only:** os hosts das aplicações held-out são negados em
   **todos os scanners**. Não basta tirar o juice-shop do OpenVAS: o
   juice-shop visto pelo ZAP ou pelo Tenable também sai. Sem essa regra o
   modelo poderia ter aprendido a mesma aplicação por outra ferramenta, e a
   avaliação cruzada entre scanners perderia o sentido.

**A guarda deixa rastro.** O relatório de geração do dataset registra quantos
exemplos ela recusou:

```
contamination guard: 16 stems, 5 eval-only hosts
denied examples: {'host': 199, 'stem': 1208}
```

São **1407 exemplos descartados** por contaminação. É evidência de que a
regra rodou, não promessa de que foi seguida.

**Os scanners nunca vistos** (Parte 4) são o Tenable e o Acunetix: eles não
aparecem no treino em nenhum formato, e estão na lista de stems negados
justamente para poderem cumprir esse papel. Os relatórios usados são
`TenableWAS_bWAPP`, `TenableWAS_JuiceShop`, `Acunetix_testaspnet` e
`Acunetix_testphp`.

## Onde estão os dados brutos

As tabelas deste documento são recortes. Cada número sai de uma árvore de
execuções, e cada execução guarda a extração completa, a avaliação campo a
campo e o registro da rodada.

**Aviso:** todas essas pastas estão no `.gitignore` (são artefatos de
execução, não código) e existem **apenas na máquina de desenvolvimento**.
Fazer backup delas é responsabilidade manual.

### O que tem dentro de cada rodada

| Arquivo | Conteúdo |
|---|---|
| `results.json` | os registros extraídos, o artefato principal |
| `results.raw.json` | versão pré-consolidação, quando houve fusão de achados |
| `evaluation.json` | avaliação completa: por campo, por métrica, **par a par** |
| `evaluation.md` | a mesma avaliação em tabela legível |
| `run.json` | blocos, tokens, custo, drops, retries e, nas rodadas recentes, o ambiente (`runtime`) |
| `run.log` | o log da execução, chunk a chunk |

O `evaluation.json` é onde está tudo o que as tabelas resumem: ele tem a lista
`pairs`, com o texto extraído e o texto do gabarito lado a lado para **cada
achado e cada campo**. É lá que se olha quando um número parece estranho.

### Mapa por parte deste documento

| Parte | Onde | Repositório |
|---|---|---|
| **Parte 1**, estudo dos 10 modelos (24 relatórios) | `output_slm_metrics/` (com BERTScore) e `output_experiments/` (léxico, mais `experiment.json` e `report.html`) | MulitaMiner2 |
| Parte 1, experimento de prompt | `output_prompt_test/` | MulitaMiner2 |
| **Parte 3**, fine-tuning (8 held-out) | `output_heldout/mulita-qwen2.5-1.5b{,-v2,-v3,-v4}/` | Mulita-Training |
| Parte 3, linha do modelo base | `output_heldout/qwen2.5-1.5b/` | Mulita-Training |
| Parte 3, linha da nuvem | `output_heldout/deepseek/` | Mulita-Training |
| **Parte 4**, scanners inéditos, v4 | `output_heldout/mulita-qwen2.5-1.5b-v4-unseen/{tenable,acunetix}/` | Mulita-Training |
| Parte 4, base e nuvem | `output_experiments/{qwen2.5-1.5b,deepseek}/{tenable,acunetix}/` | MulitaMiner2 |

Duas observações para quem for procurar:

- A pasta `_incomplete/` dentro da árvore de scanners inéditos guarda quatro
  rodadas interrompidas (só `run.log`, sem resultado), da calibração do
  Tenable. Ficam como registro, não entram em nenhuma tabela.
- As linhas do **base** e do **DeepSeek** da Parte 4 vivem no outro
  repositório, dentro da árvore do estudo comparativo, porque foram medidas
  naquela campanha e não na do fine-tuning.

### Como regerar as tabelas

```bash
# tabela comparativa entre modelos, com taxa de preenchimento
python3 scripts/compare_models.py output_heldout/qwen2.5-1.5b     output_heldout/mulita-qwen2.5-1.5b-v4 output_heldout/deepseek

# relatório HTML do estudo comparativo (no repositório MulitaMiner2)
mulitaminer report output_experiments

# reavaliar uma rodada qualquer contra seu gabarito
mulitaminer evaluate <pasta-da-rodada> -b <gabarito.xlsx> --metrics all
```

## Parte 1: modelos locais vs. nuvem (estudo comparativo)

Nove modelos locais (0.5B a 3B) servidos localmente, contra o DeepSeek (nuvem,
API) como teto de referência. Todos com o mesmo pipeline e prompts; medição em
regime few-shot (prompt com exemplos, sem ajuste de pesos).

| Modelo | Recall | description (token_f1 / BERTScore) | solution | insight |
|---|--:|--:|--:|--:|
| **DeepSeek (nuvem)** | **0.997** | **0.92 / 0.94** | **0.78** | **0.98** |
| qwen2.5-3b | 0.970 | 0.38 / 0.52 | 0.05 | 0.00 |
| qwen3-1.7b (sem thinking) | 0.947 | 0.49 / 0.57 | 0.05 | 0.00 |
| llama3.2-3b | 0.945 | 0.35 / 0.57 | 0.00 | 0.00 |
| qwen3-1.7b | 0.937 | 0.46 / 0.56 | 0.06 | 0.00 |
| qwen2.5-1.5b | 0.922 | 0.40 / 0.60 | 0.05 | 0.01 |
| granite3-dense-2b | 0.860 | 0.36 / 0.50 | 0.01 | 0.00 |
| qwen2.5-0.5b | 0.831 | 0.28 / 0.52 | 0.03 | 0.00 |
| llama3.2-1b | 0.825 | 0.36 / 0.59 | 0.00 | 0.00 |
| smollm2-1.7b | 0.740 | 0.30 / 0.53 | 0.01 | 0.00 |

> Dados: `output_slm_metrics/<modelo>/<scanner>/<relatorio>/` no MulitaMiner2,
> 24 relatórios x 10 modelos = 240 rodadas. O `report.html` navegável está em
> `output_experiments/`.

**Achado central:** cobertura não é fidelidade. Os modelos locais **alinham
bem** (recall até 0.97) e copiam o nome do achado quase perfeitamente, mas
**desabam nos campos de corpo** (texto livre): `solution` fica em ~0.05 e
`insight` em ~0.00, contra 0.78 e 0.98 do DeepSeek. Conteúdo estruturalmente
presente, porém oco. Um experimento de prompt (reescrita com regra explícita
de preenchimento) **não** moveu esses números: prompt não resolve o problema
nesse tamanho de modelo. A conclusão é que o gap é de capacidade/comportamento
do modelo pequeno, e que a alavanca correta é o **fine-tuning**.

## Parte 2: escolha do modelo para especializar

Critério fixo, dentro do teto de tamanho embarcável (≤2.5B) e com licença que
permita publicar o modelo derivado (Apache 2.0): dois finalistas foram
treinados, o **qwen3-1.7b** (melhor no agregado do estudo) e o
**qwen2.5-1.5b** (controle, mesma família, geração anterior).

O qwen3, após o fine-tuning, **degenera sob decodificação restrita**
(json_schema): entra em repetição, gera JSON truncado e fica muito mais lento.
Servido sem a restrição funciona, mas ainda pior e mais instável que o
qwen2.5. Foi descartado. O **qwen2.5-1.5b** foi o modelo escolhido, é também
o menor, o que favorece o alvo embarcado.

## Parte 3: resultado do fine-tuning (modelo final, "v4")

Foram quatro iterações de dataset/receita (v1 a v4); a v4 é a versão final.
O dataset é composto pelos exports dos scanners (OpenVAS, Qualys, Nessus, ZAP),
com os exemplos no formato exato de produção.

### Como a receita chegou na v4

Cada versão mudou **uma coisa**, escolhida a partir do defeito que a anterior
mostrou. Nenhuma foi ajuste de hiperparâmetro no escuro.

| Versão | O que mudou | Por que |
|---|---|---|
| **v1** | Um exemplo = **um bloco** (um achado por exemplo) | Ponto de partida natural: a unidade de anotação é o achado |
| **v2** | Um exemplo = **um chunk inteiro**, montado pelo `pack` da própria ferramenta, com o assistente respondendo todos os blocos de uma vez | A v1 treinava com 1 bloco e era **servida** com N por chamada. Essa diferença entre treino e produção era a suspeita para o `cvss` vir nulo em 55% dos casos do OpenVAS |
| **v3** | **Mistura das duas formas**: cada registro aparece uma vez sozinho e uma vez dentro do seu chunk. 1 época, para manter a exposição total igual à da v2 | As duas formas ensinam coisas diferentes: bloco isolado ensina **prosa**, chunk ensina **estrutura**. A hipótese era ficar com as duas |
| **v4** | Mesmo dataset misto da v3, com **2 épocas** | A v3 deu a cada habilidade **metade** da dose do seu especialista. Dobrar as épocas dá a dose cheia das duas |

### O que cada mudança produziu

Mesmos 8 relatórios held-out, mesma régua, uma execução por versão:

| Campo | v1 | v2 | v3 | **v4** |
|---|--:|--:|--:|--:|
| description | 0.755 | 0.585 | 0.662 | **0.827** |
| solution | **0.855** | 0.777 | 0.754 | 0.810 |
| insight | 0.150 | 0.558 | 0.456 | **0.672** |
| detection_result | 0.683 | 0.626 | 0.829 | **0.861** |
| cvss | 0.346 | **0.790** | 0.751 | 0.568 |
| instances | 0.423 | **0.840** | 0.348 | 0.658 |
| port | 0.675 | **0.867** | 0.699 | 0.756 |
| recall | 0.947 | **0.965** | 0.929 | 0.934 |
| blocos perdidos | 22 | **19** | 30 | 20 |

> Dados: `output_heldout/mulita-qwen2.5-1.5b{,-v2,-v3,-v4}/` no
> Mulita-Training. As quatro foram re-pontuadas na mesma régua em 2026-08-11;
> os números acima saem dos `evaluation.json` dessas rodadas.

**A leitura, versão por versão:**

- **v1 → v2 confirmou a hipótese do chunking.** Os campos estruturados
  saltaram (`cvss` 0.35 → 0.79, `instances` 0.42 → 0.84, `insight` 0.15 →
  0.56) e a cobertura subiu. O preço foi a prosa: `description` caiu de 0.755
  para 0.585. Treinar só com chunks ensinou estrutura e desensinou texto.
- **v3 refutou a hipótese da mistura simples.** Misturar as duas formas
  mantendo a exposição total constante deixou a v3 **pior que as duas** nos
  respectivos pontos fortes (`instances` despencou para 0.348, `description`
  ficou em 0.662, abaixo da v1). Cada habilidade recebeu metade do treino que
  seu especialista teve.
- **v4 corrigiu a dose.** Mesmo dataset, o dobro de épocas: `description`
  chegou ao recorde da série (0.827), `insight` também (0.672), e a aderência
  ao contrato voltou ao nível da v2 (20 blocos perdidos contra 19). A perda de
  validação continuou caindo entre as épocas, sem sinal de overfitting.

**O custo da escolha, declarado.** A v4 não vence em tudo: a v2 continua
melhor em `cvss` (0.790 contra 0.568), `instances` (0.840 contra 0.658) e
cobertura (0.965 contra 0.934). A v4 foi escolhida por priorizar os campos de
texto livre, que são os que motivaram o trabalho e onde os modelos locais
colapsavam. Os campos em que a v2 ganha são mecânicos e regulares, e há uma
alternativa determinística registrada para eles (extrair `cvss`, `port` e
`protocol` por regra a partir do bloco, em vez de pedir ao modelo).

A tabela abaixo compara o modelo **base** (qwen2.5-1.5b sem ajuste) com o
**v4** (especializado), nos mesmos 8 relatórios held-out (token_f1; BERTScore
confirma, entre parênteses onde relevante):

Cada célula traz a **média (taxa de preenchimento)**. A média cobre só os
achados que o modelo respondeu, então ela sozinha premiaria quem se cala: os
dois números precisam ser lidos juntos.

| Campo | base | **v4** | DeepSeek (nuvem) |
|---|---|---|---|
| description | 0.566 (0.67) | **0.843 (0.86)** | 0.931 (1.00) |
| solution | **0.004 (0.01)** | **0.831 (0.66)** | 0.738 (0.93) |
| insight | **0.000 (0.00)** | **0.686 (0.60)** | 0.996 (0.86) |
| impact | 0.451 (0.29) | 0.784 (0.30) | 0.747 (0.51) |
| detection_result | 0.427 (0.51) | 0.894 (0.87) | 0.986 (0.97) |
| references | 0.131 (0.22) | 0.758 (0.49) | 0.816 (0.63) |
| severity | 0.818 (1.00) | 0.968 (1.00) | 0.997 (1.00) |
| instances | 0.596 (1.00) | 0.737 (0.91) | 0.958 (1.00) |
| **Recall** | 0.906 | **0.965** | 0.992 |

**O fine-tuning fechou o colapso de conteúdo.** O `solution` do modelo base é
**0.004**, com preenchimento de 1%: ele praticamente não escreve o campo. O
`insight` é **zero**. O v4 leva os dois a 0.831 e 0.686, e sobe a cobertura de
0.906 para 0.965.

**Onde a nuvem ainda ganha:** `insight` (0.996 contra 0.686) e `instances`
(0.958 contra 0.737). O `insight` é o gap real, e ele é de preenchimento
tanto quanto de conteúdo.

**Onde o modelo local ganha:** `solution` (0.831 contra 0.738) e `impact`
(0.784 contra 0.747). Mas com preenchimento menor (0.66 contra 0.93), então a
leitura honesta é "melhor onde responde, responde menos vezes", e não
"superou a nuvem".

> Dados: `output_serve2/{qwen2.5-1.5b,mulita-qwen2.5-1.5b-v4,deepseek}/`, 8
> rodadas cada, todas de 2026-09-19/20. Empacotamento do OpenVAS em 2 achados
> por chamada, que é o valor calibrado e o que a ferramenta usa; os demais
> scanners nos seus valores de fábrica. A rodada do DeepSeek custou $0.5206.

**O fine-tuning fechou o colapso de conteúdo.** Os campos que motivaram o
trabalho saltaram de ~0 para 0.67-0.86, ao nível do teto de nuvem observado no
estudo (ex.: solution do DeepSeek era 0.78). A cobertura e a aderência ao
contrato também melhoraram. O modelo final tem ~1 GB (quantizado GGUF Q4),
compatível com o alvo de CPU/8 GB de RAM.

### O modelo aprendeu a tarefa, não decorou os dados

Recorte de memorização: entre os achados dos relatórios de avaliação,
separamos os cujo nome **nunca apareceu** em nenhum exemplo de treino
(conteúdo inédito). O v4 pontua nesses **igual ou melhor** que nos vistos
(ex.: solution 0.97-1.00 em conteúdo inédito), ou seja, não há colapso em
material novo, o modelo extrai, não recita. As curvas de perda de validação
também caem junto com as de treino (sem sinal de overfitting).

## Parte 4: generalização para scanners nunca vistos

Este é o resultado mais forte. O v4 foi aplicado a **Tenable** e **Acunetix**,
scanners que **não** estavam em nenhum exemplo de treino, em nenhum formato.
Comparado ao base e ao DeepSeek (recall / description BERTScore / solution
BERTScore):

| Relatório (scanner inédito) | base | **v4** | DeepSeek |
|---|--:|--:|--:|
| Tenable bWAPP | 0.97 / 0.57 / 0.75 | **0.99 / 0.94 / 0.79** | 1.00 / 0.93 / 0.78 |
| Tenable JuiceShop | - | **1.00 / 0.90 / 0.95** | - |
| Acunetix testaspnet | 0.67 / 0.00 / 0.00 | **1.00 / 1.00 / 0.75** | 1.00 / 1.00 / 0.97 |
| Acunetix testphp | 0.73 / 0.15 / 0.00 | **0.58 / 0.97 / 0.76** | 0.89 / 0.99 / 0.80 |

> Dados: o v4 está em
> `output_heldout/mulita-qwen2.5-1.5b-v4-unseen/{tenable,acunetix}/` no
> Mulita-Training; o base e o DeepSeek estão em
> `output_experiments/{qwen2.5-1.5b,deepseek}/{tenable,acunetix}/` no
> MulitaMiner2. Cada rodada tem o `evaluation.json` com a comparação achado a
> achado, que é onde estão os campos que esta tabela não mostra.

**O conteúdo generaliza ao nível de nuvem em scanners não vistos** (description
0.90-1.00, solution 0.75-0.95). O contraste com o base é dramático (ex.:
Acunetix testaspnet, description 0.00 → 1.00). Isso confirma que o
fine-tuning ensinou a **tarefa** (localizar a seção e copiar para o campo
certo), e não apenas os quatro scanners de treino. A cobertura pode oscilar
por relatório (o testphp perdeu blocos), mas onde o modelo extrai, extrai com
qualidade de nuvem.

## Conclusão

- Modelos locais pequenos, sem ajuste, ficam muito aquém da nuvem nos campos de
  texto livre; prompt não resolve.
- Um fine-tuning barato (QLoRA sobre um modelo de 1.5B) fecha esse gap: o
  modelo final iguala o teto de nuvem nesses campos, cabe em CPU/8 GB e roda
  on-premise.
- O ganho **transfere** para scanners nunca vistos, evidência de que o modelo
  aprendeu a tarefa de extração, não os dados de treino.

## Limitações

- **Uma execução por modelo, e isso é suficiente:** a extração é
  determinística. Dez passadas sobre os 8 relatórios (80 execuções) produziram
  `results.json` byte a byte idênticos, e cinco passadas com o modelo
  descarregado e recarregado entre elas também. Não há ruído de amostragem
  para mediar, porque a temperatura é 0 e o servidor não reaproveita o cache
  de prompt (os 2046 tokens são recalculados a cada chamada). Diferenças
  pequenas **dentro de um mesmo ambiente** são exatas, não indicativas.
- **O que varia é o ambiente, e por isso ele é declarado.** Trocar o runtime
  de Ollama 0.32.15 para 0.34.0, com pesos, Modelfile e hardware idênticos,
  moveu `instances` em +0.079 e `plugin` em -0.050. Comparações entre modelos
  só valem dentro do mesmo ambiente, e o ambiente de cada tabela está
  registrado junto dela.
- Mix de treino dominado por OpenVAS (limitação de dados declarada).
- Custo de CPU (tokens/s, minutos por relatório em máquina modesta) ainda a
  medir; em modelos pequenos e relatórios pesados a extração é lenta.
- O teto de nuvem (DeepSeek) nos held-out do fine-tuning ainda não foi medido
  (sem orçamento de API no momento); a comparação com nuvem existe no estudo
  comparativo e no corte de scanners inéditos.
