# Cartões fixos por campeão — 26/10/2026

Alteração solicitada: reunir a ultimate e os feitiços de cada campeão em um único cartão, exclusivamente no modo **Cartões fixos**. Linha do tempo e Linhas compactas preservam a apresentação anterior.

## Comportamento

- Um retrato do campeão no topo, seguido da ultimate e das duas linhas de feitiços, cada uma com ícone e contagem.
- Sem recarga registrada, a linha mostra **PRONTO** em verde, conforme solicitado. É uma suposição de exibição: não cria timers, não confirma uso nem altera os dados reconhecidos pelo parser.
- A ultimate usa seu ícone oficial mesmo antes de haver uma recarga registrada. Um feitiço ainda não identificado mantém o ícone genérico; sua identidade não é adivinhada.
- Os feitiços seguem uma ordem canônica estável, independente dos segundos restantes. Não há indicação D/F, pois o programa não conhece as teclas do adversário.
- As marcações originais `~` (tempo aproximado) e `?` (reconhecimento incerto) continuam nas contagens observadas.
- Trocas de feitiço que deixem mais de duas recargas de invocador registradas geram linhas adicionais, sem descartar esses timers.
- Ícones maiores e altura mínima adaptada às três linhas; as configurações de escala, fonte, tema, transparência e posição continuam disponíveis. Uma posição salva permanece salva; uma moldura curta demais cresce para caber um cartão inteiro.
- A largura e a altura padrão dos cartões foram ajustadas para a nova organização. Como antes, uma moldura estreita demais pode não comportar todos os cartões; ela pode ser redimensionada.
- Miniatura da escolha de exibição e ilustrações do guia atualizadas somente para esse modo.

Não houve alteração no reconhecimento, captura, detecção de partida, cálculo ou persistência dos timers, travamento, passagem de cliques nem regras de visibilidade nesta revisão. As correções anteriores de `R` e do posicionamento pelo guia estão incluídas na build.

## Arquivos desta revisão

| Arquivo | Alteração |
| --- | --- |
| `src/overlay.py` | Agrupamento e desenho dos cartões, medidas e altura mínima; espaços sem recarga mostram PRONTO sem criar timers |
| `src/ui.py` | Miniatura dos cartões |
| `src/onboarding.py` | Prévia dos cartões e moldura de posicionamento correspondente |
| `src/i18n.py` | Descrição de Cartões fixos em português, inglês e francês |
| `src/settings.py` | Comentário da opção de layout; valores e seleção padrão preservados |
| `tests/test_champion_cards.py` | Testes de agrupamento, PRONTO presumido, preservação dos dados, ordem, medidas, temas, escalas e prévias |
| `tests/test_display_choice.py` | Medidas esperadas dos cartões atualizadas; verificações dos outros modos preservadas |
| `docs/PTBR.md`, `README.md`, `NOTICE-PTBR.md` | Referências à revisão |
| `docs/CARTOES-POR-CAMPEAO.md` | Este relatório |

## Validação

**34/34 suítes passaram**, incluindo 6 testes novos de cartões por campeão. A suíte de desempenho passou em 9/9 verificações: leitura alterada de 16 linhas em 871 ms, dentro do limite original de 900 ms, sem flexibilizar o teste. Tempos variam com a máquina e sua carga.

Logs: `build/champion-cards-tests/`; resumo: `build/champion-cards-tests/results.json`. Comando: `.venv/Scripts/python.exe tools/run_tests.py --out build/champion-cards-tests`.

Os testes usam Qt fora da tela, dados simulados e imagens previamente salvas. Nenhuma partida aberta foi capturada ou controlada; o executável desta revisão não foi aberto, conforme a restrição do usuário.

Prévia real do renderizador, com dados simulados: `build/champion-cards/mundo-dark.png`. Também foram geradas prévias de cinco campeões em áreas equivalentes a 1920×1080 e 2560×1440, nos três temas, além das páginas do guia. Isso não equivale à validação física em um monitor 1440p nem à validação sobre uma partida.

As limitações do OCR brasileiro descritas em `CORRECOES-R-GUIA.md` continuam válidas. Esta alteração reorganiza a apresentação dos timers disponíveis.

## Distribuição

Saída desta revisão: `dist/cartoes-por-campeao/FlashWatch-PTBR.exe`, com runtime Python, Qt e modelos OCR incorporados. As builds anteriores foram preservadas. A licença MIT original e a licença da fonte Mulish permanecem no pacote e acompanham a distribuição.

Inspeção do executável apenas como arquivo, sem executá-lo: `build/package-champion-cards-verification.json`. Comparação com a build anterior para confirmar que os métodos da barra/lista e os módulos de captura, OCR, parser, timers e segurança mantêm o mesmo código compilado.

**45/45 verificações estáticas passaram**, incluindo correspondência dos módulos alterados com as fontes finais, preservação dos métodos dos outros modos, runtime Python, plugin Qt do Windows, três modelos OCR e licenças. Nenhuma captura fornecida pelo usuário foi incorporada ao executável.

Build de 107.701.399 bytes. SHA-256:

```text
c6d9570c76dd3acb3c5b4e3f06858775efcb402e66beb3f3f634665ad6c22a43
```

Comando de build: `.venv/Scripts/python.exe build.py --out dist/cartoes-por-campeao`. A inspeção estática não substitui um teste de abertura do executável; este foi deliberadamente omitido para respeitar o pedido de não testar com o LoL aberto.
